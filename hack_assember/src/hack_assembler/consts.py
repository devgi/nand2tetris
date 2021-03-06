JMP_SEP = ';'
DST_SEP = "="

JUMP_null = "" # Null jump is empty and not "null"
JUMP_JGT = "JGT"
JUMP_JEQ="JEQ"
JUMP_JGE="JGE"
JUMP_JLT="JLT"
JUMP_JNE="JNE"
JUMP_JLE="JLE"
JUMP_JMP="JMP"

LEGAL_JUMP = (JUMP_null, JUMP_JGT , JUMP_JEQ, JUMP_JGE,
              JUMP_JLT, JUMP_JNE, JUMP_JLE, JUMP_JMP)

DEST_null="" # Null dest is empty and not "null"
DEST_M="M"
DEST_D="D"
DEST_MD="MD"
DEST_A="A"
DEST_AM="AM"
DEST_AD="AD"
DEST_AMD="AMD"

LEGAL_DEST =  (DEST_null, DEST_M, DEST_D, DEST_MD,
               DEST_A, DEST_AM, DEST_AD, DEST_AMD)
COMP_0="0"
COMP_1="1"
COMP_NEG_1="-1"
COMP_D="D"
COMP_A="A"
COMP_NOT_D="!D"
COMP_NOT_A="!A"
COMP_NEG_D="-D"
COMP_NEG_A="-A"
COMP_D_PLUS_1="D+1"
COMP_A_PLUS_1="A+1"
COMP_D_MINUS_1="D-1"
COMP_A_MINUS_1="A-1"
COMP_D_PLUS_A="D+A"
COMP_D_MINUS_A="D-A"
COMP_A_MINUS_D="A-D"
COMP_D_AND_A="D&A"
COMP_D_OR_A="D|A"
COMP_M="M"
COMP_NOT_M="!M"
COMP_NEG_M="-M"
COMP_M_PLUS_1="M+1"
COMP_M_MINUS_1="M-1"
COMP_D_PLUS_M="D+M"
COMP_D_MINUS_M="D-M"
COMP_M_MINUS_D="M-D"
COMP_D_AND_M="D&M"
COMP_D_OR_M="D|M"

LEGAL_COMP = (COMP_0, COMP_1, COMP_NEG_1, COMP_D, COMP_A, COMP_NOT_D,
              COMP_NOT_A, COMP_NEG_D, COMP_NEG_A, COMP_D_PLUS_1, COMP_A_PLUS_1,
              COMP_D_MINUS_1, COMP_A_MINUS_1, COMP_D_PLUS_A, COMP_D_MINUS_A,
              COMP_A_MINUS_D, COMP_D_AND_A, COMP_D_OR_A, COMP_M, COMP_NOT_M,
              COMP_NEG_M, COMP_M_PLUS_1, COMP_M_MINUS_1, COMP_D_PLUS_M,
              COMP_D_MINUS_M, COMP_M_MINUS_D, COMP_D_AND_M, COMP_D_OR_M)