import os
from jack_compiler import consts
from jack_compiler.symbol_table import SubroutineSymbolTable, ClassSymbolTable


class VMBytecodeWriter(object):
    WHILE_START_LABEL = 'WHILE_EXP{index}'
    WHILE_END_LABEL = 'WHILE_END{index}'
    IF_LABEL = 'IF_TRUE{index}'
    ELSE_LABEL = 'IF_FALSE{index}'
    IF_END_LABEL = 'IF_END{index}'

    def __init__(self):
        self._bytecode = []
        self._while_index = 0
        self._if_index = 0

    def _write(self, *lines):
        self._bytecode.extend(lines)

    def save(self):
        return os.linesep.join(self._bytecode)

    def write_function_declaration(self, name, num_of_local_vars):
        self._if_index = 0
        self._while_index = 0
        self._write('function {name} {num}'.format(name=name, num=num_of_local_vars))

    def write_constructor(self, num_of_class_fields):
        self.write_push('constant', num_of_class_fields)
        self.write_method_call('Memory.alloc', 1)
        self.write_pop('pointer', 0)

    def write_method_declaration(self):
        self.write_push('argument', 0)
        self.write_pop('pointer', 0)

    def write_method_call(self, function_name, num_of_args):
        self._write('call {name} {num}'.format(name=function_name, num=num_of_args))


    def write_push(self, segment, index):
        self._write('push {segment} {index}'.format(segment=segment,index=index))

    def write_pop(self, segment, index):
        self._write('pop {segment} {index}'.format(segment=segment,index=index))

    def write_return(self):
        self._write('return')

    def write_binary_operation(self, symbol):
        symbol_to_command = {
            '+': 'add',
            '*': 'call Math.multiply 2',
            '-': 'sub',
            '/': 'call Math.divide 2',
            '&': 'and',
            '<': 'lt',
            '>': 'gt',
            '=': 'eq',
            '|': 'or',
        }
        self._write(symbol_to_command[symbol])

    def write_unary_operation(self, symbol):
        symbol_to_command = {
            '-': 'neg',
            '~': 'not'
        }
        self._write(symbol_to_command[symbol])

    def write_push_symbol(self, symbol):
        self.write_push(self.symbol_kind_to_segment(symbol.kind), symbol.index)

    def write_pop_symbol(self, symbol):
        self.write_pop(self.symbol_kind_to_segment(symbol.kind), symbol.index)

    def symbol_kind_to_segment(self,symbol_kind):
        kind_mapping = {
            SubroutineSymbolTable.VAR: 'local',
            SubroutineSymbolTable.ARGUMENT: 'argument',
            consts.FIELD: 'this',
            consts.STATIC: 'static',
        }
        return kind_mapping[symbol_kind]

    def write_builtin_value(self, value):
        if value == consts.TRUE:
            self.write_push('constant', 0)
            self._write('not')
        elif value == consts.FALSE:
            self.write_push('constant', 0)
        elif value == consts.THIS:
            self.write_push('pointer', 0)
        elif value == consts.NULL:
            self.write_push('constant', 0)
        else:
            raise ValueError(value)

    def write_label(self, label):
        self._write('label {}'.format(label))

    def write_if_goto(self, label):
        self._write('if-goto {label}'.format(label=label))

    def write_goto(self, label):
        self._write('goto {label}'.format(label=label))

    def write_while_declaration_start(self):
        self.write_label(self.WHILE_START_LABEL.format(index=self._while_index))
        self._while_index += 1
        return self._while_index - 1

    def write_while_declaration_end(self, index):
        self._write('not')
        self.write_if_goto(self.WHILE_END_LABEL.format(index=index))

    def write_while_end(self, index):
        self.write_goto(self.WHILE_START_LABEL.format(index=index))
        self.write_label(self.WHILE_END_LABEL.format(index=index))

    def write_if_start(self):
        self.write_if_goto(self.IF_LABEL.format(index=self._if_index))
        self.write_goto(self.ELSE_LABEL.format(index=self._if_index))
        self.write_label(self.IF_LABEL.format(index=self._if_index))
        self._if_index += 1
        return self._if_index - 1

    def write_else(self, index):
        self.write_goto(self.IF_END_LABEL.format(index=index))
        self.write_label(self.ELSE_LABEL.format(index=index))

    def write_if_end(self, index, is_else):
        if is_else:
            self.write_label(self.IF_END_LABEL.format(index=index))
        else:
            self.write_label(self.ELSE_LABEL.format(index=index))

    def write_string(self, string):
        self.write_push('constant', len(string))
        self.write_method_call('String.new', 1)
        for c in string:
            self.write_push('constant', ord(c))
            # 2 arguments because the string reference was never popped
            self.write_method_call('String.appendChar', 2)

    def write_array_assignment(self):
        self.write_pop('temp', 0)
        self.write_pop('pointer', 1)
        self.write_push('temp', 0)
        self.write_pop('that', 0)

    def write_array_indexing(self, symbol):
        self.write_push_symbol(symbol)
        self.write_binary_operation('+')
        self.write_pop('pointer', 1)
        self.write_push('that', 0)