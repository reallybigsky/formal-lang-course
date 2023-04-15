from pyformlang.cfg import Variable
from pyformlang.finite_automaton import EpsilonNFA
from typing import Dict

from project.ecfg import ECFG
from project.regular_path_queries import enfa_to_boolean_decomposition


class RecursiveAutomata:
    def __init__(self, start: Variable, var_to_auto: Dict[Variable, EpsilonNFA]):
        self.start = start
        self.var_to_auto = var_to_auto

    def minimize(self) -> "RecursiveAutomata":
        """
        Get minimized recursive automata
        """
        return RecursiveAutomata(
            self.start, {v: nfa.minimize() for v, nfa in self.var_to_auto.items()}
        )

    def to_boolean_dcmps(self):
        """
        Get boolean decomposition from current recursive automata
        :return: BooleanDecomposition
        """
        decompositions = {}
        for key, value in self.var_to_auto.items():
            decompositions[key] = enfa_to_boolean_decomposition(value)
        return decompositions

    @classmethod
    def from_ecfg(cls, ecfg: ECFG) -> "RecursiveAutomata":
        """
        Convert ecfg to recursive automata
        :param ecfg: ecfg
        :return: recursive automata
        """
        return RecursiveAutomata(
            ecfg.start,
            {v: regex.to_epsilon_nfa() for v, regex in ecfg.productions.items()},
        )
