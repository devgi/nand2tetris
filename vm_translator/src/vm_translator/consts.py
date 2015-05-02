
# List of arithmetic the vm commands
PUSH = "push"
POP = "pop"
ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"

# List of program flow commands

LABEL = "label"
GOTO = "goto"
IF_GOTO = "if-goto"

# List of function related commands
CALL = "call"
FUNCTION = "function"
RETURN = "return"


# List of memory segments
STATIC="static"
THIS="this"
LOCAL="local"
ARGUMENT="argument"
THAT="that"
CONSTANT="constant"
POINTER="pointer"
TEMP="temp"


REG_SEGMENTS = (POINTER, TEMP)


ARITHMETIC_INSTRUCTIONS = (
    ADD,
    SUB,
    NEG,
    EQ,
    GT,
    LT,
    AND,
    OR,
    NOT
)

MEMORY_INSTRUCTIONS = (
    PUSH,
    POP
)

PROGRAM_FLOW_INSTRUCTIONS = (
    LABEL,
    GOTO,
    IF_GOTO
)

FUNCTION_PROTOCOL_INSTRUCTIONS = (
    FUNCTION,
    CALL
)

# Sys.init function name (for bootsrap the program)
SYS_INIT = "Sys.init"