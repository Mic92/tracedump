# only covers the basic that I need at the moment.
# Can be extended based on demand
from typing import Any

CData: Any

def new(type: str, initial_data: Any = None) -> CData: ...
def cast(type: str, value: CData) -> CData: ...
def string(value: CData) -> bytes: ...
