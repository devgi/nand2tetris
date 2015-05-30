from jack_syntax_analyzer.analyzer import JackCompiler

def test_compiler(directory_to_compile):
    compiler = JackCompiler()

    for jack_file in directory_to_compile.visit("*.jack"):
        _, bytecode = compiler.analyze(jack_file.read())

        print bytecode

        reference_bytecode = jack_file.new(ext='vm.reference')
        original_bytecode = jack_file.new(ext='vm.original')

        expected_bytecode = None

        if reference_bytecode.check(file=1):
            expected_bytecode = reference_bytecode.read()

        elif original_bytecode.check(file=1):
                expected_bytecode = original_bytecode.read()

        assert bytecode.splitlines() == expected_bytecode.splitlines()


