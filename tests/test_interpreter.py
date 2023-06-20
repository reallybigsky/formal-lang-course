from project.graphs import get_nx_graph_by_name
from project.language.FL_utils import parse
from project.finite_automaton import graph_to_nfa, regex_to_min_dfa
from project.language.interpreter import interpret
from project.regular_path_queries import nfa_iterator
from test_utils import interpret_to_str


def test_empty_program():
    assert interpret_to_str(parse("")) == ""
    assert interpret_to_str(parse("// just a comment")) == ""


def test_very_simple_print_program():
    actual = interpret_to_str(parse("""
                                        hello := \"world\";
                                        print hello;
                                    """))
    expected = "world\n"
    assert actual == expected


def test_literals():
    actual = interpret(parse("\"hello\"", "expr"))
    expected = "hello"
    assert actual.value == expected

    actual = interpret(parse("1", "expr"))
    expected = 1
    assert actual.value == expected

    actual = interpret(parse("{1}", "expr"))
    expected = {1}
    assert actual.value == expected

    actual = interpret(parse("{1,2,3}", "expr"))
    expected = {1, 2, 3}
    assert actual.value == expected

    actual = interpret(parse("{1,2,3, \"hello\"}", "expr"))
    expected = {1, 2, 3, "hello"}
    assert actual.value == expected

    actual = interpret(parse("{}", "expr"))
    expected = {}
    assert actual.value == expected

    actual = interpret(parse("{\t\t\t\t\n\n\n\t}", "expr"))
    expected = {}
    assert actual.value == expected


def test_interpret():
    interpret(parse("lam := map (lambda (s) -> { s }, g);"))
    interpret(parse("lam := filter (lambda (s) -> { s }, g);"))


def test_load():
    actual = interpret(parse("load \"pizza\";", "expr"))
    expected = graph_to_nfa(get_nx_graph_by_name("pizza"))
    assert actual.value == expected


def test_get_start():
    actual = interpret(parse("get_start \"a\";", "expr"))
    expected = {"0"}
    assert actual.value == expected

    actual = interpret(parse("get_start(\"a*\");", "expr"))
    expected = {"0;1;2;1;2;3"}
    assert actual.value == expected


def test_get_final():
    actual = interpret(parse("get_final \"a\";", "expr"))
    expected = {"1"}
    assert actual.value == expected

    actual = interpret(parse("get_final \"a*\";", "expr"))
    expected = {"0;1;2;1;2;3"}
    assert actual.value == expected


def test_set_start():
    actual = interpret(parse("set_start(\"a\", {322});", "expr"))
    expected = regex_to_min_dfa("a")
    expected.start_states.clear()
    expected.add_start_state(322)
    assert actual.value == expected


def test_set_final():
    actual = interpret(parse("set_final(\"a\", {322});", "expr"))
    expected = regex_to_min_dfa("a")
    expected.final_states.clear()
    expected.add_final_state(322)
    assert actual.value == expected


def test_add_start():
    actual = interpret(parse("add_start(\"a\", {322});", "expr"))
    expected = regex_to_min_dfa("a")
    expected.add_start_state(322)
    assert actual.value == expected


def test_add_final():
    actual = interpret(parse("add_final(\"a\", {322});", "expr"))
    expected = regex_to_min_dfa("a")
    expected.add_final_state(322)
    assert actual.value == expected


def test_get_reachable():
    actual = interpret(parse("get_reachable(\"a\");", "expr"))
    expected = regex_to_min_dfa("a")
    assert actual.value == expected._get_reachable_states()


def test_get_vertices():
    actual = interpret(parse("get_vertices(\"a\");", "expr"))
    expected = regex_to_min_dfa("a")
    assert actual.value == expected.states


def test_get_edges():
    actual = interpret(parse("get_edges(\"a\");", "expr"))
    expected = regex_to_min_dfa("a")
    expected_transitions = {(u, l, v) for u, l, v in nfa_iterator(expected)}
    assert actual.value == expected_transitions


def test_get_labels():
    actual = interpret(parse("get_labels(\"a\");", "expr"))
    expected = regex_to_min_dfa("a")
    expected_labels = expected.symbols
    assert actual.value == expected_labels


def test_equals():
    actual = interpret(parse("1 == 1", "expr"))
    assert actual.value
    actual = interpret(parse("\"a\" == \"a\"", "expr"))
    assert actual.value
    actual = interpret(parse("{0,1} == {1,0}", "expr"))
    assert actual.value


def test_not_equals():
    actual = interpret(parse("1 != 1", "expr"))
    assert not actual.value
    actual = interpret(parse("\"a\" != \"a\"", "expr"))
    assert not actual.value
    actual = interpret(parse("{0,1} != {1,0}", "expr"))
    assert not actual.value


def test_in():
    actual = interpret(parse("1 in {1,0}", "expr"))
    assert actual.value
    actual = interpret(parse("0 in {1,0}", "expr"))
    assert actual.value
    actual = interpret(parse("\"1\" in {1,0}", "expr"))
    assert not actual.value
    actual = interpret(parse("\"1\" in {\"1\",\"0\"}", "expr"))
    assert actual.value
    actual = interpret(parse("2 in {1,0}", "expr"))
    assert not actual.value


def test_concat_and_intersect_NFA():
    interpret(parse('load("pizza") && load("wc")', "expr"))
    interpret(parse('load("pizza") || load("wc")', "expr"))
    interpret(parse('load("pizza") != load("wc")', "expr"))
    interpret(parse('load("pizza") != load("pizza")', "expr"))


def test_concat_and_intersect_set():
    actual = interpret(parse('{1} && {2}', "expr"))
    expected = set()
    assert actual.value == expected
    actual = interpret(parse('{1} || {2}', "expr"))
    expected = {1, 2}
    assert actual.value == expected


def test_concat_intersect_string():
    actual = interpret(parse('"12" && "23"', "expr"))
    expected = "2"
    assert actual.value == expected
    actual = interpret(parse('"12" || "23"', "expr"))
    expected = "1223"
    assert actual.value == expected
