import os

import pytest

from hack_assembler.parser import parse_a_instruction
from hack_assembler.assembler import compile_a_instruction, HACK_EXT, compile_file


@pytest.mark.parametrize(
    ("asm_line", "expected_output"),
    [
        ("@1", "0000000000000001"),
        ("@100", "0000000001100100"),
        ("@12", "0000000000001100")
    ]

)
def test_convert_a_instruction_direct_value(asm_line, expected_output):
    instruction = parse_a_instruction(asm_line)
    assert compile_a_instruction(instruction, {}, {}) == expected_output


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')

@pytest.mark.parametrize(("program",),
            [
                ("Add",),
                ("Max",),
                ("MaxL",),
                ("Pong",),
                ("Rect",),
                ("RectL",),
                ("PongL",),
            ])
def test_compile_program(program):
    asm_file =  os.path.join(RESOURCE_DIR, program + ".asm")
    hack_file = os.path.join(RESOURCE_DIR, program + HACK_EXT)
    assert compile_file(asm_file).splitlines() == open(hack_file).read().splitlines()