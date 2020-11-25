import subprocess
import json
from pathlib import Path
from typing import Any, Dict, List, Union
from .pt import Instruction
from .loader import Loader
from .trace import decode_trace
from .pwn_wrapper import Coredump


def unpack(report: Union[str, Path], archive_root: Union[str, Path]) -> Dict[str, Any]:
    report = Path(report)
    archive_root = Path(archive_root)
    subprocess.check_call(["tar", "-xzf", str(report), "-C", str(archive_root)])

    manifest_path = archive_root.joinpath("manifest.json")
    with open(str(manifest_path)) as f:
        manifest = json.load(f)

    for cpu in manifest["trace"]["cpus"]:
        cpu["event_path"] = str(archive_root.joinpath(cpu["event_path"]))
        cpu["trace_path"] = str(archive_root.joinpath(cpu["trace_path"]))

    coredump = manifest["coredump"]
    coredump["executable"] = str(archive_root.joinpath(coredump["executable"]))
    coredump["file"] = str(archive_root.joinpath(coredump["file"]))

    return manifest


class Trace():
    def __init__(self, loader: Loader, instructions: List[Instruction]) -> None:
        self.instructions = instructions
        self.loader = loader


def load_trace(report: Union[str, Path], archive_root: Union[str, Path]) -> Trace:
    report = Path(report)
    archive_root = Path(archive_root)

    manifest = unpack(report, archive_root)

    coredump = Coredump(manifest["coredump"]["file"])
    vdso_x64 = archive_root.joinpath("vdso")

    with open(str(vdso_x64), "wb+") as f:
        f.write(coredump.vdso.data)
    sysroot = archive_root.joinpath("binaries")
    executable = manifest["coredump"]["executable"]
    loader = Loader(executable, coredump.mappings, sysroot, vdso_x64)
    return Trace(loader, decode_trace(manifest, loader))
