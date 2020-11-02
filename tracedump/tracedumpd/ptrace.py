import ctypes as ct

libc = ct.CDLL("libc.so.6", use_errno=True)
PTRACE = libc.ptrace
PTRACE_TRACEME = 0
PTRACE_SETOPTIONS = 16896
PTRACE_CONT = 7
PTRACE_ATTACH = 16
PTRACE_DETACH = 17
PTRACE_O_TRACEEXIT = 0x00000040
PTRACE_O_TRACESYSGOOD = 0x00000001


def ptrace(request: int, pid: int, addr: int, data: int) -> int:
    res = PTRACE(request, pid, addr, data)
    assert res != 1
    return res


def ptrace_me() -> None:
    ptrace(PTRACE_TRACEME, 0, 0, 0)


def ptrace_attach(pid: int) -> None:
    ptrace(PTRACE_ATTACH, pid, 0, 0)


def ptrace_cont(pid: int) -> None:
    ptrace(PTRACE_CONT, pid, 0, 0)

   
def ptrace_detach(pid: int) -> None:
    ptrace(PTRACE_DETACH, pid, 0, 0)


def ptrace_traceexit(pid: int) -> None:
    ptrace(PTRACE_SETOPTIONS, pid, 0, PTRACE_O_TRACESYSGOOD|PTRACE_O_TRACEEXIT)
