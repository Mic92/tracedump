import os
import subprocess
import signal
from typing import Dict, List, Any, Tuple, Optional, IO
from pathlib import Path
from threading import Thread
import re
import time

import pandas as pd
from helpers import (
    NOW,
    create_settings,
    nix_build,
    read_stats,
    write_stats,
)
from tracedump.tracedumpd import record
from storage import Storage


class StdoutPipe:
    def __init__(self) -> None:
        self.read_file: Optional[IO[str]] = None
        self.write_file: Optional[IO[str]] = None
        self.output: Optional[str] = None
        self.thread: Optional[Thread] = None

    def _read_pipe(self) -> None:
        if self.read_file:
            self.output = self.read_file.read()
            self.read_file.close()

    def __enter__(self) -> Optional[IO[str]]:
        read_fd, write_fd = os.pipe()
        self.read_file = os.fdopen(read_fd)
        self.write_file = os.fdopen(write_fd, mode="w")
        self.thread = Thread(target=self._read_pipe)
        self.thread.start()
        return self.write_file

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.thread:
            self.thread.join()
        if self.read_file:
            self.read_file.close()
        if self.write_file:
            self.write_file.close()


def trace_run(cmd: List[str], cwd: str = ".") -> str:
    pipe = StdoutPipe()
    with pipe as stdout:
        record(
            record_path=Path(cwd),
            log_path=Path(cwd),
            target=cmd,
            working_directory=Path(cwd),
            stdout=stdout,
        )
        stdout.close()
    assert pipe.output is not None
    return pipe.output


def benchmark_sqlite(
    system: str,
    directory: str,
    stats: Dict[str, List[Any]],
    extra_env: Dict[str, str] = {},
    trace: bool = False,
) -> None:
    sqlite = nix_build("sqlite-speedtest")
    cmd = [f"{sqlite}/bin/speedtest1"]
    print(f"[Benchmark]:{system}")

    if trace:
        output = trace_run(cmd, cwd=directory)
    else:
        proc = subprocess.run(
            cmd, cwd=directory, stdout=subprocess.PIPE, check=True, text=True
        )
        assert proc.stdout
        output = proc.stdout

    n_rows = 0
    print(output)
    for line in output.split("\n"):
        line = line.rstrip()
        print(line)
        match = re.match(r"(?: \d+ - |\s+)([^.]+)[.]+\s+([0-9.]+)s", line)
        if match:
            if "TOTAL" in match.group(1):
                continue
            stats["system"].append(system)
            stats["sqlite-op-type"].append(match.group(1))
            stats["sqlite-time [s]"].append(match.group(2))
            n_rows += 1

    expected = 3
    if n_rows < expected:
        raise RuntimeError(
            f"Expected {expected} rows, got: {n_rows} when running benchmark for {system}"
        )


def benchmark_sqlite_normal(storage: Storage, stats: Dict[str, List[Any]]) -> None:
    with storage.setup() as mnt:
        benchmark_sqlite("normal", mnt, stats)


def benchmark_sqlite_trace(storage: Storage, stats: Dict[str, List[Any]]) -> None:
    with storage.setup() as mnt:
        benchmark_sqlite("trace", mnt, stats, trace=True)


def main() -> None:
    stats = read_stats("sqlite.json")
    settings = create_settings()
    storage = Storage(settings)

    benchmarks = {
        "normal": benchmark_sqlite_normal,
        "trace": benchmark_sqlite_trace,
    }
    system = set(stats["system"])
    for name, benchmark in benchmarks.items():
        if name in system:
            print(f"skip {name} benchmark")
            continue
        benchmark(storage, stats)
        write_stats("sqlite.json", stats)

    csv = f"sqlite-speedtest-{NOW}.tsv"
    print(csv)
    df = pd.DataFrame(stats)
    df.to_csv(csv, index=False, sep="\t")
    df.to_csv("sqlite-speedtest-latest.tsv", index=False, sep="\t")


if __name__ == "__main__":
    main()
