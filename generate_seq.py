import ast
from mod import Link, TryBlock, FuncBlock, Block, CFG







def sequentialize_cfgs(cfg):
    cfgs = []
    def seq_cfg(cfg):
        cfg.reset_ids()
        seq = cfg.seq()
        cfgs.append(seq)

    seq_cfg(cfg)
    
    for fgraph in cfg.functioncfgs.values():
        seq_cfg(fgraph)
    for cgraph in cfg.classcfgs.values():
        seq_cfg(cgraph)
        for fgraph in cgraph.functioncfgs.values():
            seq_cfg(fgraph)

    return cfgs