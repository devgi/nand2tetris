import py
import pytest

from vm_translator.parser import (parse_instruction, parse_vm_file_content,
                                  MemoryInstruction, ArithmeticInstruction)


@pytest.mark.parametrize(
    ("instruction_line", "expected_instruction"),
    [
        ("push constant 122", MemoryInstruction(command="push",
                                               segment="constant",
                                               index="122")),
        ("eq", ArithmeticInstruction(command="eq"))
    ]
)
def test_simple_content(instruction_line, expected_instruction):
    assert parse_instruction(instruction_line) == expected_instruction


def test_parse_files(vm_file):
    instructions = parse_vm_file_content(vm_file.read())
    assert len(instructions) > 0