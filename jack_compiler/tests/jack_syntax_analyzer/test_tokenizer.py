import pytest

from jack_syntax_analyzer.tokenizer import strip_comments, tokenize, tokens_to_xml

from conftest import compare_xmls


comments_samples = dict()
comments_samples['simple_single_line'] = (
"""
// this is single line comment
foo = 1
// this is another
""",
"""
foo = 1
""")

comments_samples['simple_multi_line'] = (
"""
/**
 * This is multi line comment
 * =========================
 */
foo = 1
/**
 * This is multi line comment
 * =========================
 */
""",
"""

foo = 1

""")

comments_samples['inline_comment'] = (
"""
foo = 1// foo bar

""",
"""
foo = 1
""")

@pytest.mark.parametrize(("text_with_comments", "expected_result"),
                        comments_samples.values(),
                        ids=comments_samples.keys())
def test_strip_comments(text_with_comments, expected_result):
    assert strip_comments(text_with_comments) == expected_result



def test_tokenizer(sample_program_for_syntax_analyze):
    """
    Compare our tokens xml against all the samples provided.
    """
    jack_input = open(sample_program_for_syntax_analyze.jack).read()
    result_tokens = tokenize(jack_input)
    result_tokens_xml = tokens_to_xml(result_tokens)

    tokens_xml_content = open(sample_program_for_syntax_analyze.tokens_xml).read()
    compare_xmls(result_tokens_xml, tokens_xml_content)