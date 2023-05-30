import ast
from mod import Link, TryBlock, FuncBlock, Block, CFG

cfgs = []
edges = []


def seq_cfg(cfg):
    # main cfg
    cfg.reset_ids()
    stmt, e = cfg.seq()
    cfgs.append(stmt)
    edges.append(e)


def sequentialize_cfgs(cfg):

    seq_cfg(cfg)
    
    for fgraph in cfg.functioncfgs.values():
        seq_cfg(fgraph)
    for cgraph in cfg.classcfgs.values():
        seq_cfg(cgraph)
        for fgraph in cgraph.functioncfgs.values():
            seq_cfg(fgraph)

    return cfgs, edges