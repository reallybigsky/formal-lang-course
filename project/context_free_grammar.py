from pyformlang.cfg import CFG


def import_cfg_from_file(path: str) -> CFG:
    """
    Load context free grammar from file
    :param path: filepath with CFG
    :return: CFG from file
    """
    with open(path) as f:
        content = f.readlines()
        return CFG.from_text("\n".join(content))


def cfg_to_weak_cnf(cfg: CFG) -> CFG:
    """
    Convert context free grammar to weak Chomsky normal form
    :param cfg: context free grammar
    :return: weak Chomsky normal form
    """
    cfg_no_unit_prods = cfg.eliminate_unit_productions().remove_useless_symbols()
    new_prods = cfg_no_unit_prods._get_productions_with_only_single_terminals()
    new_prods = cfg_no_unit_prods._decompose_productions(new_prods)
    result = CFG(
        start_symbol=cfg_no_unit_prods.start_symbol,
        productions=set(new_prods),
    )
    return result
