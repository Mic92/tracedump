#!/usr/bin/env python3
import subprocess
import re
import os
import json
import shlex
from pathlib import Path
from typing import List, Dict, Optional
import tempfile
import multiprocessing
from dataclasses import dataclass

ROOT = Path(os.path.dirname(os.path.realpath(__file__)))
CPU_COUNT = multiprocessing.cpu_count()
PLATFORM = "amd64-linux.gcc"
parsecmgmt = ROOT.joinpath("bin/parsecmgmt")


@dataclass
class Command:
    args: str
    env: Dict[str, str]
    input_archive: Optional[Path]

    def _unpack(self, cwd: str, input_via_stdin: bool) -> Optional[str]:
        if self.input_archive is None:
            return None
        unpack_cmd = ["tar", "-C", cwd, "-vxf", str(self.input_archive)]
        print(f"$ {' '.join(unpack_cmd)}")
        subprocess.run(unpack_cmd, check=True)
        input: Optional[str] = None
        if input_via_stdin:
            with open(Path(cwd).joinpath("input.template")) as f:
                input = f.read()
                return input.replace("NUMPROCS", str(CPU_COUNT))
        return None


    def run(
        self, interpreter: List[str] = [], simulate: bool = False, cwd: str = "."
    ) -> None:
        input = None
        cmd = interpreter
        cmd += shlex.split(self.args)
        input_via_stdin = False
        if cmd[-2] == "<":
            input_via_stdin = True
            cmd.pop()
            cmd.pop()
        input = self._unpack(cwd, input_via_stdin)
        print(f"$ cd {cwd}")
        print(f"$ LD_LIBRARY_PATH={self.env['LD_LIBRARY_PATH']} {' '.join(cmd)}" + (" << EOF" if input_via_stdin else ""))
        if input:
            print(input)
            print("EOF")
        if simulate:
            return
        subprocess.run(cmd, env=self.env, check=True, cwd=cwd, input=input)


@dataclass
class App:
    name: str
    framework: str

    def root_path(self) -> Path:
        if self.framework == "parsec":
            return ROOT.joinpath("pkgs", "apps", self.name)
        elif self.framework == "splash2" or self.framework == "splash2x":
            return ROOT.joinpath("ext", self.framework, "apps", self.name)
        raise Exception(f"unknown framework {self.framework}")

    def source_env(self, path: Path) -> Dict[str, str]:
        wrapper = str(path.joinpath("inst", PLATFORM, "bin", "run.sh"))
        script = f"""
            export NTHREADS={CPU_COUNT}
            export NUMPROCS={CPU_COUNT}
            export INPUTSIZE=native
            export PARSECPLAT={PLATFORM}
            export PARSECDIR={ROOT}
            export LD_LIBRARY_PATH="$PARSECDIR/pkgs/libs/hooks/inst/$PARSECPLAT/lib:$LD_LIBRARY_PATH"
            source {path.joinpath('parsec', 'native.runconf')}
            # mock eval
            eval(){{
              :
            }}
            if [ -f {wrapper} ]; then
              source {wrapper};
            fi
            export run_exec run_args RUN
            echo __EXPORT_START__
            jq -n env
        """
        proc = subprocess.run(
            ["bash", "-c", script], text=True, stdout=subprocess.PIPE, check=True
        )
        assert proc.stdout is not None

        env_str = ""
        export_starts = False
        for line in proc.stdout.split("\n"):
            if line == "__EXPORT_START__":
                export_starts = True
                continue

            if export_starts:
                env_str += line
        assert env_str != ""
        return json.loads(env_str)

    def command(self) -> Command:
        path = self.root_path()
        env = self.source_env(path)
        assert "run_exec" in env
        assert "run_args" in env
        inputs_dir = path.joinpath("inputs")
        input_archive: Optional[Path] = None
        if inputs_dir.exists():
            size = "test" if self.framework == "splash2" else "native"
            input_archive = inputs_dir.joinpath(f"input_{size}.tar")
        if self.framework != "parsec":
            executable = env["RUN"]
            return Command(args=executable, env=env, input_archive=input_archive)
        executable = str(path.joinpath("inst", PLATFORM, env["run_exec"]))
        return Command(
            args=executable + " " + env["run_args"],
            input_archive=input_archive,
            env=env,
        )


def get_apps() -> List[App]:
    apps = []
    proc = subprocess.run(
        [parsecmgmt, "-a", "status", "-p", "apps"],
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    assert proc.stdout is not None
    for line in proc.stdout.split("\n"):
        match = re.match(r"\[PARSEC\] (splash2|splash2x|parsec|)\.([^ ]+)", line)
        if not match:
            continue
        framework = match.group(1)
        name = match.group(2)
        apps.append(App(name, framework))
    return apps


def main() -> None:
    simulate = False
    benchmarks = {}
    if os.path.exists("benchmarks.json"):
        with open("benchmarks.json") as f:
            benchmarks = json.load(f)

    for app in get_apps():
        cmd = app.command()
        if app.name in benchmarks:
            print(f"skip {app.name}")
            continue

        with tempfile.TemporaryDirectory() as temp:
            cmd.run([], simulate=simulate, cwd=temp)
        benchmarks[app.name] = {}
        with open("benchmarks.json", "w") as f:
            json.dump(benchmarks, f)
            #cmd.run("tracedump", simulate=simulate, cwd=temp)


if __name__ == "__main__":
    main()
