import sys
import os

from jack_syntax_analyzer.analyzer import analyze

def parse_args():
    if len(sys.argv) < 2:
        print "Usage: %s <jack file/ directory>" % sys.argv[0]
        sys.exit(1)
    return sys.argv[1]

def main():
    input_path = parse_args()
    if os.path.isdir(input_path):
        inputs = [os.path.join(input_path, filename) for filename in os.listdir(input_path) if filename.endswith(".jack")]
    else:
        inputs = [input_path]

    for input_file in inputs:
        jack_file_content = open(input_file).read()
        output_file = os.path.splitext(input_file)[0] + ".xml"
        open(output_file, 'wb').write(analyze(jack_file_content))

if __name__ == "__main__":
    main()  
