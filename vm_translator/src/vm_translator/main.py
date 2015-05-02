import sys
import os

from vm_translator.parser import parse_vm_file
from vm_translator.code_generator import CodeGenerator

def translate_to_hack(file_paths, output_path):
    code_generator = CodeGenerator()
    for path in file_paths:
        instructions = parse_vm_file(path)
        code_generator.set_current_file(path)

        for instruction in instructions:
            code_generator.process_instruction(instruction)

    return open(output_path, 'wb').write(code_generator.get_assembly_code())

def translate_to_hack_given_path(input_path):
    if os.path.isdir(input_path):
        paths = [os.path.join(input_path, filename) for
                 filename in os.listdir(input_path) if filename.endswith(".vm")]
        output_file =  os.path.join(input_path, os.path.basename(input_path) + ".asm")
    else:
        paths = [input_path]
        output_file = os.path.splitext(input_path)[0] + '.asm'

    translate_to_hack(paths, output_file)

def parse_args():
    if len(sys.argv) < 2:
        print "Usage: %s <vm file/ directory>" % sys.argv[0]
        sys.exit(1)
    return sys.argv[1]

def main():
    input_path = parse_args()
    translate_to_hack_given_path(input_path)

if __name__ == "__main__":
    main()  
