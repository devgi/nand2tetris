import contextlib

from jack_syntax_analyzer.consts import (CLASS, FIELD, STATIC, BOOLEAN, CHAR,
                                         INT, CONSTRUCTOR, FUNCTION, METHOD, VOID, VAR, LET, IF, WHILE, DO,
                                         RETURN, ELSE, TRUE, FALSE, NULL, THIS, OPS, UNARY_OPS)
from jack_syntax_analyzer.tokenizer import (tokenize, Keyword, Symbol,
                                            Identifier, Integer, String)

from jack_syntax_analyzer.symbol_table import SymbolTable, SubroutineSymbolTable
from jack_syntax_analyzer.vm_writer import VMBytecodeWriter


class JackCompiler(object):
    def __init__(self):
        self._symbol_table = SymbolTable()

    def analyze(self, jack_file_content):
        tokens = tokenize(jack_file_content)
        return JackAnalyzer(tokens, self._symbol_table).process()


class JackAnalyzer(object):
    """
    Analyze the syntax of jack file.
    This class should process only single file since it maintain a state.
    """

    def __init__(self, tokens, symbol_table):
        self._xml_result = ""
        self._indentation_level = 0
        self._tokens = tokens
        self.position = 0
        self._symbol_table = symbol_table
        self._vm_bytecode = VMBytecodeWriter()

    def process(self):
        self._process_class()
        assert len(self._tokens) == self.position, "Verify that there are no leftover"
        return (self._xml_result, self._vm_bytecode.save())

    def _write_to_xml(self, node):
        indentation = (2 * " ") * self._indentation_level
        self._xml_result += indentation + node + "\n"

    def _write_single_token(self, token):
        self._write_to_xml(token.to_xml())
        self.position += 1

    @contextlib.contextmanager
    def _write_parsing_rule(self, rule):
        try:
            self._write_to_xml("<%s>" % rule)
            self._indentation_level += 1
            yield
        finally:
            self._indentation_level -= 1
            self._write_to_xml("</%s>" % rule)


    # def _write_token_list(self, tokens):
    # for token in tokens:
    # self._write_single_token(token)

    def _next_token(self):
        return self._tokens[self.position]

    def _is_next_token(self, token_type, *possible_values):
        """
        Query the next token
        :param token_type: The expected token type.
        :param possible_values: possible values for the token.
        :return: True if the token is as expected False otherwise.
            This method don't advance the position
        """
        token = self._next_token()
        return self._is_token(token, token_type, *possible_values)

    def _is_token(self, token, token_type, *possible_values):
        """
        Query information about a given token
        :param token_type: The expected token type.
        :param possible_values: possible values for the token.
        :return: True if the token is as expected False otherwise.
            This method don't advance the position
        """
        if possible_values:
            # Check if the type and the possible value
            return isinstance(token, token_type) and token.value in possible_values
        else:
            # Check if the type.
            return isinstance(token, token_type)

    def _expect_keyword(self, *possible_keywords):
        """
        Expect the next token to be keyword from range of possible values.
        :param possible_keywords:  The possible values of the keyboard
        :return: The actual value of the keyword.
        """
        assert self._is_next_token(Keyword, *possible_keywords), 'expected %s' % repr(possible_keywords)

        token = self._next_token()
        self._write_single_token(token)
        return token.value

    def _expect_symbol(self, *possible_symbols):
        """
        Expect the next token to be symbol from range of possible values.
        :param possible_symbols:  The possible values of the symbol
        :return: The actual value of the symbol.
        """
        assert self._is_next_token(Symbol, *possible_symbols), 'expected %s' % repr(possible_symbols)

        token = self._next_token()
        self._write_single_token(token)
        return token.value

    def _expect_identifier(self):
        """
        Expect identifier token.
        :return: The value of the identifier.
        """
        token = self._next_token()
        assert isinstance(token, Identifier), 'expected identifier'
        self._write_single_token(token)
        return token.value

    def _expected_symbol_definition(self, kind, variable_type):
        """
        Expects a symbol definition (as oppose to usage).
        """
        identifier = self._expect_identifier()
        self._symbol_table.define_symbol(identifier, kind, variable_type)

    def _expect_type(self):
        """
        Expect type description. Type may be class name (identifier)
        or native type (int, char, bool).
        :return: The type.
        """
        token = self._next_token()
        if isinstance(token, Identifier):
            return self._expect_identifier()

        else:
            return self._expect_keyword(CHAR, BOOLEAN, INT)

    def _process_class(self):
        with self._write_parsing_rule("class"):
            self._expect_keyword(CLASS)

            class_name = self._expect_identifier()
            self._symbol_table.start_class(class_name)

            self._expect_symbol("{")
            self._expect_class_variable_declarations()
            self._expect_subroutine_declarations()
            self._expect_symbol("}")

    def _expect_class_variable_declarations(self):
        while self._is_next_token(Keyword, FIELD, STATIC):
            self._process_single_class_variable_declaration()

    def _process_single_class_variable_declaration(self):
        # Look for class variable.
        with self._write_parsing_rule("classVarDec"):
            kind = self._expect_keyword(FIELD, STATIC)
            self._expect_variable_declaration(kind)

    def _expect_variable_declaration(self, kind):
        """
        :return: the number of vars declared
        """
        type = self._expect_type()
        identifier = self._expect_identifier()

        self._symbol_table.define_symbol(identifier, kind, type)
        var_cnt = 1
        # Handle multiple variable declaration.
        while not self._is_next_token(Symbol, ";"):
            var_cnt += 1
            self._expect_symbol(",")
            identifier = self._expect_identifier()
            self._symbol_table.define_symbol(identifier, kind, type)

        self._expect_symbol(";")
        return var_cnt

    def _expect_subroutine_declarations(self):
        # Look for subroutine prefix
        while self._is_next_token(Keyword, CONSTRUCTOR, FUNCTION, METHOD):
            self._process_single_subroutine_declaration()

    def _process_single_subroutine_declaration(self):

        with self._write_parsing_rule("subroutineDec"):
            self._expect_keyword(CONSTRUCTOR, FUNCTION, METHOD)

            if self._is_next_token(Keyword, VOID):
                self._expect_keyword(VOID)
            else:
                self._expect_type()

            identifier = self._expect_identifier()
            func_name = self._symbol_table.start_subroutine(identifier)
            self._expect_symbol("(")
            self._process_parameter_list()
            self._expect_symbol(")")
            self._process_subroutine_body(func_name)

    def _process_parameter_list(self):
        with self._write_parsing_rule("parameterList"):
            first_parameter = True
            while not self._is_next_token(Symbol, ")"):

                if first_parameter:
                    first_parameter = False
                else:
                    self._expect_symbol(",")

                type = self._expect_type()
                identifier = self._expect_identifier()
                self._symbol_table.define_symbol(identifier, SubroutineSymbolTable.ARGUMENT, type)

    def _process_subroutine_body(self, func_name):
        with self._write_parsing_rule("subroutineBody"):
            self._expect_symbol("{")
            num_of_vars = 0
            while self._is_next_token(Keyword, VAR):
                num_of_vars += self._process_var_declaration()
            self._vm_bytecode.write_function_declaration(func_name, num_of_vars)

            self._process_statements()
            self._expect_symbol("}")

    def _process_var_declaration(self):
        """
        :return: the number of vars declared
        """
        with self._write_parsing_rule("varDec"):
            self._expect_keyword(VAR)
            return self._expect_variable_declaration(SubroutineSymbolTable.VAR)

    def _process_statements(self):
        with self._write_parsing_rule("statements"):
            process_statements = True
            while process_statements:
                if self._is_next_token(Keyword, LET):
                    self._process_let_statement()

                elif self._is_next_token(Keyword, IF):
                    self._process_if_statement()

                elif self._is_next_token(Keyword, WHILE):
                    self._process_while_statement()

                elif self._is_next_token(Keyword, DO):
                    self._process_do_statement()

                elif self._is_next_token(Keyword, RETURN):
                    self._process_return_statement()

                else:
                    # No more statement to process.
                    process_statements = False

    def _process_let_statement(self):
        with self._write_parsing_rule("letStatement"):
            self._expect_keyword(LET)
            identifier = self._expect_identifier()
            symbol = self._symbol_table.get(identifier)
            # Handle array indexing
            if self._is_next_token(Symbol, "["):
                self._expect_symbol("[")
                self._process_expression()
                self._expect_symbol("]")
            self._expect_symbol("=")
            self._process_expression()
            self._expect_symbol(";")
            self._vm_bytecode.write_pop_symbol(symbol)

    def _process_if_statement(self):
        with self._write_parsing_rule("ifStatement"):
            self._expect_keyword(IF)
            self._expect_symbol("(")
            self._process_expression()
            self._expect_symbol(")")
            if_index = self._vm_bytecode.write_if_start()
            self._expect_symbol("{")
            self._process_statements()
            self._expect_symbol("}")
            self._vm_bytecode.write_else(if_index)
            if self._is_next_token(Keyword, ELSE):
                self._expect_keyword(ELSE)
                self._expect_symbol("{")
                self._process_statements()
                self._expect_symbol("}")
            self._vm_bytecode.write_if_end(if_index)

    def _process_while_statement(self):
        with self._write_parsing_rule("whileStatement"):
            self._expect_keyword(WHILE)
            while_index = self._vm_bytecode.write_while_declaration_start()
            self._expect_symbol("(")
            self._process_expression()
            self._expect_symbol(")")
            self._vm_bytecode.write_while_declaration_end(while_index)
            self._expect_symbol("{")
            self._process_statements()
            self._expect_symbol("}")
            self._vm_bytecode.write_while_end(while_index)


    def _process_do_statement(self):
        with self._write_parsing_rule("doStatement"):
            self._expect_keyword(DO)
            self._expect_subroutine_call()
            self._expect_symbol(";")
            self._vm_bytecode.write_pop('temp', 0)


    def _expect_subroutine_call(self):
        # From some reason the book state that subroutineCall is parsing rule
        # but in the example its not so, ..
        first_identifier = self._expect_identifier()

        if self._is_next_token(Symbol, "."):
            # class or variable invocation, else direct invocation of
            # method of this class.
            self._expect_symbol(".")
            second_identifier = self._expect_identifier()
            func_name = self._symbol_table.create_mangled_name(subroutine_name=second_identifier,
                                                               class_name=first_identifier)
        else:
            func_name = self._symbol_table.create_mangled_name(subroutine_name=first_identifier)

        self._expect_symbol("(")
        num_of_args = self._process_expression_list()
        self._vm_bytecode.write_method_call(func_name, num_of_args)
        self._expect_symbol(")")


    def _process_return_statement(self):
        with self._write_parsing_rule("returnStatement"):
            self._expect_keyword(RETURN)
            if not self._is_next_token(Symbol, ";"):
                self._process_expression()
            else:
                self._vm_bytecode.write_push('constant', 0)
            self._expect_symbol(";")
            self._vm_bytecode.write_return()

    def _process_expression(self):
        with self._write_parsing_rule("expression"):
            self._process_term()

            if self._is_next_token(Symbol, *OPS):
                op = self._expect_symbol(*OPS)
                self._process_term()
                self._vm_bytecode.write_binary_operation(op)


    def _process_expression_list(self):
        """
        :return: The number of expressions.
        """
        with self._write_parsing_rule("expressionList"):
            # need to overlook. but since expression list is always
            # surrounded by parenthesis we just check for )

            exp_cnt = 0
            while not self._is_next_token(Symbol, ")"):
                if exp_cnt:
                    self._expect_symbol(",")
                exp_cnt += 1
                self._process_expression()
        return exp_cnt

    def _process_term(self):
        with self._write_parsing_rule("term"):
            token = self._next_token()

            # Handle integer const
            if isinstance(token, Integer):
                self._vm_bytecode.write_push('constant', token.value)
                self._write_single_token(token)
                return

            # Handle String const
            elif isinstance(token, String):
                self._write_single_token(token)
                return

            # Handle Keyword const
            elif isinstance(token, Keyword):
                value = self._expect_keyword(TRUE, FALSE, NULL, THIS)
                self._vm_bytecode.write_builtin_value(value)
                return

            # Handle array indexing:
            elif self._is_next_array_indexing():
                self._expect_identifier()
                self._expect_symbol("[")
                self._process_expression()
                self._expect_symbol("]")

            # Handle subroutine call
            elif self._is_next_subroutine_call():
                self._expect_subroutine_call()

            # Handle variable
            elif isinstance(token, Identifier):
                identifier = self._expect_identifier()
                symbol = self._symbol_table.get(identifier)
                self._vm_bytecode.write_push_symbol(symbol)

            # Handle ( expression )
            elif self._is_next_token(Symbol, "("):
                self._expect_symbol("(")
                self._process_expression()
                self._expect_symbol(")")

            # Handle unaryOps - ~
            elif self._is_next_token(Symbol, *UNARY_OPS):
                op = self._expect_symbol(*UNARY_OPS)
                self._process_term()
                self._vm_bytecode.write_unary_operation(op)

            else:
                raise RuntimeError("Unexpected?")


    def _is_next_subroutine_call(self):
        """
        Look ahead and return True if the next expression is subroutine call.
        """
        # Check if there is more to read.
        if self.position + 1 < len(self._tokens):
            next_next_token = self._tokens[self.position + 1]
            return (self._is_next_token(Identifier) and
                    (self._is_token(next_next_token, Symbol, "(") or
                     self._is_token(next_next_token, Symbol, ".")))

    def _is_next_array_indexing(self):
        """
        Look ahead and return True if the next expression is array indexing.
        """
        # Check if there is more to read.
        if self.position + 1 < len(self._tokens):
            next_next_token = self._tokens[self.position + 1]
            return (self._is_next_token(Identifier) and
                    self._is_token(next_next_token, Symbol, "["))
