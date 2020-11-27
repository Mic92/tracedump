import subprocess
import time
import pandas as pd
import os
from typing import Dict, List, DefaultDict
from pathlib import Path

from helpers import (
    Settings,
    create_settings,
    nix_build,
    spawn,
    read_stats,
    write_stats,
    NOW,
    trace_with_pt,
)
from storage import Storage


def process_ycsb_out(ycsb_out: str, system: str, results: Dict[str, List]) -> None:
    for line in ycsb_out.split("\n"):
        print(line)
        if line == "":
            break
        operation, metric, value = line.split(",")
        results["system"].append(system)
        results["operation"].append(operation.strip())
        results["metric"].append(metric.strip())
        results["value"].append(value.strip())


class Benchmark:
    def __init__(
        self,
        settings: Settings,
        storage: Storage,
        record_count: int,
        operation_count: int,
    ) -> None:
        self.settings = settings
        self.storage = storage
        self.nc_command = settings.remote_command(nix_build("netcat"))
        self.remote_ycsb = settings.remote_command(nix_build("ycsb"))
        self.record_count = record_count
        self.operation_count = operation_count

    def run_ycsb(
        self, proc: subprocess.Popen, system: str, stats: Dict[str, List],
    ) -> None:
        print(f"waiting for redis for {system} benchmark...", end="")
        while True:
            try:
                self.nc_command.run(
                    "bin/nc", ["-z", "-v", self.settings.local_dpdk_ip, "6379"]
                )
                break
            except subprocess.CalledProcessError:
                status = proc.poll()
                if status is not None:
                    raise OSError(f"redis-server exiteded with {status}")
                time.sleep(1)
                pass

        load_proc = self.remote_ycsb.run(
            "bin/ycsb",
            [
                "load",
                "redis",
                "-s",
                "-P", f"{self.remote_ycsb.nix_path}/share/ycsb/workloads/workloada",
                "-p", f"redis.host={self.settings.local_dpdk_ip}",
                "-p", "redis.port=6379",
                "-p", "redis.timeout=600000",
                "-p", f"recordcount={self.record_count}",
                "-p", f"operationcount={self.operation_count}",
                "-p", "redis.password=snakeoil",
            ],
        )

        run_proc = self.remote_ycsb.run(
            "bin/ycsb",
            [
                "run",
                "redis",
                "-s",
                "-P", f"{self.remote_ycsb.nix_path}/share/ycsb/workloads/workloada",
                "-threads", "16",
                "-p", f"redis.host={self.settings.local_dpdk_ip}",
                "-p", "redis.port=6379",
                "-p", "redis.timeout=600000",
                "-p", f"recordcount={self.record_count}",
                "-p", f"operationcount={self.operation_count}",
                "-p", "redis.password=snakeoil",
            ],
        )
        process_ycsb_out(run_proc.stdout, system, stats)

    def run(
        self, system: str, db_dir: str, stats: Dict[str, List], trace: bool = False
    ) -> None:
        args = [
            "--dir",
            db_dir,
            "--requirepass",
            "snakeoil"
        ]
        redis_server = nix_build("redis")
        with spawn(f"{redis_server}/bin/redis-server", *args) as proc:
            if trace:
                record = trace_with_pt(proc.pid, Path(db_dir))
            try:
                self.run_ycsb(proc, system, stats)
            finally:
                if trace:
                    record.result()


def benchmark_redis_normal(benchmark: Benchmark, stats: Dict[str, List],) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("normal", mnt, stats)


def benchmark_redis_trace(benchmark: Benchmark, stats: Dict[str, List],) -> None:
    with benchmark.storage.setup() as mnt:
        benchmark.run("trace", mnt, stats, trace=True)


def main() -> None:
    stats = read_stats("redis.json")
    settings = create_settings()
    storage = Storage(settings)
    record_count = 100000
    op_count = 10000

    benchmark = Benchmark(settings, storage, record_count, op_count)

    benchmarks = {
        "normal": benchmark_redis_normal,
        "trace": benchmark_redis_trace,
    }

    system = set(stats["system"])
    for name, benchmark_func in benchmarks.items():
        if name in system:
            print(f"skip {name} benchmark")
            continue
        benchmark_func(benchmark, stats)
        write_stats("redis.json", stats)

    csv = f"redis-{NOW}.tsv"
    print(csv)
    throughput_df = pd.DataFrame(stats)
    throughput_df.to_csv(csv, index=False, sep="\t")
    throughput_df.to_csv("redis-latest.tsv", index=False, sep="\t")


if __name__ == "__main__":
    main()
