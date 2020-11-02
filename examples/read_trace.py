#!/usr/bin/env python3

import sys
import tempfile
import tracedump


def main() -> None:
    if len(sys.argv) < 2:
        print("USAGE: report")
        sys.exit(1)
    report = sys.argv[1]

    with tempfile.TemporaryDirectory() as unpack_dir:
        trace = tracedump.load_trace(report, unpack_dir)
        loader = trace.loader

        for instruction in trace.instructions:
            print(f"{instruction} at {loader.find_mapping(instruction.ip)}")


if __name__ == "__main__":
    main()
