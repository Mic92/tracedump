import re
import os
import time
import subprocess
from functools import lru_cache
from typing import Dict, List
from pathlib import Path
from collections import defaultdict
from enum import Enum, auto

import pandas as pd
from helpers import (
    NOW,
    RemoteCommand,
    Settings,
    create_settings,
    nix_build,
    spawn,
    read_stats,
    trace_with_pt,
)
from storage import Storage


@lru_cache(maxsize=1)
def sysbench_command(settings: Settings) -> RemoteCommand:
    path = nix_build("sysbench")
    return settings.remote_command(path)


@lru_cache(maxsize=1)
def nc_command(settings: Settings) -> RemoteCommand:
    path = nix_build("netcat")
    return settings.remote_command(path)


def parse_sysbench(output: str) -> Dict[str, str]:
    stats_found = False
    section = ""
    data = {}
    for line in output.split("\n"):
        print(line)
        if line.startswith("SQL statistics"):
            stats_found = True
        if stats_found:
            col = line.split(":")
            if len(col) != 2:
                continue
            name = col[0].strip()
            # remove trailing statistics, e.g.:
            # transform
            #     transactions:                        3228   (322.42 per sec.)
            # to
            #     transactions:                        3228
            value = re.sub(r"\([^)]+\)$", "", col[1]).strip()
            if value == "" and name != "queries performed":
                section = name
                continue
            data[f"{section} {name}"] = value
    return data


def process_sysbench(output: str, system: str, stats: Dict[str, List]) -> None:
    data = parse_sysbench(output)

    for k, v in data.items():
        stats[k].append(v)
    stats["system"].append(system)


class Mode(Enum):
    NORMAL = auto()
    TRACE = auto()
    PERF = auto()


class Benchmark:
    def __init__(self, settings: Settings, storage: Storage) -> None:
        self.settings = settings
        self.storage = storage

    def run_sysbench(self, system: str, stats: Dict[str, List]) -> None:
        sysbench = sysbench_command(self.settings)
        common_flags = [
            f"--mysql-host={self.settings.local_dpdk_ip}",
            "--mysql-db=root",
            "--mysql-user=root",
            "--mysql-password=root",
            "--table-size=5000000",
            "--time=60",
            f"{sysbench.nix_path}/share/sysbench/oltp_read_write.lua",
        ]
        while True:
            try:
                proc = nc_command(self.settings).run(
                    "bin/nc", ["-z", "-v", self.settings.local_dpdk_ip, "3306"]
                )
                time.sleep(1)
                break
            except subprocess.CalledProcessError:
                print(".")
                pass

        sysbench.run("bin/sysbench", common_flags + ["prepare"])
        proc = sysbench.run("bin/sysbench", common_flags + ["run"])
        process_sysbench(proc.stdout, system, stats)
        sysbench.run("bin/sysbench", common_flags + ["cleanup"])

    def run(
        self,
        system: str,
        mnt: str,
        stats: Dict[str, List],
        extra_env: Dict[str, str] = {},
        mode: Mode = Mode.NORMAL,
    ) -> None:
        mysql = nix_build("mysql")

        command = []
        if mode == Mode.PERF:
            command = [
                "perf", "record", "-e", "intel_pt/cyc=1/u", "--"
            ]

        command += [
            f"{mysql}/bin/mysqld",
            f"--datadir={mnt}/var/lib/mysql",
            "--socket=/tmp/mysql.sock",
        ]
        if os.geteuid() == 0:
            command += ["--user=nobody"]
            subprocess.run(["chown", "-R", "nobody", f"{mnt}/var/lib/mysql"])

        with spawn(*command, cwd=mnt) as proc:
            if mode == Mode.TRACE:
                record = trace_with_pt(proc.pid, Path(mnt))
            try:
                self.run_sysbench(system, stats)
            finally:
                if mode == Mode.TRACE:
                    record.result()


def benchmark_normal(benchmark: Benchmark, stats: Dict[str, List]) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("normal", mnt, stats)
        stats["trace_size"].append(0)


def benchmark_trace(benchmark: Benchmark, stats: Dict[str, List]) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("trace", mnt, stats, mode=Mode.TRACE)
        stats["trace_size"].append(0)


def benchmark_perf(benchmark: Benchmark, stats: Dict[str, List]) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("perf", mnt, stats, mode=Mode.PERF)
        perf_data = os.path.join(mnt, "perf.data")
        stats["trace_size"].append(os.path.getsize(perf_data))


def main() -> None:
    enable_perf = os.environ.get("ENABLE_PERF") is not None
    suffix = "-perf" if enable_perf else ""
    stats = read_stats(f"mysql{suffix}.json")

    settings = create_settings()
    storage = Storage(settings)
    benchmark = Benchmark(settings, storage)

    benchmarks = {
        "normal": benchmark_normal,
        "trace": benchmark_trace,
        "perf": benchmark_perf,
    }

    for name, benchmark_func in benchmarks.items():
        while stats.runs[name] < 5:
            benchmark_func(benchmark, stats.data)
            stats.checkpoint(name)

    stats.to_tsv(f"mysql{suffix}-latest.tsv")


if __name__ == "__main__":
    main()
