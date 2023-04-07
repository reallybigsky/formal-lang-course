from tempfile import NamedTemporaryFile
from textwrap import dedent

from pyformlang.cfg import Variable
from pyformlang.regular_expression import Regex

from project.ecfg import ECFG


def test_ecfg_from_pyformlang_cfg():
    def check_ecfg_eq(text: str, expected: ECFG):
        with NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(dedent(text))
            path = f.name

        actual = ECFG.from_file(path)

        assert set(actual.productions.keys()) == set(expected.productions.keys())
        for k in actual.productions.keys():
            assert (
                actual.productions[k]
                .to_epsilon_nfa()
                .is_equivalent_to(expected.productions[k].to_epsilon_nfa())
            )
        assert actual.start == expected.start

    check_ecfg_eq(
        """
            S -> A B C
            A -> a
            B -> b
            C -> c
        """,
        ECFG(
            Variable("S"),
            {
                Variable("S"): Regex("A.B.C"),
                Variable("A"): Regex("a"),
                Variable("B"): Regex("b"),
                Variable("C"): Regex("c"),
            },
        ),
    )

    check_ecfg_eq(
        """
            S -> a b c D
            D -> E
            E -> d
        """,
        ECFG(
            Variable("S"),
            {
                Variable("S"): Regex("a.b.c.D"),
                Variable("D"): Regex("E"),
                Variable("E"): Regex("d"),
            },
        ),
    )

    check_ecfg_eq(
        """
            S -> A B
            A -> a
            B -> C
            C -> c
        """,
        ECFG(
            Variable("S"),
            {
                Variable("S"): Regex("A.B"),
                Variable("A"): Regex("a"),
                Variable("B"): Regex("C"),
                Variable("C"): Regex("c"),
            },
        ),
    )

    check_ecfg_eq(
        """
            S -> A
            A -> a
            B -> b
        """,
        ECFG(
            Variable("S"),
            {
                Variable("S"): Regex("A"),
                Variable("A"): Regex("a"),
                Variable("B"): Regex("b"),
            },
        ),
    )

    check_ecfg_eq(
        """
            S -> a b
        """,
        ECFG(Variable("S"), {Variable("S"): Regex("a.b")}),
    )

    check_ecfg_eq(
        """
            S -> S S | a b | $
        """,
        ECFG(Variable("S"), {Variable("S"): Regex("(S.S)|(a.b)|$")}),
    )
