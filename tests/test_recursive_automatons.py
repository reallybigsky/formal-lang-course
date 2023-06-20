from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex

from project.ecfg import ECFG
from project.recursive_automaton import RecursiveAutomata


def test_recursive_automata():
    def check_automata_eq(actual: RecursiveAutomata, expected: RecursiveAutomata):
        assert set(actual.var_to_auto.keys()) == set(expected.var_to_auto.keys())
        for k in actual.var_to_auto.keys():
            assert actual.var_to_auto[k].is_equivalent_to(expected.var_to_auto[k])
        assert actual.start == expected.start

    check_automata_eq(
        RecursiveAutomata.from_ecfg(
            ECFG.from_text(
                """
                    S -> A B C
                    A -> a
                    B -> b
                    C -> c
                """
            )
        ),
        RecursiveAutomata(
            Variable("S"),
            {
                Variable("S"): Regex("A.B.C").to_epsilon_nfa(),
                Variable("A"): Regex("a").to_epsilon_nfa(),
                Variable("B"): Regex("b").to_epsilon_nfa(),
                Variable("C"): Regex("c").to_epsilon_nfa(),
            },
        ),
    )

    check_automata_eq(
        RecursiveAutomata.from_ecfg(
            ECFG.from_text(
                """
                    S -> a b c D
                    D -> E
                    E -> d
                """
            )
        ),
        RecursiveAutomata(
            Variable("S"),
            {
                Variable("S"): Regex("a.b.c.D").to_epsilon_nfa(),
                Variable("D"): Regex("E").to_epsilon_nfa(),
                Variable("E"): Regex("d").to_epsilon_nfa(),
            },
        ),
    )

    check_automata_eq(
        RecursiveAutomata.from_ecfg(
            ECFG.from_text(
                """
                    S -> A B
                    A -> a
                    B -> C
                    C -> c
                """
            )
        ),
        RecursiveAutomata(
            Variable("S"),
            {
                Variable("S"): Regex("A.B").to_epsilon_nfa(),
                Variable("A"): Regex("a").to_epsilon_nfa(),
                Variable("B"): Regex("C").to_epsilon_nfa(),
                Variable("C"): Regex("c").to_epsilon_nfa(),
            },
        ),
    )

    check_automata_eq(
        RecursiveAutomata.from_ecfg(
            ECFG.from_text(
                """
                    S -> A
                    A -> a
                    B -> b
                """
            )
        ),
        RecursiveAutomata(
            Variable("S"),
            {
                Variable("S"): Regex("A").to_epsilon_nfa(),
                Variable("A"): Regex("a").to_epsilon_nfa(),
                Variable("B"): Regex("b").to_epsilon_nfa(),
            },
        ),
    )

    check_automata_eq(
        RecursiveAutomata.from_ecfg(
            ECFG.from_text(
                """
                    S -> a b
                """
            )
        ),
        RecursiveAutomata(
            Variable("S"), {Variable("S"): Regex("a.b").to_epsilon_nfa()}
        ),
    )

    check_automata_eq(
        RecursiveAutomata.from_ecfg(
            ECFG.from_text(
                """
                    S -> S S | a b | $
                """
            )
        ),
        RecursiveAutomata(
            Variable("S"), {Variable("S"): Regex("(a.b)|(S.S)|$").to_epsilon_nfa()}
        ),
    )
