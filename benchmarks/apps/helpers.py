import os
import signal
import subprocess
import sys
import json
import tempfile
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Text, DefaultDict, Any, IO, Callable
from collections import defaultdict
from tracedump.tracedumpd import RecordPaths, RecordProcess  # type: ignore

ROOT = Path(__file__).parent.resolve()
NOW = datetime.now().strftime("%Y%m%d-%H%M%S")
HAS_TTY = sys.stderr.isatty()


def color_text(code: int, file: IO[Any] = sys.stdout) -> Callable[[str], None]:
    def wrapper(text: str) -> None:
        if HAS_TTY:
            print(f"\x1b[{code}m{text}\x1b[0m", file=file)
        else:
            print(text, file=file)

    return wrapper


info = color_text(31, file=sys.stderr)


def run(
    cmd: List[str],
    extra_env: Dict[str, str] = {},
    stdout: int = subprocess.PIPE,
    input: Optional[str] = None,
    check: bool = True,
) -> "subprocess.CompletedProcess[Text]":
    env = os.environ.copy()
    env.update(extra_env)
    env_string = []
    for k, v in extra_env.items():
        env_string.append(f"{k}={v}")
    print(f"$ {' '.join(env_string)} {' '.join(cmd)}")
    return subprocess.run(
        cmd, cwd=ROOT, stdout=stdout, check=check, env=env, text=True, input=input
    )


def read_stats(path: str) -> DefaultDict[str, List]:
    stats: DefaultDict[str, List] = defaultdict(list)
    if not os.path.exists(path):
        return stats
    with open(path) as f:
        raw_stats = json.load(f)
        for key, value in raw_stats.items():
            stats[key] = value
    return stats


def trace_with_pt(pid: int, path: Path) -> RecordProcess:
    return RecordProcess(pid, RecordPaths(path, path, None))


def write_stats(path: str, stats: DefaultDict[str, List]) -> None:
    with open(path, "w") as f:
        json.dump(stats, f)


class Chdir(object):
    def __init__(self, path: str) -> None:
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self) -> None:
        os.chdir(self.new_dir)

    def __exit__(self, *args: Any) -> None:
        os.chdir(self.old_dir)


@contextmanager
def spawn(
    *args: str, extra_env: Dict[str, str] = {}, cwd: str = str(ROOT)
) -> Iterator[subprocess.Popen]:
    env = os.environ.copy()

    env.update(extra_env)
    env_string = []
    for k, v in extra_env.items():
        env_string.append(f"{k}={v}")

    print(f"$ {' '.join(env_string)} {' '.join(args)}&")
    proc = subprocess.Popen(args, cwd=cwd, env=env)

    try:
        yield proc
    finally:
        print(f"terminate {args[0]}")
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.send_signal(signal.SIGKILL)
            proc.wait()


@dataclass
class RemoteCommand:
    nix_path: str
    ssh_host: str

    def __post_init__(self) -> None:
        run(["nix", "copy", self.nix_path, "--to", f"ssh://{self.ssh_host}"])

    def run(
        self, exe: str, args: List[str], extra_env: Dict[str, str] = {}
    ) -> subprocess.CompletedProcess:

        cmd = ["ssh", self.ssh_host, "--", "env"]
        for k, v in extra_env.items():
            cmd.append(f"{k}={v}")
        cmd.append(os.path.join(self.nix_path, exe))
        cmd += args
        return run(cmd)


@dataclass(frozen=True)
class Settings:
    remote_ssh_host: str
    remote_dpdk_ip: str
    remote_dpdk_ip6: str
    local_dpdk_ip: str
    local_dpdk_gw: str
    local_dpdk_ip6: str
    dpdk_netmask: int
    dpdk_netmask6: int
    nvme_pci_id: str

    @property
    def cidr(self) -> str:
        return f"{self.local_dpdk_ip}/{self.dpdk_netmask}"

    @property
    def remote_cidr(self) -> str:
        return f"{self.remote_dpdk_ip}/{self.dpdk_netmask}"

    @property
    def cidr6(self) -> str:
        return f"{self.local_dpdk_ip6}/{self.dpdk_netmask6}"

    @property
    def remote_cidr6(self) -> str:
        return f"{self.remote_dpdk_ip6}/{self.dpdk_netmask6}"

    def remote_command(self, nix_attr: str) -> RemoteCommand:
        return RemoteCommand(nix_attr, self.remote_ssh_host)

    def spdk_device(self) -> str:
        for device in os.listdir("/sys/block"):
            path = Path(f"/sys/block/{device}").resolve()
            if not str(path).startswith("/sys/devices/pci"):
                continue
            pci_id = path.parents[2].name
            if pci_id == self.nvme_pci_id:
                return device
        raise Exception(f"No block device with PCI ID {self.nvme_pci_id} found")


def nix_build(attr: str) -> str:
    return run(["nix-build", "-A", attr, "--out-link", attr]).stdout.strip()


def create_settings() -> Settings:
    remote_ssh_host = os.environ.get("REMOTE_SSH_HOST", None)
    if not remote_ssh_host:
        print("REMOTE_SSH_HOST not set", file=sys.stderr)
        sys.exit(1)

    remote_dpdk_ip = os.environ.get("REMOTE_DPDK_IP4", "10.0.42.2")
    if not remote_dpdk_ip:
        print("REMOTE_DPDK_IP4 not set", file=sys.stderr)
        sys.exit(1)

    remote_dpdk_ip6 = os.environ.get("REMOTE_DPDK_IP6", "fdbf:9188:5fbd:a895::1")
    if not remote_dpdk_ip:
        print("REMOTE_DPDK_IP6 not set", file=sys.stderr)
        sys.exit(1)

    nvme_pci_id = os.environ.get("NVME_PCI_ID")
    if not nvme_pci_id:
        print("NVME_PCI_ID not set", file=sys.stderr)
        sys.exit(1)

    return Settings(
        remote_ssh_host=remote_ssh_host,
        remote_dpdk_ip=remote_dpdk_ip,
        remote_dpdk_ip6=remote_dpdk_ip6,
        local_dpdk_ip=os.environ.get("SGXLKL_DPDK_IP4", "10.0.42.1"),
        local_dpdk_gw=os.environ.get("SGXLKL_DPDK_GW4", "10.0.42.254"),
        local_dpdk_ip6=os.environ.get("SGXLKL_DPDK_IP6", "fdbf:9188:5fbd:a895::1"),
        dpdk_netmask=int(os.environ.get("DEFAULT_DPDK_IPV4_MASK", "24")),
        dpdk_netmask6=int(os.environ.get("DEFAULT_DPDK_IPV6_MASK", "64")),
        nvme_pci_id=nvme_pci_id,
    )
