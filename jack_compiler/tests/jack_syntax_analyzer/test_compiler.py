from jack_compiler.compiler import JackCompiler


def test_compiler(directory_to_compile):
    compiler = JackCompiler()

    for jack_file in directory_to_compile.visit("*.jack"):
        _, bytecode = compiler.compile(jack_file.read())

        print bytecode

        reference_bytecode = jack_file.new(ext='vm.reference')
        original_bytecode = jack_file.new(ext='vm.original')

        expected_bytecode = original_bytecode.read()
        reference_bytecode.write(bytecode, mode='wb')

        assert bytecode.splitlines() == expected_bytecode.splitlines()


