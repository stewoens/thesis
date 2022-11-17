import torch
import utils
import json

class Dataset(torch.utils.data.Dataset):
    def __init__(self, fp, ids_fp):
        super().__init__()
        self.fp = fp
        self.ids_fp = ids_fp
        self._line_pos_dp = list(utils.line_positions(fp))
        self._line_pos_ids = list(utils.line_positions(ids_fp))
        assert (len(self._line_pos_dp) == len(self._line_pos_ids))
    
    def __len__(self):
        return len(self._line_pos_dp)
    
    def __getitem__(self, idx):
        line_pos = self._line_pos_dp[idx]
        with open(self.fp) as f:
            f.seek(line_pos)
            dp_line = f.readline().strip()
        
        line_pos = self._line_pos_ids[idx]
        with open(self.ids_fp) as f:
            f.seek(line_pos)
            ids_line = f.readline().strip()
        return (json.loads(dp_line), json.loads(ids_line))

    @staticmethod
    def collate(seqs, pad_idx=None):
        max_len = max(len(seq[0][0]) for seq in seqs)
        max_len = max(max_len, 2)
        input_seqs = []
        target_seqs = []
        extended = []
        ids = {name: [] for name in seqs[0][1].keys()}

        for i,  ((seq, ext), ids_lst) in enumerate(seqs):
            padding = [pad_idx] * (max_len - len(seq))
            input_seqs.append(seq[:-1] + padding)
            target_seqs.append(seq[1:] + padding)
            extended.append(ext)
            for name, lst in ids_lst.items():
                ids[name] += [j - i + (max_len - 1) * i for j in lst]

        return {
            "input_seq": torch.tensor(input_seqs),
            "target_seq": torch.tensor(target_seqs),
            "extended": torch.tensor(extended),
            "ids": ids
        }