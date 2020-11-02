import sys
from typing import Any, List

import argparse
from . import DEFAULT_LOG_DIR, record_command


def parse_arguments(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=argv[0], description="Event-triggered processor trace dumps")
    parser.add_argument(
        "--log-dir",
        default=str(DEFAULT_LOG_DIR),
        type=str,
        help="where to store crash reports",
    )

    parser.add_argument(
        "--pid-file",
        default=str(DEFAULT_LOG_DIR.joinpath("tracedumpd.pid")),
        help="pid file to be created when recording is started",
    )

    parser.add_argument(
        "--limit",
        default=0,
        type=int,
        help="Maximum crashes to record (0 for unlimited crashes)",
    )

    parser.add_argument(
        "args", nargs="*", help="Executable and arguments for perf tracing"
    )

    return parser.parse_args(argv[1:])


def main(argv: List[str] = sys.argv) -> Any:
    args = parse_arguments(argv)
    return record_command(args)


if __name__ == "__main__":
    main()
