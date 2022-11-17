import argparse
from rq4_dataset import Dataset
from tokenizers import Tokenizer
from rq4_trainer import Trainer, TrainingArgs
from model import TransformerModel
import models.trav_trans.dataset
from torch.nn import CrossEntropyLoss
from torch.optim import AdamW

def main():
    parser = argparse.ArgumentParser(description="Train GPT2 Model")
    parser.add_argument("--batch_size", type=int, default=4, help="Specify batch size")
    parser.add_argument("--num_epoch", type=int, default=3, help="Specify number of epochs")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Specify AdamW learning rate")

    args = parser.parse_args()

    tokenizer = Tokenizer.from_file("output/tokenizer.json")
    dataset = Dataset("output/train_rq4_dps.txt")

    model = TransformerModel(
        tokenizer.get_vocab_size(),
        CrossEntropyLoss(ignore_index=tokenizer.encode("[PAD]").ids[0]),
        6,
        300,
        1000,
        6,
        1e-05
    )

    training_args = TrainingArgs(
        batch_size = args.batch_size,
        num_epoch = args.num_epoch,
        output_dir = "output",
        optimizer = AdamW(model.parameters(), lr=args.learning_rate),
        save_model_on_epoch = False
    )

    trainer = Trainer(
        model,
        dataset,
        tokenizer,
        training_args
    )

    trainer.train()


if __name__ == "__main__":
    main()
