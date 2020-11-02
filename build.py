from typing import Dict


def build(setup_kwargs: Dict[str, str]) -> None:
    setup_kwargs["cffi_modules"] = "pt/ffi.py:ffibuilder"
