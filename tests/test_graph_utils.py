import filecmp
import os
from project import graph_utils


def test_get_graph_info_by_name():
    def _inner_test_get_graph_info_by_name(
        name: str, nodes: int, edges: int, labels: set
    ):
        graph = graph_utils.get_graph_info_by_name(name)
        assert graph.nodes == nodes
        assert graph.edges == edges
        assert set(graph.labels_to_list()) == labels

    _inner_test_get_graph_info_by_name("pr", 815, 692, {"a", "d"})
    _inner_test_get_graph_info_by_name("ls", 1687, 1453, {"a", "d"})


def test_create_and_save_two_cycles_graph_as_pydot():
    graph_utils.create_and_save_two_cycles_graph_as_pydot(
        42, 29, labels=("a", "d"), path="tmp_two_cycles_graph_42_29"
    )
    assert filecmp.cmp(
        "tmp_two_cycles_graph_42_29",
        "./tests/test_graph_utils_two_cycles_graph_42_29_expected",
    )
    os.remove("tmp_two_cycles_graph_42_29")
