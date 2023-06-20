import pydot

from project.language.FL_utils import program_to_dot
from test_utils import deep_compare, dot_from_string


testdata = [
    (
        "// simple comment \n",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
            }
        """
        ),
    ),
    (
        "print 1;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[print]"];
                2 -> 3;
                4 [label="print"];
                3 -> 4;
                5 [label="Rule[expr]"];
                3 -> 5;
                6 [label="Rule[val]"];
                5 -> 6;
                7 [label="1"];
                6 -> 7;
                8 [label=";"];
                1 -> 8;
            }
        """
        ),
    ),
    (
        "n := 1;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="n"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="Rule[val]"];
                6 -> 7;
                8 [label="1"];
                7 -> 8;
                9 [label=";"];
                1 -> 9;
            }
        """
        ),
    ),
    (
        'string := "str";',
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="string"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="Rule[val]"];
                6 -> 7;
                8 [label="str"];
                7 -> 8;
                9 [label=";"];
                1 -> 9;
            }
        """
        ),
    ),
    (
        "l := lambda (s) -> {s || s};",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="l"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="Rule[lambda]"];
                6 -> 7;
                8 [label="lambda"];
                7 -> 8;
                9 [label="("];
                7 -> 9;
                10 [label="Rule[val]"];
                7 -> 10;
                11 [label="s"];
                10 -> 11;
                12 [label=")"];
                7 -> 12;
                13 [label="->"];
                7 -> 13;
                14 [label="{"];
                7 -> 14;
                15 [label="Rule[expr]"];
                7 -> 15;
                16 [label="Rule[expr]"];
                15 -> 16;
                17 [label="s"];
                16 -> 17;
                18 [label="||"];
                15 -> 18;
                19 [label="Rule[expr]"];
                15 -> 19;
                20 [label="s"];
                19 -> 20;
                21 [label="}"];
                7 -> 21;
                22 [label=";"];
                1 -> 22;
            }
        """
        ),
    ),
    (
        'l := lambda ("") -> {"test"};',
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="l"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="Rule[lambda]"];
                6 -> 7;
                8 [label="lambda"];
                7 -> 8;
                9 [label="("];
                7 -> 9;
                10 [label="Rule[val]"];
                7 -> 10;
                11 [label=""];
                10 -> 11;
                12 [label=")"];
                7 -> 12;
                13 [label="->"];
                7 -> 13;
                14 [label="{"];
                7 -> 14;
                15 [label="Rule[expr]"];
                7 -> 15;
                16 [label="Rule[val]"];
                15 -> 16;
                17 [label="test"];
                16 -> 17;
                18 [label="}"];
                7 -> 18;
                19 [label=";"];
                1 -> 19;
            }
        """
        ),
    ),
    (
        "nodes := set_start (graph, {1, 2, 3});",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="nodes"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="set_start"];
                6 -> 7;
                8 [label="("];
                6 -> 8;
                9 [label="Rule[expr]"];
                6 -> 9;
                10 [label="graph"];
                9 -> 10;
                11 [label=","];
                6 -> 11;
                12 [label="Rule[expr]"];
                6 -> 12;
                13 [label="Rule[val]"];
                12 -> 13;
                14 [label="Rule[set]"];
                13 -> 14;
                15 [label="{"];
                14 -> 15;
                16 [label="Rule[expr]"];
                14 -> 16;
                17 [label="Rule[val]"];
                16 -> 17;
                18 [label="1"];
                17 -> 18;
                19 [label=","];
                14 -> 19;
                20 [label="Rule[expr]"];
                14 -> 20;
                21 [label="Rule[val]"];
                20 -> 21;
                22 [label="2"];
                21 -> 22;
                23 [label=","];
                14 -> 23;
                24 [label="Rule[expr]"];
                14 -> 24;
                25 [label="Rule[val]"];
                24 -> 25;
                26 [label="3"];
                25 -> 26;
                27 [label="}"];
                14 -> 27;
                28 [label=")"];
                6 -> 28;
                29 [label=";"];
                1 -> 29;
            }
        """
        ),
    ),
    (
        "nodes := get_start graph;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="nodes"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="get_start"];
                6 -> 7;
                8 [label="Rule[expr]"];
                6 -> 8;
                9 [label="graph"];
                8 -> 9;
                10 [label=";"];
                1 -> 10;
            }
        """
        ),
    ),
    (
        "nodes := filter (lambda (a) -> {a == 1}, graph);",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="nodes"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="filter"];
                6 -> 7;
                8 [label="("];
                6 -> 8;
                9 [label="Rule[lambda]"];
                6 -> 9;
                10 [label="lambda"];
                9 -> 10;
                11 [label="("];
                9 -> 11;
                12 [label="Rule[val]"];
                9 -> 12;
                13 [label="a"];
                12 -> 13;
                14 [label=")"];
                9 -> 14;
                15 [label="->"];
                9 -> 15;
                16 [label="{"];
                9 -> 16;
                17 [label="Rule[expr]"];
                9 -> 17;
                18 [label="Rule[expr]"];
                17 -> 18;
                19 [label="a"];
                18 -> 19;
                20 [label="=="];
                17 -> 20;
                21 [label="Rule[expr]"];
                17 -> 21;
                22 [label="Rule[val]"];
                21 -> 22;
                23 [label="1"];
                22 -> 23;
                24 [label="}"];
                9 -> 24;
                25 [label=","];
                6 -> 25;
                26 [label="Rule[expr]"];
                6 -> 26;
                27 [label="graph"];
                26 -> 27;
                28 [label=")"];
                6 -> 28;
                29 [label=";"];
                1 -> 29;
            }
        """
        ),
    ),
    (
        'reg := "regex*";',
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="reg"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="Rule[val]"];
                6 -> 7;
                8 [label="regex*"];
                7 -> 8;
                9 [label=";"];
                1 -> 9;
            }
        """
        ),
    ),
    (
        "lang := a && b;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="lang"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="Rule[expr]"];
                6 -> 7;
                8 [label="a"];
                7 -> 8;
                9 [label="&&"];
                6 -> 9;
                10 [label="Rule[expr]"];
                6 -> 10;
                11 [label="b"];
                10 -> 11;
                12 [label=";"];
                1 -> 12;
            }
        """
        ),
    ),
    (
        "logic := a in graph;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="logic"];
                3 -> 4;
                5 [label=":="];
                3 -> 5;
                6 [label="Rule[expr]"];
                3 -> 6;
                7 [label="Rule[expr]"];
                6 -> 7;
                8 [label="a"];
                7 -> 8;
                9 [label="in"];
                6 -> 9;
                10 [label="Rule[expr]"];
                6 -> 10;
                11 [label="graph"];
                10 -> 11;
                12 [label=";"];
                1 -> 12;
            }
        """
        ),
    ),
]


def test_FL_parser():
    def compare_programs(actual: str, expected: pydot.Dot):
        assert deep_compare(program_to_dot(actual), expected)

    for [act, exp] in testdata:
        compare_programs(act, exp)
