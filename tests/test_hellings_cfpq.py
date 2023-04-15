from typing import Set

from pyformlang.cfg import CFG
from networkx import MultiDiGraph
from project.context_free_grammar import context_free_path_query
from tests.test_utils import create_graph


def test_context_free_path_query():
    def check_cfpq(txt: str, graph: MultiDiGraph, expected: Set):
        actual = context_free_path_query(cfg=CFG.from_text(txt), graph=graph)
        assert actual == expected

    check_cfpq(
        """
                S -> A B
                A -> a
                B -> b
            """,
        create_graph(nodes=[0, 1, 2], edges=[(0, "a", 1), (1, "b", 2)]),
        {(0, 2)},
    )

    check_cfpq(
        """
                S -> $
            """,
        create_graph(nodes=[0, 1], edges=[(0, "a", 1), (1, "b", 0)]),
        {(0, 0), (1, 1)},
    )

    check_cfpq(
        """
                S -> A B C
                A -> a
                B -> b
                C -> c
            """,
        create_graph(nodes=[0, 1, 2, 3], edges=[(0, "a", 1), (1, "b", 2), (2, "c", 3)]),
        {(0, 3)},
    )

    check_cfpq(
        """
                S -> A B C | S S | s
                A -> a
                B -> b
                C -> c
            """,
        create_graph(
            nodes=[0, 1, 2, 3],
            edges=[(0, "s", 0), (0, "a", 1), (1, "b", 2), (2, "c", 3)],
        ),
        {(0, 3), (0, 0)},
    )

    check_cfpq(
        """
                S -> A B | S S
                A -> a | $
                B -> b
            """,
        create_graph(
            nodes=[0, 1, 2, 3, 4],
            edges=[(0, "a", 1), (1, "b", 2), (2, "a", 3), (3, "b", 4)],
        ),
        {(0, 4), (2, 4), (1, 2), (3, 4), (1, 4), (0, 2)},
    )
