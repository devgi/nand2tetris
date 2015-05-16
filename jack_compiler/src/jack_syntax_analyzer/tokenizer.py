import re

from xml.sax.saxutils import escape
from jack_syntax_analyzer.consts import KEYWORDS, SYMBOLS

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return self.to_xml()

    def to_xml(self):
        return "<{type}> {value} </{type}>".format(type=self.type,
                                                   value=escape(self.value))

class Keyword(Token):
    def __init__(self, value):
        assert value in KEYWORDS
        super(Keyword, self).__init__(type="keyword", value=value)

class Symbol(Token):
    def __init__(self, value):
        assert value in SYMBOLS
        super(Symbol, self).__init__(type='symbol', value=value)

class Integer(Token):
    def __init__(self, value):
        assert 0 <= int(value) <= (2**15 - 1)
        super(Integer, self).__init__(type='integerConstant',
                                      value=value)

class String(Token):
    def __init__(self, value):
        assert value[0] == '"' and value[-1] == '"'
        value = value[1:-1]
        super(String, self).__init__(type='stringConstant',
                                     value=value)

class Identifier(Token):
    def __init__(self, value):
        super(Identifier, self).__init__(type="identifier",
                                         value=value)



SINGLE_LINE_COMMENT = re.compile(r'//[^\n]*\n')
MULTI_LINE_COMMENT = re.compile(r'/\*(.*?)\*/',  re.MULTILINE|re.DOTALL)

def strip_comments(jack_file_content):
    """
    Strip comments from files.
    We should handle two types of comments: single line comments (starts wth
    "//") and multiline comments (starts with "/*")
    :param line:
    :return:
    """
    content_no_comments = SINGLE_LINE_COMMENT.sub("", jack_file_content)
    content_no_comments = MULTI_LINE_COMMENT.sub("", content_no_comments)
    return content_no_comments

KEYWORD_PATTERN = "|".join(KEYWORDS)
SYMBOL_PATTERN = "|".join(re.escape(symbol) for symbol in SYMBOLS)
INTEGER_PATTERN = "\d+"
# No new line or "
STRING_PATTERN = r"\"[^\"\n]*\""
ID_PATTERN = "[a-zA-Z_][a-zA-Z_0-9]*"
TOKEN_PATTERN = "|".join([KEYWORD_PATTERN, SYMBOL_PATTERN, INTEGER_PATTERN, STRING_PATTERN, ID_PATTERN])

# Compile relevant regular expressions.
INTEGER_RE = re.compile(INTEGER_PATTERN)
STRING_RE = re.compile(STRING_PATTERN)
ID_RE = re.compile(ID_PATTERN)
TOKEN_RE = re.compile(TOKEN_PATTERN)


def tokenize(jack_file_content):
    """
    Split jack file into list of tokens.
    :param jack_file_content: The content of the file.
    :return: List of Token instances.
    """
    tokens = []
    for line in strip_comments(jack_file_content).splitlines():
        tokens.extend(tokenize_line(line))
    return tokens

def tokenize_line(jack_line_no_comment):
    """
    Split line into tokens and yield them one by one.
    :param jack_line_no_comment: Line without comments to process.
    :return: generator that yields token instances.
    """
    # Split the line by the token regex and see if we catch
    # anything that is not spaces. if we do, its illegal expression.
    for leftover in TOKEN_RE.split(jack_line_no_comment):
        if leftover.strip():
            raise RuntimeError("Unexpected token: %s" % leftover)

    for token in TOKEN_RE.findall(jack_line_no_comment):
        if token in KEYWORDS:
            yield Keyword(value=token)

        elif token in SYMBOLS:
            yield Symbol(value=token)

        elif INTEGER_RE.match(token):
            yield Integer(value=token)

        elif STRING_RE.match(token):
            yield String(value=token)

        elif ID_RE.match(token):
            yield Identifier(value=token)

        else:
            # this never should happen since the token re covers
            # exactly all the cases.
            raise RuntimeError("Unexpected token: %s" % token)

def tokens_to_xml(tokens):
    """
    Export all the tokens to xml string.
    :param tokens: List of Token instances.
    :return: the tokens formatted in xml.
    """
    xml = "<tokens>\n"

    # The expected xml contains no indentation
    for token in tokens:
        xml += token.to_xml() + "\n"

    # The expected xml ends with new line.
    xml += "</tokens>\n"
    return xml