from collections import namedtuple

from vm_translator import consts


ArithmeticInstruction = namedtuple("ArithmeticInstruction", ["command"])
MemoryInstruction = namedtuple("MemoryInstruction", ["command", "segment", "index"])


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
        line = line.strip()
        if not skip_line(line):
            instructions.append(parse_instruction(line))

    return instructions


def skip_line(line):
    """
    Check if skip this line.
    :param line:
    :return:
    """
    return not line or line.startswith("//")


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
    else:
        raise RuntimeError("Unsupported instruction: %s" % line)
