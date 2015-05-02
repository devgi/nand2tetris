import os

import pytest
import py

all_vm_files = py.path.local(__file__).dirpath().join("resources").visit("*.vm")

@pytest.fixture(params=all_vm_files)
def vm_file(request):
    return request.param


NAND2TETRIS_TOOLS = os.environ.get("NAND2TETRIS_TOOLS", None)

@pytest.fixture
def cpu_emulator():
    if NAND2TETRIS_TOOLS is None:
        pytest.skip("NAND2TETRIS_TOOLS environment variable not defined.")

    cpu_emulator_bin = py.path.local(NAND2TETRIS_TOOLS).join("CPUEmulator.bat")

    if not cpu_emulator_bin.check(file=1):
        pytest.skip("CPUEmulator not found at %s" % cpu_emulator_bin)

    return cpu_emulator_bin