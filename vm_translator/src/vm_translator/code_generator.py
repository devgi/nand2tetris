import os

from vm_translator import consts

class CodeGenerator(object):

    def __init__(self, debug=True):
        self._assembly_lines = []
        self.debug = debug

    def process_instruction(self, instruction):
        if self.debug:
            self._asm("// Instruction: %s" % repr(instruction))

        INSTRUCTION_COMMAND_TO_PROCESS_METHOD = {
            # Binray arithmatic commands.
            consts.ADD: self._process_binray_arithmetic_command,
            consts.SUB: self._process_binray_arithmetic_command,

            # Unary arithmatic commands

            # Memory instructions
            consts.PUSH: self._process_push,
            consts.POP: self._process_pop
        }

        process_instruction = INSTRUCTION_COMMAND_TO_PROCESS_METHOD[instruction.command]
        return process_instruction(instruction)

    def set_current_file(self, file_path):
        pass

    def get_assembly_code(self):
        """
        Get the complete assembly code for the program.
        :return: String represents the final HACK program.
        """
        return os.linesep.join(self._assembly_lines)

    def _asm(self, *asm_lines):
        self._assembly_lines.extend(asm_lines)

    def _process_binray_arithmetic_command(self, instruction):
        hack_instruction = self._BINARY_ARITHMETIC_COMMAND_TO_HACK[instruction.command]
        self._asm(
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            hack_instruction
        )

    def _process_push(self, instruction):
        # Read the value from the correct segment and store it in D
        # than store D value at the top of the stack and increment the stack.

        # If its to pseudo segment constants
        if instruction.segment == consts.CONSTANT:
            self._asm(
                "@" + instruction.index,
                "D=A",
            )

        # If its to one of the index based memory segments
        elif instruction.segment in self._MEMORY_SEGMENT_TO_BASE_VARIABLE:
            base = self._MEMORY_SEGMENT_TO_BASE_VARIABLE[instruction.segment]
            self._asm(
                "@" + base,
                "D=M",
                "@" + instruction.index,
                "A=D+A",
                "D=M",
            )
        elif instruction.segment in self._REG_SEGMENT_TO_BASE_VARIABLE_ADDRESS:
            base = self._REG_SEGMENT_TO_BASE_VARIABLE_ADDRESS[instruction.segment]
            self._asm(
                "@" + base,
                "D=A",
                "@" + instruction.index,
                "A=D+A",
                "D=M",
            )
        else:
            raise RuntimeError("Not supported memory instruction: %s" % instruction)

        # Store the value of D in @SP
        # And increment the value of SP
        self._asm(
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
        )

    def _process_pop(self, instruction):
        # Read the value from the correct segment and store it in D
        # than store the value of D at the top of the stack and increment
        # the stack pointer.

        if instruction.segment in self._MEMORY_SEGMENT_TO_BASE_VARIABLE:
            base = self._MEMORY_SEGMENT_TO_BASE_VARIABLE[instruction.segment]
            self._asm(
                "@" + base,
                "D=M",
                "@" + instruction.index,
                "D=D+A"
            )
        elif instruction.segment in self._REG_SEGMENT_TO_BASE_VARIABLE_ADDRESS:
            base = self._REG_SEGMENT_TO_BASE_VARIABLE_ADDRESS[instruction.segment]
            self._asm(
                "@" + base,
                "D=A",
                "@" + instruction.index,
                "D=D+A"
            )
        else:
            raise RuntimeError("Unsupported instruction: %" % instruction)

        self._asm(
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D"
        )


    _BINARY_ARITHMETIC_COMMAND_TO_HACK = {
        consts.ADD: "M=D+M",
        consts.SUB: "M=M-D",
        consts.AND: "M=D&M",
    }

    # Map memory segment instruction to the appropriate variable
    # which represents the segment base index.
    _MEMORY_SEGMENT_TO_BASE_VARIABLE = {
        consts.LOCAL: "LCL",
        consts.ARGUMENT: "ARG",
        consts.THIS: "THIS",
        consts.THAT: "THAT"
    }

    _REG_SEGMENT_TO_BASE_VARIABLE_ADDRESS = {
        consts.POINTER: "THIS",
        consts.TEMP: "R5"
    }