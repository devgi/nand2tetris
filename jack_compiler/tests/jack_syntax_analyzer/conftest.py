import collections

import pytest
import py

resource_path = py.path.local(__file__).dirpath().join("resources")

sample_jack_programs_for_syntax_analyze = list(resource_path.join("syntax_analyzer")
                                  .visit("*.jack"))

SampleSyntaxAnalyzeProgram = collections.namedtuple("SampleProgram",
    ["jack", "tokens_xml", "ast_xml"])

@pytest.fixture(params=sample_jack_programs_for_syntax_analyze,
                ids=sample_jack_programs_for_syntax_analyze)
def sample_program_for_syntax_analyze(request):
    jack_program_path = request.param
    tokens_xml = jack_program_path.new(
        purebasename=jack_program_path.purebasename + "T", ext=".xml")
    ast_xml = jack_program_path.new(ext='.xml')

    assert jack_program_path.check(file=1)
    assert tokens_xml.check(file=1)
    assert ast_xml.check(file=1)
    return SampleSyntaxAnalyzeProgram(jack=jack_program_path.strpath,
                         tokens_xml=tokens_xml.strpath,
                         ast_xml=ast_xml.strpath)



def compare_xmls(result_xml, expected_xml):
    assert result_xml == expected_xml


sample_jack_programs_to_compile = resource_path.join("compiler").listdir()

@pytest.fixture(params=sample_jack_programs_to_compile,
                ids=sample_jack_programs_to_compile)
def directory_to_compile(request):
    return request.param