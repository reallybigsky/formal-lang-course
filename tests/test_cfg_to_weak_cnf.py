from functools import reduce
from pyformlang.cfg import CFG, Terminal, Variable
from project.context_free_grammar import import_cfg_from_file, cfg_to_weak_cnf


def test_cfg_to_weak_cnf():
    def is_cfg_in_weak_cnf(cfg: CFG) -> bool:
        try:
            for production in cfg.productions:
                if len(production.body) == 0:
                    continue
                elif len(production.body) == 1:
                    assert isinstance(production.body[0], Terminal)
                elif len(production.body) == 2:
                    assert isinstance(production.body[0], Variable) and isinstance(
                        production.body[1], Variable
                    )
                else:
                    assert False
        except AssertionError:
            return False

        return True

    def check_cfg_in_weak_cnf(path: str, max_word_len=10):
        cfg = import_cfg_from_file(path)
        weak_cnf_cfg = cfg_to_weak_cnf(cfg)

        expected_words = set()
        for word in cfg.get_words(max_length=max_word_len):
            expected_words.add(reduce(lambda acc, symbol: acc + str(symbol), word, ""))
        actual_words = set()
        for word in weak_cnf_cfg.get_words(max_length=max_word_len):
            actual_words.add(reduce(lambda acc, symbol: acc + str(symbol), word, ""))

        assert is_cfg_in_weak_cnf(weak_cnf_cfg) and expected_words == actual_words

    check_cfg_in_weak_cnf("./tests/data/cfg_decompose.txt")
    check_cfg_in_weak_cnf("./tests/data/cfg_epsilon.txt")
    check_cfg_in_weak_cnf("./tests/data/cfg_general_test.txt")
    check_cfg_in_weak_cnf("./tests/data/cfg_terminals_to_variables.txt")
    check_cfg_in_weak_cnf("./tests/data/cfg_unit_production.txt")
    check_cfg_in_weak_cnf("./tests/data/cfg_useless_variables.txt")
