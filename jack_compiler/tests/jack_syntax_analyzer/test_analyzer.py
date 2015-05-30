from jack_syntax_analyzer.analyzer import JackCompiler

from conftest import compare_xmls


def test_analyzer(sample_program):
    jack_input = open(sample_program.jack).read()

    result_ast_xml, _ = JackCompiler().analyze(jack_input)
    expected_ast_xml_content = open(sample_program.ast_xml).read()
    compare_xmls(result_ast_xml, expected_ast_xml_content)