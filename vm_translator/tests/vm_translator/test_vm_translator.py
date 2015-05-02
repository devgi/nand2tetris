import py

from vm_translator.main import translate_to_hack_given_path

def test_vm_translator(vm_program, cpu_emulator):
    vm_program_path = py.path.local(vm_program)


    # Verify that the files exists, and remove
    # previous artifacts.

    for asm_path in vm_program_path.visit("*.asm"):
        asm_path.remove(ignore_errors=True)

    for out_path in vm_program_path.visit("*.out"):
        out_path.remove(ignore_errors=True)

    translate_to_hack_given_path(input_path=vm_program)

    assert len(list(vm_program_path.visit("*.asm"))), \
            ("Check that the program was translated successfully.")

    # Execute cpu emulator
    tst_path = vm_program_path.join(vm_program_path.basename + '.tst')
    cmp_path = vm_program_path.join(vm_program_path.basename + '.cmp')
    assert tst_path.check(file = 1)
    assert cmp_path.check(file = 1)

    cpu_emulator.sysexec(tst_path.strpath)

    out_path = vm_program_path.join(vm_program_path.basename + '.out')
    assert out_path.check(file=1), "Expected output file to be created"
    assert out_path.read() == cmp_path.read(), "Expected output to be the same as .cmp"