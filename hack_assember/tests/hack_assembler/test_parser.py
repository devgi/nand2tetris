import os

import pytest

import hack_assembler.consts as c
from hack_assembler.parser import (parse_program_line,
    CInstruction, AInstruction, Label, parse_file
)

@pytest.mark.parametrize(("line", "expected_result"),
                         [
                             ("A=D+A", CInstruction(dest=c.DEST_A,
                                                   comp=c.COMP_D_PLUS_A,
                                                   jmp=c.JUMP_null)),

                             ("0;JMP // foo bar", CInstruction(dest=c.DEST_null,
                                                               comp=c.COMP_0,
                                                               jmp=c.JUMP_JMP)),

                             ("@12", AInstruction(value="12")),

                             ("(LOOP_BEGIN)", Label(name="LOOP_BEGIN")),
                         ])

def test_parse_program_line(line, expected_result):
    assert parse_program_line(line) == expected_result


RESOURCE_DIR = os.path.join(os.path.dirname(__file__), 'resources')

@pytest.mark.parametrize(("asm_file",),
            [
                ("Add",),
                ("Max",),
                ("MaxL",),
                ("Pong",),
                ("Rect",),
                ("RectL",),
                ("PongL",),
            ])
def test_parse_asm_program(asm_file):
    asm_file = os.path.join(RESOURCE_DIR, asm_file + ".asm")
    res = parse_file(asm_file)
    assert res