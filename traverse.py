import json
from cptm.utils import file_tqdm, get_dfs, separate_dps

data = 'OUTPUT/sample_data.json'
out = 'OUTPUT/dps.txt'

with open(data, "r") as f, open(out, "w") as fout:
    for line in file_tqdm(f):
        dp = json.loads(line.strip())
        asts = separate_dps(dp, 1000)