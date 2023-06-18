import pydot

from project.language.FL_utils import FL_prog_to_dot
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
                7 [label="Rule[integer]"];
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
        "n := 1;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="n"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[val]"];
                7 -> 8;
                9 [label="Rule[integer]"];
                8 -> 9;
                10 [label="1"];
                9 -> 10;
                11 [label=";"];
                1 -> 11;
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
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="string"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[val]"];
                7 -> 8;
                9 [label="Rule[string]"];
                8 -> 9;
                10 [label="str"];
                9 -> 10;
                11 [label=";"];
                1 -> 11;
            }
        """
        ),
    ),
    (
        "l := (lambda {s} -> s . s);",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="l"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[lambda]"];
                7 -> 8;
                9 [label="("];
                8 -> 9;
                10 [label="lambda"];
                8 -> 10;
                11 [label="Rule[list]"];
                8 -> 11;
                12 [label="{"];
                11 -> 12;
                13 [label="Rule[item]"];
                11 -> 13;
                14 [label="Rule[var]"];
                13 -> 14;
                15 [label="s"];
                14 -> 15;
                16 [label="}"];
                11 -> 16;
                17 [label="->"];
                8 -> 17;
                18 [label="Rule[expr]"];
                8 -> 18;
                19 [label="Rule[concat]"];
                18 -> 19;
                20 [label="Rule[bin_arg_l]"];
                19 -> 20;
                21 [label="Rule[var]"];
                20 -> 21;
                22 [label="s"];
                21 -> 22;
                23 [label="."];
                19 -> 23;
                24 [label="Rule[bin_arg_r]"];
                19 -> 24;
                25 [label="Rule[var]"];
                24 -> 25;
                26 [label="s"];
                25 -> 26;
                27 [label=")"];
                8 -> 27;
                28 [label=";"];
                1 -> 28;
            }
        """
        ),
    ),
    (
        'l := (lambda {} -> "test");',
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="l"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[lambda]"];
                7 -> 8;
                9 [label="("];
                8 -> 9;
                10 [label="lambda"];
                8 -> 10;
                11 [label="Rule[list]"];
                8 -> 11;
                12 [label="{"];
                11 -> 12;
                13 [label="}"];
                11 -> 13;
                14 [label="->"];
                8 -> 14;
                15 [label="Rule[expr]"];
                8 -> 15;
                16 [label="Rule[val]"];
                15 -> 16;
                17 [label="Rule[string]"];
                16 -> 17;
                18 [label="test"];
                17 -> 18;
                19 [label=")"];
                8 -> 19;
                20 [label=";"];
                1 -> 20;
            }
        """
        ),
    ),
    (
        "nodes := set_start of graph to {1, 2, 3};",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="nodes"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[set_start]"];
                7 -> 8;
                9 [label="set_start"];
                8 -> 9;
                10 [label="of"];
                8 -> 10;
                11 [label="Rule[source]"];
                8 -> 11;
                12 [label="Rule[var]"];
                11 -> 12;
                13 [label="graph"];
                12 -> 13;
                14 [label="to"];
                8 -> 14;
                15 [label="Rule[target]"];
                8 -> 15;
                16 [label="Rule[list]"];
                15 -> 16;
                17 [label="{"];
                16 -> 17;
                18 [label="Rule[item]"];
                16 -> 18;
                19 [label="Rule[integer]"];
                18 -> 19;
                20 [label="1"];
                19 -> 20;
                21 [label=","];
                16 -> 21;
                22 [label="Rule[item]"];
                16 -> 22;
                23 [label="Rule[integer]"];
                22 -> 23;
                24 [label="2"];
                23 -> 24;
                25 [label=","];
                16 -> 25;
                26 [label="Rule[item]"];
                16 -> 26;
                27 [label="Rule[integer]"];
                26 -> 27;
                28 [label="3"];
                27 -> 28;
                29 [label="}"];
                16 -> 29;
                30 [label=";"];
                1 -> 30;
            }
        """
        ),
    ),
    (
        "nodes := get_start of graph;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="nodes"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[get_start]"];
                7 -> 8;
                9 [label="get_start"];
                8 -> 9;
                10 [label="of"];
                8 -> 10;
                11 [label="Rule[target]"];
                8 -> 11;
                12 [label="Rule[var]"];
                11 -> 12;
                13 [label="graph"];
                12 -> 13;
                14 [label=";"];
                1 -> 14;
            }
        """
        ),
    ),
    (
        "nodes := filter (lambda {a} -> a == 1) : graph;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="nodes"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[filter]"];
                7 -> 8;
                9 [label="filter"];
                8 -> 9;
                10 [label="Rule[lambda]"];
                8 -> 10;
                11 [label="("];
                10 -> 11;
                12 [label="lambda"];
                10 -> 12;
                13 [label="Rule[list]"];
                10 -> 13;
                14 [label="{"];
                13 -> 14;
                15 [label="Rule[item]"];
                13 -> 15;
                16 [label="Rule[var]"];
                15 -> 16;
                17 [label="a"];
                16 -> 17;
                18 [label="}"];
                13 -> 18;
                19 [label="->"];
                10 -> 19;
                20 [label="Rule[expr]"];
                10 -> 20;
                21 [label="Rule[equal]"];
                20 -> 21;
                22 [label="Rule[bin_eq_arg_l]"];
                21 -> 22;
                23 [label="Rule[var]"];
                22 -> 23;
                24 [label="a"];
                23 -> 24;
                25 [label="=="];
                21 -> 25;
                26 [label="Rule[bin_eq_arg_r]"];
                21 -> 26;
                27 [label="Rule[val]"];
                26 -> 27;
                28 [label="Rule[integer]"];
                27 -> 28;
                29 [label="1"];
                28 -> 29;
                30 [label=")"];
                10 -> 30;
                31 [label=":"];
                8 -> 31;
                32 [label="Rule[iterable]"];
                8 -> 32;
                33 [label="Rule[var]"];
                32 -> 33;
                34 [label="graph"];
                33 -> 34;
                35 [label=";"];
                1 -> 35;
            }
        """
        ),
    ),
    (
        'reg := "regex"*;',
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="reg"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[kleene]"];
                7 -> 8;
                9 [label="Rule[bin_arg_l]"];
                8 -> 9;
                10 [label="Rule[string]"];
                9 -> 10;
                11 [label="regex"];
                10 -> 11;
                12 [label="*"];
                8 -> 12;
                13 [label=";"];
                1 -> 13;
            }
        """
        ),
    ),
    (
        "lang := a & b;",
        dot_from_string(
            """
            digraph "FL program" {
                1 [label="Rule[program]"];
                2 [label="Rule[stmt]"];
                1 -> 2;
                3 [label="Rule[bind]"];
                2 -> 3;
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="lang"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[intersect]"];
                7 -> 8;
                9 [label="Rule[bin_arg_l]"];
                8 -> 9;
                10 [label="Rule[var]"];
                9 -> 10;
                11 [label="a"];
                10 -> 11;
                12 [label="&"];
                8 -> 12;
                13 [label="Rule[bin_arg_r]"];
                8 -> 13;
                14 [label="Rule[var]"];
                13 -> 14;
                15 [label="b"];
                14 -> 15;
                16 [label=";"];
                1 -> 16;
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
                4 [label="Rule[var]"];
                3 -> 4;
                5 [label="logic"];
                4 -> 5;
                6 [label=":="];
                3 -> 6;
                7 [label="Rule[expr]"];
                3 -> 7;
                8 [label="Rule[in]"];
                7 -> 8;
                9 [label="Rule[bin_in_arg_l]"];
                8 -> 9;
                10 [label="Rule[var]"];
                9 -> 10;
                11 [label="a"];
                10 -> 11;
                12 [label="in"];
                8 -> 12;
                13 [label="Rule[bin_in_arg_r]"];
                8 -> 13;
                14 [label="Rule[var]"];
                13 -> 14;
                15 [label="graph"];
                14 -> 15;
                16 [label=";"];
                1 -> 16;
            }
        """
        ),
    ),
]


def test_FL_parser():
    def compare_programs(actual: str, expected: pydot.Dot):
        assert deep_compare(FL_prog_to_dot(actual), expected)

    for [act, exp] in testdata:
        compare_programs(act, exp)
