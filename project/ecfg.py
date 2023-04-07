from pyformlang.cfg import Variable, CFG
from pyformlang.regular_expression import Regex
from typing import Dict


class ECFG:
    """
    Extended context free grammar
    """
    def __init__(self, start: Variable, productions: Dict[Variable, Regex]):
        self.start = start
        self.productions = productions

    @classmethod
    def from_pyformlang_cfg(cls, cfg: CFG) -> "ECFG":
        """
        Get ECFG from pyformlang CFG
        """
        start = cfg.start_symbol
        productions = dict()
        for prod in cfg.productions:
            body = Regex(".".join(symbol.value for symbol in prod.body) if len(prod.body) > 0 else "$")
            if prod.head not in productions:
                productions[prod.head] = body
            else:
                productions[prod.head] = productions[prod.head].union(body)
        return ECFG(start, productions)

    @classmethod
    def from_text(cls, text: str) -> "ECFG":
        """
        Get ECFG from text
        """
        return cls.from_pyformlang_cfg(CFG.from_text(text))

    @classmethod
    def from_file(cls, path) -> "ECFG":
        """
        Get ECFG from file
        """
        with open(path) as f:
            return ECFG.from_text(f.read())
