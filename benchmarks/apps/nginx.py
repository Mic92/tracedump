import time
import subprocess
from typing import Dict, List
import os
from pathlib import Path

import pandas as pd

from helpers import (
    NOW,
    Settings,
    create_settings,
    nix_build,
    read_stats,
    write_stats,
    spawn,
    trace_with_pt,
)
from storage import Storage
from process_wrk import parse_wrk_output


def process_wrk_output(
    wrk_out: str, system: str, stats: Dict[str, List[str]], connections: int
) -> None:
    wrk_metrics = parse_wrk_output(wrk_out)
    stats["system"].append(system)
    stats["connections"].append(str(connections))
    for k, v in wrk_metrics.items():
        stats[k].append(v)


class Benchmark:
    def __init__(self, settings: Settings, storage: Storage) -> None:
        self.settings = create_settings()
        self.storage = storage
        self.remote_nc = settings.remote_command(nix_build("netcat-native"))
        self.remote_wrk = settings.remote_command(nix_build("wrk-bench"))

    def run_wrk(
        self, proc: subprocess.Popen, system: str, stats: Dict[str, List]
    ) -> None:
        host = self.settings.local_dpdk_ip
        while True:
            try:
                self.remote_nc.run(
                    "bin/nc", ["-z", self.settings.local_dpdk_ip, "9000"]
                )
                break
            except subprocess.CalledProcessError:
                status = proc.poll()
            if status is not None:
                raise OSError(f"nginx exiteded with {status}")
                time.sleep(1)
            pass

        wrk_connections = 100
        wrk_proc = self.remote_wrk.run(
            "bin/wrk",
            [
                "-t",
                "16",
                "-c",
                f"{wrk_connections}",
                "-d",
                "30s",
                f"https://{host}:9000/test/file",
            ],
        )
        process_wrk_output(wrk_proc.stdout, system, stats, wrk_connections)

    def run(
        self,
        attr: str,
        system: str,
        mnt: str,
        stats: Dict[str, List],
        trace: bool = False,
    ) -> None:
        nginx_server = nix_build(attr)
        with spawn(
            nginx_server, "bin/nginx", "-c", f"{mnt}/nginx/nginx.conf", cwd=mnt
        ) as proc:
            if trace:
                record = trace_with_pt(proc.pid, Path(mnt))
            try:
                self.run_wrk(proc, system, stats)
            finally:
                if trace:
                    record.result()


def benchmark_nginx_normal(benchmark: Benchmark, stats: Dict[str, List]) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("nginx-native", "native", mnt, stats)


def benchmark_nginx_trace(benchmark: Benchmark, stats: Dict[str, List]) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("nginx-native", "native", mnt, stats, trace=True)


def main() -> None:
    stats = read_stats("nginx.json")
    settings = create_settings()
    storage = Storage(settings)

    benchmark = Benchmark(settings, storage)

    benchmarks = {
        "normal": benchmark_nginx_normal,
        "trace": benchmark_nginx_trace,
    }

    system = set(stats["system"])
    for name, benchmark_func in benchmarks.items():
        if name in system:
            print(f"skip {name} benchmark")
            continue
        benchmark_func(benchmark, stats)
        write_stats("nginx.json", stats)

    csv = f"nginx-{NOW}.tsv"
    print(csv)
    throughput_df = pd.DataFrame(stats)
    throughput_df.to_csv(csv, index=False, sep="\t")
    throughput_df.to_csv("nginx-latest.tsv", index=False, sep="\t")


if __name__ == "__main__":
    main()
