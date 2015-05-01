import collections

from hack_assembler import consts

Label = collections.namedtuple("Label", ["name"])
AInstruction = collections.namedtuple("AInstruction", ["value"])
CInstruction = collections.namedtuple("CInstruction", ["comp", "dest", "jmp"])


def parse_file(path):
    data = open(path, 'rt').read()
    return parse_data(data)

def parse_data(raw_program):
    program = []
    for program_line in read_lines(raw_program):
        res = parse_program_line(program_line)
        if res:
            program.append(res)
    return program

def read_lines(raw_program):
    for line in raw_program.splitlines():
        stripped_line = line.strip()
        if stripped_line:
            yield stripped_line

def strip_comments(program_line):
    line = program_line.split("//")[0]
    return line.strip()

def parse_program_line(program_line):
    program_line = strip_comments(program_line)
    if not program_line:
        return None

    elif parse_label(program_line):
        return parse_label(program_line)

    elif parse_a_instruction(program_line):
        return parse_a_instruction(program_line)

    else:
        return parse_c_instruction(program_line)

def parse_label(line):
    if line.startswith("(") and line.endswith(")"):
        name = line[1:-1]
        name = name.strip()
        # We can enforce names restrictions
        # here (all in alpha numeric ascii, etc..)
        return Label(name=name)

def parse_a_instruction(line):
    if line.startswith("@"):
        value = line[1:]
        return AInstruction(value=value)

def parse_c_instruction(line):
    if consts.JMP_SEP in line:
        line, jmp = line.split(consts.JMP_SEP)
        jmp = jmp.strip()
        assert jmp in consts.LEGAL_JUMP, 'Illegal jump.'
    else:
        jmp = consts.JUMP_null

    if consts.DST_SEP in line:
        dest, line = line.split(consts.DST_SEP)
        dest = dest.strip()
        assert dest in consts.LEGAL_DEST, "Illegal destination"
    else:
        dest=consts.DEST_null

    comp = line.strip()
    assert comp in consts.LEGAL_COMP, "Illegal compute"
    return CInstruction(comp=comp,
                        dest=dest,
                        jmp=jmp)


