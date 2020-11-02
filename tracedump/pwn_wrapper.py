import os

# stop pwnlib from doing fancy things
os.environ["PWNLIB_NOTERM"] = "1"
from pwnlib.elf.corefile import Coredump, Mapping  # noqa: E402
from pwnlib.elf.elf import ELF  # noqa: E402
