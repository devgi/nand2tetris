import os
import itertools

from vm_translator.parser import MemoryInstruction, ProgramFlowInstruction
from vm_translator import consts

class CodeGenerator(object):

    def __init__(self, debug=True):
        self._assembly_lines = []
        self.debug = debug
        self._current_file = None

        # This flag states if Sys.init function was processed during translation
        # and if so make sure later that it will be called during the bootstrap.
        self._call_sys_init = False

        # Uses us to give unique labels for comparison statements.
        self._label_counter = itertools.count(1)

        # Uses us to track which is the current function we process
        # (This is important for scoping labels and flow control instructions)
        self._current_func = ""

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
            consts.POP: self._process_pop,

            # Program Flow instructions
            consts.LABEL: self._process_label,
            consts.GOTO: self._process_goto,
            consts.IF_GOTO: self._process_if_goto,

            # Function Protocol Instructions
            consts.FUNCTION: self._process_function_declaration,
            consts.CALL: self._process_function_call,
            consts.RETURN: self._process_return
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
        if self._call_sys_init:
            bootstrap = [
                "@256",
                "D=A",
                "@SP",
                "M=D",
                ""
            ]

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

        condition_true_label = self._get_unique_label("condition.true")
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

    def _process_label(self, instruction):
        self._asm("(%s)" % self._get_label_within_function(instruction.label))

    def _process_goto(self, instruction):
        self._asm("@" + self._get_label_within_function(instruction.label),
                  "0;JMP")

    def _process_if_goto(self, instruction):
        self._asm(
            "@SP",
            "AM=M-1",
            "D=M",
            "@" +  self._get_label_within_function(instruction.label),
            "D;JNE"
        )

    def _process_function_declaration(self, instruction):
        self._current_func = instruction.function_name

        if self._current_func ==

        self._asm(
            "(%s)" % self._current_func,
        )
        for _ in xrange(int(instruction.number_of_arguments)):
            self._process_push(MemoryInstruction(command=consts.PUSH,
                                                 segment=consts.CONSTANT,
                                                 index="0"))

    def _process_function_call(self, instruction):
        return_address_label = self._get_unique_label(
            name="return-from-" + instruction.function_name)

        # 1. Push return address, we use push constant with index
        # as label (which mean push the value of this label).
        self._process_push(MemoryInstruction(command=consts.PUSH,
                                             segment=consts.CONSTANT,
                                             index=return_address_label))

        # 2. Push the value of LCL
        self._process_push(MemoryInstruction(command=consts.PUSH,
                                             segment=consts.CONSTANT,
                                             index="LCL"),
                           dereference_constant=True)

        # 3. Push the value of ARG
        self._process_push(MemoryInstruction(command=consts.PUSH,
                                             segment=consts.CONSTANT,
                                             index="ARG"),
                           dereference_constant=True)

        # 4. Push the value of THIS
        self._process_push(MemoryInstruction(command=consts.PUSH,
                                             segment=consts.CONSTANT,
                                             index="THIS"),
                           dereference_constant=True)

        # 5. Push the value of THAT
        self._process_push(MemoryInstruction(command=consts.PUSH,
                                             segment=consts.CONSTANT,
                                             index="THAT"),
                           dereference_constant=True)

        # 6. ARG <- SP - n - 5 (n - number of arguments)
        self._asm(
            "@SP",
            "D=M",
            "@" + str((int(instruction.number_of_arguments) + 5)), # (n + 5)
            "D=D-A", # SP - (n + 5)
            "@ARG",
            "M=D",
        )

        # 7. LCL <- SP
        self._asm(
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
        )

        # 8. Goto function.
        self._asm(
            "@" + instruction.function_name,
            "0;JMP"
        )

        # 9. Declare the return address
        self._asm(
            "(%s)" % return_address_label
        )

    def _xprocess_return(self, instruction):
        FRAME = "R13"
        RET = "R14"

        # 1. Frame <- *LCL.
        self._asm(
            "@LCL",
            "D=M",
            "@" + FRAME,
            "M=D",
        )

        # # 2. RET=*(FRAME - 5)
        self._asm(
            "@" + FRAME,
            "D=A",
            "@5",
            "A=D-A",
            "D=M",
            "@" + RET,
            "M=D",
        )

        # 3. ARG=pop()
        self._asm(
            "@SP",
            "A=M-1", # FIXME: MAYBE am?
            "D=M",
            "@ARG",
            "A=M",
            "M=D")

        # 4. SP = ARG + 1
        self._asm("@ARG",
                  "D=M+1",
                  "@SP",
                  "M=D")

        # (for the next steps we put FRAME value at D)
        # 5. THAT=*(FRAME-1)
        # 6. THIS=*(FRAME-2)
        # 7. ARG=*(FRAME-3)
        # 8. LCL=*(FRAME-4)
        # 9. RET==*(FRAME-5)
        #
        for idx, dest in enumerate(("THAT", "THIS", "ARG", "LCL")): #RET):
            stack_offset = idx + 1
            self._asm(
                    "// %s = *(FRAME - %d)" % (dest, stack_offset),
                    "@" + FRAME,
                    "D=M",
                    "@" + str(stack_offset),
                    "A=D-A",
                    "D=M",
                    "@" + dest,
                    "M=D")

        # 10. goto RET
        self._asm("@" + RET,
                  "0;JMP")
        
    def _process_return(self, instruction):
        self._asm(
            # *(LCL - 5) -> R13
            "@LCL",
            "D=M",
            "@5",
            "A=D-A",
            "D=M",
            "@R13",
            "M=D",
            # *(SP - 1) -> *ARG
            "@SP",
            "A=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D ",
            # ARG + 1 -> SP
            "D=A+1",
            "@SP",
            "M=D",
            # *(LCL - 1) -> THAT; LCL--
            "@LCL",
            "AM=M-1",
            "D=M",
            "@THAT",
            "M=D",
            # *(LCL - 1) -> THIS; LCL--
            "@LCL",
            "AM=M-1",
            "D=M",
            "@THIS",
            "M=D",
            # *(LCL - 1) -> ARG; LCL--
            "@LCL",
            "AM=M-1",
            "D=M",
            "@ARG",
            "M=D",
            # *(LCL - 1) -> LCL
            "@LCL",
            "A=M-1",
            "D=M",
            "@LCL",
            "M=D",
            # R13 -> A
            "@R13",
            "A=M",
            "0;JMP")

    def _static_symbol(self, index):
        """
        Return a string representation of this static symbol
        :param index: The index of within the static segment.
        :return: str.
        """
        return "%s.%s" % (self._current_file, index)

    def _get_label_within_function(self, label_name):
        """
        :param label_name: The name of the label (used in flow control instructions)
        :return: label for the current scope.
        """
        return "{func}.{label}".format(
                    func=self._current_func,
                    label=label_name)

    def _get_unique_label(self, name):
        """
        Create new string which represent unique label in the generated assembly
        program.
        :param name: The name of the label. Uses only for ease on the eys while
        debugging.
        :return: String.
        """
        return "%s.%d" % (name, self._label_counter.next())

    def _process_push(self, instruction, dereference_constant=False):
        # Read the value from the correct segment and store it in D
        # than store D value at the top of the stack and increment the stack.

        # If its to pseudo segment constants
        if instruction.segment == consts.CONSTANT:
            self._asm(
                "@" + instruction.index,
                "D=A" if not dereference_constant else "D=M",
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