import pytest
import py

all_vm_files = py.path.local(__file__).dirpath().join("resources").visit("*.vm")

@pytest.fixture(params=all_vm_files)
def vm_file(request):
    return request.param