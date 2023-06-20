from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from project import graphs, finite_automaton
from regexs_data import sources


def test_regex_to_min_dfa():
    mdfa = finite_automaton.regex_to_min_dfa("e*((13)|(37)).boi")
    dfa = DeterministicFiniteAutomaton()
    dfa.add_start_state(0)
    dfa.add_final_state(2)
    dfa.add_transition(0, "e", 0)
    dfa.add_transition(0, "13", 1)
    dfa.add_transition(0, "37", 1)
    dfa.add_transition(1, "boi", 2)

    assert mdfa.is_equivalent_to(dfa)


def test_regex_to_min_dfa_on_complex_data():
    def helper_test_on_regexs_data(rx: str, source_name: str):
        dfa = finite_automaton.regex_to_min_dfa(rx)
        regex = Regex(rx)

        for word in sources[source_name]["good"]:
            assert regex.accepts(word) and regex.accepts(word) == dfa.accepts(word)

        for word in sources[source_name]["bad"]:
            assert not regex.accepts(word) and regex.accepts(word) == dfa.accepts(word)

    union = "|".join(sources["union_test"]["source"])
    helper_test_on_regexs_data(union, "union_test")

    concat = ".".join(sources["concat_test"]["source"])
    helper_test_on_regexs_data(concat, "concat_test")

    combo = ".".join(sources["combo_test"]["source"])
    helper_test_on_regexs_data(combo, "combo_test")


def test_graph_to_nfa():
    def helper_test_fa_on_cfpq_data(name: str):
        graph = graphs.get_nx_graph_by_name(name)
        nfa = finite_automaton.graph_to_nfa(graph)

        assert graph.number_of_nodes() == len(nfa.start_states)
        assert graph.number_of_nodes() == len(nfa.final_states)
        assert graph.number_of_edges() == nfa.get_number_transitions()

        for _, _, d in graph.edges(data=True):
            label = d.get("label")
            assert nfa.accepts([label])

    def helper_two_cycles_graph():
        tsg = graphs.create_two_cycles_graph(3, 6, ["a", "b"])
        nfa = finite_automaton.graph_to_nfa(tsg, {0}, {0})
        dfa = finite_automaton.regex_to_min_dfa("(a a a a|b b b b b b b)*")

        assert dfa.is_equivalent_to(nfa)

    helper_two_cycles_graph()
    helper_test_fa_on_cfpq_data("people")
    helper_test_fa_on_cfpq_data("pizza")
