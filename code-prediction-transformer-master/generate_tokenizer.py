from pathlib import Path
from tokenizers import ByteLevelBPETokenizer

tokenizer = ByteLevelBPETokenizer()

tokenizer.train(files="output/new_ast_raw.txt", vocab_size=100_000, special_tokens=[
    "<pad_token>",
    "<unk_token>",
    "<mask>",
    "<ast>"
])

tokenizer.save_model("./tokenizer/", "code")