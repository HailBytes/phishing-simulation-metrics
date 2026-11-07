import importlib.util
import pathlib

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def _load(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def roi():
    return _load("calculate-roi")


@pytest.fixture(scope="session")
def variance():
    return _load("department-variance")


@pytest.fixture(scope="session")
def gophish():
    return _load("gophish-export")
