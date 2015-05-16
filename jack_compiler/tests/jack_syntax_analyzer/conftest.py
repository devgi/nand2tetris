import collections

import pytest
import py

sample_jack_programs_paths = list(py.path.local(__file__)
                                  .dirpath()
                                  .join("resources")
                                  .visit("*.jack"))

SampleProgram = collections.namedtuple("SampleProgram",
    ["jack", "tokens_xml", "ast_xml"])

@pytest.fixture(params=sample_jack_programs_paths, ids=sample_jack_programs_paths)
def sample_program(request):
    jack_program_path = request.param
    tokens_xml = jack_program_path.new(
        purebasename=jack_program_path.purebasename + "T", ext=".xml")
    ast_xml = jack_program_path.new(ext='.xml')

    assert jack_program_path.check(file=1)
    assert tokens_xml.check(file=1)
    assert ast_xml.check(file=1)
    return SampleProgram(jack=jack_program_path.strpath,
                         tokens_xml=tokens_xml.strpath,
                         ast_xml=ast_xml.strpath)



def compare_xmls(result_xml, expected_xml):
    assert result_xml == expected_xml