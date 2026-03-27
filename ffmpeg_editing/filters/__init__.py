from importlib import import_module
from pathlib import Path


def _module_names():
    current_dir = Path(__file__).parent
    for path in sorted(current_dir.glob("*.py")):
        if path.name in {"__init__.py", "base.py"}:
            continue
        yield path.stem


def load_effects():
    effects = {}
    package_prefix = __name__
    for module_name in _module_names():
        module = import_module(f"{package_prefix}.{module_name}")
        definitions = module.get_effect_definitions()
        for definition in definitions:
            if definition.name in effects:
                raise ValueError(f"Duplicate effect name detected: {definition.name}")
            effects[definition.name] = definition
    return effects
