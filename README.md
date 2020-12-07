# tracedump
System service to dump Intel processor trace + memory after a crash.

## INSTALL

Install [processor-trace](https://github.com/intel/libipt), we tested with v2.0. 
Than install [poetry](https://python-poetry.org/docs/) in order to build the project with:

```console
$ poetry install
```

To get a virtual environment with the tracedump python library use:

```
$ poetry shell
```

## USAGE

Get traces from process id
```console
$ sudo tracedumpd --pid 4660
```

Get traces from child process
```console
$ tracedumpd -- bash -c 'kill -11 $$'
```

If the application creates a coredump there will be an archive created in `/var/lib/tracedump`.
This archive can be read by the tracedump decoder library. An example is in `./examples/read_trace.py`:


```console
root> ./examples/read_trace.py /var/lib/tracedump/bash-20201102T131134.tar.gz
# ...
<Instruction[ptic_other] @ 0x7f83652f783b> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f783c> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f783d> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f783f> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f7843> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_cond_jump] @ 0x7f83652f7846> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f7857> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f785c> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f7865> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f786d> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f7872> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_cond_jump] @ 0x7f83652f7874> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f7876> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_other] @ 0x7f83652f7879> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
<Instruction[ptic_far_call] @ 0x7f83652f787e> at 7f836522a000-7f836536e000 r-xp 144000 /run/user/1000/tmp6_g4xyeq/binaries/nix/store/bdf8iipzya03h2amgfncqpclf6bmy3a1-glibc-2.32/lib/libc-2.32.so
```
