import py

from vm_translator.main import translate_to_hack

def test_vm_translator(vm_file, cpu_emulator):
    vm_path = py.path.local(vm_file)
    asm_path = vm_path.new(ext='.asm')
    out_path = vm_path.new(ext='.out')
    tst_path = vm_path.new(ext='.tst')
    cmp_path = vm_path.new(ext='.cmp')

    # Verify that the files exists, and remove
    # previous artifacts.
    assert tst_path.check(file=1)
    assert vm_path.check(file=1)
    if asm_path.check(file=1):
        asm_path.remove(ignore_errors=True)
    if out_path.check(file=1):
        out_path.remove(ignore_errors=True)

    translate_to_hack(file_paths=[vm_path.strpath], output_path=asm_path.strpath)
    assert asm_path.check(file=1), ("Check that the program was translated "
                                    "successfully.")

    # Execute cpu emulator
    cpu_emulator.sysexec(tst_path.strpath)
    assert out_path.check(file=1), "Expected output file to be created"
    assert out_path.read() == cmp_path.read(), "Expected output to be the same as .cmp"