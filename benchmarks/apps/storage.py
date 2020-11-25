import getpass
import os
import time
from enum import Enum
from typing import Any, Optional, Dict
from pathlib import Path
import subprocess

from helpers import ROOT, Settings, nix_build, run

# Use a fixed path here so that we can unmount previous failed runs
MOUNTPOINT = ROOT.joinpath("iotest-mnt")


class Mount:
    def __init__(self, dev: str) -> None:
        self.dev = dev
        self.mountpoint = MOUNTPOINT

    def mount(self) -> None:
        MOUNTPOINT.mkdir(exist_ok=True)
        run(["sudo", "mount", self.dev, str(MOUNTPOINT)])
        run(["sudo", "chown", "-R", getpass.getuser(), str(MOUNTPOINT)])

    def umount(self) -> None:
        for i in range(3):
            try:
                run(["sudo", "umount", str(MOUNTPOINT)])
            except subprocess.CalledProcessError:
                print(f"unmount {MOUNTPOINT} failed; retry in 1s")
                time.sleep(1)
            break

    def __enter__(self) -> str:
        self.mount()

        return str(self.mountpoint)

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        self.umount()


class Storage:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def setup(self) -> Mount:
        image = nix_build("iotest-image")

        if MOUNTPOINT.is_mount():
            run(["sudo", "umount", str(MOUNTPOINT)])

        spdk_device = self.settings.spdk_device()
        time.sleep(2)  # wait for device to appear

        dev = f"/dev/{spdk_device}"

        # TRIM for optimal performance
        run(["sudo", "blkdiscard", "-f", dev])
        run(
            [
                "sudo",
                "dd",
                f"if={image}",
                f"of={dev}",
                "bs=128M",
                "conv=fdatasync",
                "oflag=direct",
                "status=progress",
            ]
        )
        run(["sudo", "resize2fs", dev])

        return Mount(dev)
