#!/usr/bin/env python3

from .loader import Loader
from .pt import Instruction, InstructionClass, decode
from typing import Any, Dict, List, Tuple


def decode_trace(manifest: Dict[str, Any], loader: Loader) -> List[Instruction]:
    coredump = manifest["coredump"]
    trace = manifest["trace"]

    trace_paths = []
    perf_event_paths = []
    start_thread_ids = []
    start_times = []

    pid = coredump["global_pid"]
    tid = coredump["global_tid"]

    for cpu in trace["cpus"]:
        assert pid == cpu["start_pid"], "only one pid is allowed at the moment"
        trace_paths.append(cpu["trace_path"])
        perf_event_paths.append(cpu["event_path"])
        start_thread_ids.append(cpu["start_tid"])
        start_times.append(cpu["start_time"])

    return decode(
        trace_paths=trace_paths,
        perf_event_paths=perf_event_paths,
        start_thread_ids=start_thread_ids,
        start_times=start_times,
        loader=loader,
        pid=pid,
        tid=tid,
        cpu_family=trace["cpu_family"],
        cpu_model=trace["cpu_model"],
        cpu_stepping=trace["cpu_stepping"],
        cpuid_0x15_eax=trace["cpuid_0x15_eax"],
        cpuid_0x15_ebx=trace["cpuid_0x15_ebx"],
        time_zero=trace["time_zero"],
        time_shift=trace["time_shift"],
        time_mult=trace["time_mult"],
        sample_type=trace["sample_type"],
    )
