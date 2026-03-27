from dataclasses import dataclass
from typing import Callable, Dict


FilterBuilder = Callable[[Dict[str, str]], str]


@dataclass(frozen=True)
class EffectDefinition:
    name: str
    description: str
    builder: FilterBuilder
    mode: str = "af"
