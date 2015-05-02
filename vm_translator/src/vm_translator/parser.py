from collections import namedtuple

from vm_translator import consts


ArithmeticInstruction = namedtuple("ArithmeticInstruction", ["command"])
MemoryInstruction = namedtuple("MemoryInstruction", ["command", "segment", "index"])
ProgramFlowInstruction = namedtuple("ProgramFlowInstruction", ["command", "label"])


def parse_vm_file(path):
    """
    Parse vm file.
    :param filename: The file path.
    :return: List of instructions.
    """
    return parse_vm_file_content(open(path).read())


def parse_vm_file_content(file_content):
    """
    Parse single vm file into list of Instructions.
    :param file_content: The content of a file
    :return: List of instructions.
    """
    lines = file_content.splitlines()
    instructions = []
    for line in lines:
        # Strip the comments and the extra spaces.
        line_without_comments = strip_comments(line).strip()
        if line_without_comments:
            instructions.append(parse_instruction(line_without_comments))

    return instructions


def strip_comments(line):
    COMMENT = "//"
    if COMMENT in line:
        return line.split(COMMENT)[0]
    else:
        return line


def parse_instruction(line):
    """
    Parse single instruction.
    :param line: Line from .vm file (No comments)
    :return: Instruction object.
    """
    terms = line.split(" ")
    instruction = terms[0]

    if instruction in consts.ARITHMETIC_INSTRUCTIONS:
        return ArithmeticInstruction(*terms)
    elif instruction in consts.MEMORY_INSTRUCTIONS:
        return MemoryInstruction(*terms)
    elif instruction in consts.PROGRAM_FLOW_INSTRUCTIONS:
        return ProgramFlowInstruction(*terms)
    else:
        raise RuntimeError("Unsupported instruction: %s" % line)
