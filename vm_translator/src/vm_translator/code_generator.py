import os
import itertools


from vm_translator import consts

class CodeGenerator(object):

    def __init__(self, debug=True):
        self._assembly_lines = []
        self.debug = debug
        self._current_file = None
        self._label_counter = itertools.count(1)

    def process_instruction(self, instruction):
        """
        Process signle instruction inside given file. Not that the file
        must be set before the instructions are processed.
        :param instruction: instance of Instruction like object (see Parser)
        """
        if self.debug:
            self._asm("// Instruction: %s at file %s" % (repr(instruction),
                                                         self._current_file))

        # Map between vm instruction, to the correct hack translation
        # routine.
        INSTRUCTION_COMMAND_TO_PROCESS_METHOD = {
            # Binray arithmatic commands.
            consts.ADD: self._process_binray_arithmetic_command,
            consts.SUB: self._process_binray_arithmetic_command,
            consts.AND: self._process_binray_arithmetic_command,
            consts.OR: self._process_binray_arithmetic_command,

            # Unary arithmatic commands
            consts.NOT: self._process_unary_arithmetic_command,
            consts.NEG: self._process_unary_arithmetic_command,

            # Compare commands
            consts.EQ: self._process_compare_command,
            consts.GT: self._process_compare_command,
            consts.LT: self._process_compare_command,

            # Memory instructions
            consts.PUSH: self._process_push,
            consts.POP: self._process_pop
        }

        process_instruction = INSTRUCTION_COMMAND_TO_PROCESS_METHOD[instruction.command]
        return process_instruction(instruction)

    def set_current_file(self, file_path):
        """
        Change the current file we process. This infects the prefix of static
        addresses.
        :param file_path: The path of the file we process.
        """
        self._current_file = os.path.basename(file_path)

    def get_assembly_code(self):
        """
        Get the complete assembly code for the program.
        :return: String represents the final HACK program.
        """
        return os.linesep.join(self._assembly_lines)

    def _asm(self, *asm_lines):
        self._assembly_lines.extend(asm_lines)

    def _process_binray_arithmetic_command(self, instruction):
        """
        Translate to hack single binary arithmetic instruction.
        :param instruction: The instruction to translate.
        """
        # Map between command to the appropriate hack instruction
        # assuming D is the value on the top of the stack, and A
        # is set to the second cell (thus M is both the location
        # to write the instruction results to and value needs to be read)
        BINARY_ARITHMETIC_TO_HACK_INSTRUCTION = {
            consts.ADD: "M=D+M",
            consts.SUB: "M=M-D",
            consts.AND: "M=D&M",
            consts.OR: "M=D|M"
        }

        binary_op_on_D_and_M = BINARY_ARITHMETIC_TO_HACK_INSTRUCTION[instruction.command]
        self._asm(
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            binary_op_on_D_and_M
        )

    def _process_unary_arithmetic_command(self, instruction):
        """
        Translate to hack single unary arithmetic instruction.
        :param instruction: The instruction to translate.
        """
        # Map between command to the appropriate hack instruction
        # assuming A is set to the top of the stack.
        UNARY_ARITHMETIC_TO_HACK_INSTRUCTION = {
            consts.NEG: "M=-M",
            consts.NOT: "M=!M"
        }
        unary_op_on_M = UNARY_ARITHMETIC_TO_HACK_INSTRUCTION[instruction.command]
        self._asm(
            "@SP",
            "A=M-1",
            unary_op_on_M
        )

    def _process_compare_command(self, instruction):
        # Map between compare command to the appropriate hack conditional
        # jump instruction, assuming D contains X - Y
        # where X and Y are the following stack cells (according to the book):
        #        |...|
        #        |_X_|
        #        |_Y_|
        #  SP -> |   |
        COMPARISON_TO_HACK_JUMP_INSTRUCTION = {
            consts.EQ: "D;JEQ", # x == y
            consts.GT: "D;JGT", # x > y
            consts.LT: "D;JLT" # x< y
        }
        conditional_jump_over_D = COMPARISON_TO_HACK_JUMP_INSTRUCTION[instruction.command]

        condition_true_label = self._label("condition.true")
        self._asm(
            "@SP",
            "AM=M-1",
            "D=M", # D = Y
            "A=A-1",
            "D=M-D", # D = X - Y
            # Set the head of the stack to be True (0xffff)
            "M=-1",
            "@" + condition_true_label,
            conditional_jump_over_D,
            # In case of false increment the stack head value by one
            # so it became False (0)
            "@SP",
            "A=M-1",
            "M=M+1",
            "(%s)" % condition_true_label,
        )

    def _static_symbol(self, index):
        """
        Return a string representation of this static symbol
        :param index: The index of within the static segment.
        :return: str.
        """
        return "%s.%s" % (self._current_file, index)

    def _label(self, name):
        """
        Create new string which represent unique label in the generated assembly
        program.
        :param name: The name of the label. Uses only for ease on the eys while
        debugging.
        :return: String.
        """
        return "%s.%d" % (name, self._label_counter.next())

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
        elif instruction.segment == consts.STATIC:
            static_variable = self._static_symbol(instruction.index)
            self._asm(
                "@" + static_variable,
                "D=M"
            )

        else:
            raise RuntimeError("Not supported memory instruction: %s" % repr(instruction))

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
        # Set D to contain the address of the correct address to fill (depend
        # on the segment type)
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
        elif instruction.segment == consts.STATIC:
            static_variable = self._static_symbol(instruction.index)
            self._asm(
                "@" + static_variable,
                "D=A"
            )
        else:
            raise RuntimeError("Unsupported instruction: %s" % repr(instruction))

        self._asm(
            "@R13",
            "M=D", # R13 <- address of the cell to read from
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D"
        )

    # Map memory segment instruction to the appropriate variable
    # which its value represents the segment base index.
    _MEMORY_SEGMENT_TO_BASE_VARIABLE = {
        consts.LOCAL: "LCL",
        consts.ARGUMENT: "ARG",
        consts.THIS: "THIS",
        consts.THAT: "THAT"
    }

    # Map memory segment instruction to the appropriate variable
    # which its address represents the segment base index.
    _REG_SEGMENT_TO_BASE_VARIABLE_ADDRESS = {
        consts.POINTER: "THIS",
        consts.TEMP: "R5"
    }