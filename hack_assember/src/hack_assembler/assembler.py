import os
import ast

from hack_assembler import consts as c
from hack_assembler.parser import (parse_file, Label, AInstruction, CInstruction)

HACK_EXT = ".hack"

PREDEFINED_SYMBOLS = dict(
    SP=0,
    LCL=1,
    ARG=2,
    THIS=3,
    THAT=4,

    R0=0,
    R1=1,
    R2=2,
    R3=3,
    R4=4,
    R5=5,
    R6=6,
    R7=7,
    R8=8,
    R9=9,
    R10=10,
    R11=11,
    R12=12,
    R13=13,
    R14=14,
    R15=15,

    SCREEN=0x4000,
    KBD=0x6000
)

VARIABLE_BEGIN_OFFSET = 0x10

def compile_file(path):
    symbol_table = dict()
    symbol_table.update(PREDEFINED_SYMBOLS)
    variable_table = dict()

    assembly_lines = parse_file(path)
    # First pass, fill the symbol table
    program_offset = 0
    for asm_line in assembly_lines:
        if isinstance(asm_line, Label):
            label = asm_line
            symbol_table[label.name] = program_offset
        else:
            program_offset += 1

    # Second pass, convert the lines to binary.
    binary = []
    for asm_line in assembly_lines:
        if isinstance(asm_line, AInstruction):
            binary.append(
                compile_a_instruction(asm_line, symbol_table, variable_table)
            )
        elif isinstance(asm_line, CInstruction):
            binary.append(
                compile_c_instruction(asm_line)
            )

    return "\n".join(binary)


def write_output_to_file(input_path, output):
    hack_output_file = os.path.splitext(input_path)[0] + HACK_EXT
    open(hack_output_file, 'wb').write(output)

def compile_a_instruction(a_instruction, symbol_table, variable_table):
    value = resolve_value(a_instruction.value, symbol_table, variable_table)
    return "0" + convert_value_to_binary(value)

def resolve_value(value, symbol_table, variable_table):
    if value in symbol_table:
        # Check if the value is symbol.
        return symbol_table[value]

    elif value in variable_table:
        # Check if the value is pre declared variable
        return variable_table[value]
    else:
        # Try to evaluate the value as integer.
        # Don't support negative values at all.
        try:
            return int(value)
        except ValueError:
            # Declare this value as variable.
            variable_offset = VARIABLE_BEGIN_OFFSET
            declared_variable_offset = variable_table.values()
            while variable_offset in declared_variable_offset:
                variable_offset += 1

            # Set the symbol to be at this free offset
            variable_table[value] = variable_offset
            return variable_offset


def convert_value_to_binary(value):
    """
    Convert integer values to binary. Don't support negative values.
    """
    assert value >= 0, "Negative values not supported. %s" % value
    return bin(value)[2:].zfill(15)


def compile_c_instruction(c_instruction):
    dest = DEST_TO_BINARY[c_instruction.dest]
    comp = COMP_TO_BINARY[c_instruction.comp]
    jump = JUMP_TO_BINARY[c_instruction.jmp]
    return "111" + comp + dest + jump


DEST_TO_BINARY =  {
    c.DEST_null: "000",
    c.DEST_M: "001",
    c.DEST_D: "010",
    c.DEST_MD: "011",
    c.DEST_A: "100",
    c.DEST_AM: "101",
    c.DEST_AD: "110",
    c.DEST_AMD: "111"
}


JUMP_TO_BINARY = {
    c.JUMP_null: "000",
    c.JUMP_JGT: "001",
    c.JUMP_JEQ: "010",
    c.JUMP_JGE: "011",
    c.JUMP_JLT: "100",
    c.JUMP_JNE: "101",
    c.JUMP_JLE: "110",
    c.JUMP_JMP: "111"
}

COMP_TO_BINARY = {
    # A=0
    c.COMP_0: "0101010",
    c.COMP_1: "0111111",
    c.COMP_NEG_1: "0111010",
    c.COMP_D: "0001100",
    c.COMP_A: "0110000",
    c.COMP_NOT_D: "0001101",
    c.COMP_NOT_A: "0110001",
    c.COMP_NEG_D: "0001111",
    c.COMP_NEG_A: "0110011",
    c.COMP_D_PLUS_1: "0011111",
    c.COMP_A_PLUS_1: "0110111",
    c.COMP_D_MINUS_1: "0001110",
    c.COMP_A_MINUS_1: "0110010",
    c.COMP_D_PLUS_A: "0000010",
    c.COMP_D_MINUS_A: "0010011",
    c.COMP_A_MINUS_D: "0000111",
    c.COMP_D_AND_A: "0000000",
    c.COMP_D_OR_A: "0010101",

    # A=1
    c.COMP_M: "1110000",
    c.COMP_NOT_M: "1110001",
    c.COMP_NEG_M: "1110011",
    c.COMP_M_PLUS_1: "1110111",
    c.COMP_M_MINUS_1: "1110010",
    c.COMP_D_PLUS_M: "1000010",
    c.COMP_D_MINUS_M: "1010011",
    c.COMP_M_MINUS_D: "1000111",
    c.COMP_D_AND_M: "1000000",
    c.COMP_D_OR_M: "1010101",
}
