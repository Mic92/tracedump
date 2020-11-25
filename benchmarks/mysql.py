import re
import os
import subprocess
from functools import lru_cache
from typing import Dict, List
from pathlib import Path

import pandas as pd
from helpers import (
    NOW,
    RemoteCommand,
    Settings,
    create_settings,
    nix_build,
    spawn,
    read_stats,
    write_stats,
    trace_with_pt,
)
from storage import Storage


@lru_cache(maxsize=1)
def sysbench_command(settings: Settings) -> RemoteCommand:
    path = nix_build("sysbench")
    return settings.remote_command(path)


@lru_cache(maxsize=1)
def nc_command(settings: Settings) -> RemoteCommand:
    path = nix_build("netcat-native")
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
            "--mysql-ssl=on",
            "--table-size=500000",
            f"{sysbench.nix_path}/share/sysbench/oltp_read_write.lua",
        ]

        while True:
            try:
                proc = nc_command(self.settings).run(
                    "bin/nc", ["-z", "-v", self.settings.local_dpdk_ip, "3306"]
                )
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
        attr: str,
        system: str,
        mnt: str,
        stats: Dict[str, List],
        extra_env: Dict[str, str] = {},
        trace: bool = False,
    ) -> None:
        mysql = nix_build(attr)

        with spawn(
            mysql,
            "bin/mysqld",
            f"--datadir={mnt}/var/lib/mysql",
            "--socket=/tmp/mysql.sock",
            cwd=mnt,
        ) as proc:
            if trace:
                record = trace_with_pt(proc.pid, Path(mnt))
            try:
                self.run_sysbench(system, stats)
            finally:
                if trace:
                    record.result()


def benchmark_normal(benchmark: Benchmark, stats: Dict[str, List]) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("mysql-native", "native", mnt, stats)


def benchmark_trace(benchmark: Benchmark, stats: Dict[str, List]) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("mysql-native", "native", mnt, stats, trace=True)


def main() -> None:
    stats = read_stats("mysql.json")

    settings = create_settings()
    storage = Storage(settings)
    benchmark = Benchmark(settings, storage)

    benchmarks = {
        "normal": benchmark_normal,
        "trace": benchmark_trace,
    }

    system = set(stats["system"])
    for name, benchmark_func in benchmarks.items():
        if name in system:
            print(f"skip {name} benchmark")
            continue
        benchmark_func(benchmark, stats)
        write_stats("mysql.json", stats)

    csv = f"mysql-{NOW}.tsv"
    print(csv)
    throughput_df = pd.DataFrame(stats)
    throughput_df.to_csv(csv, index=False, sep="\t")
    throughput_df.to_csv("mysql-latest.tsv", index=False, sep="\t")


if __name__ == "__main__":
    main()
