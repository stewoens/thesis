import argparse
from trainer import Trainer, TrainingArgs
from rq8_model import TransformerModel
import models.trav_trans.dataset
from torch.nn import CrossEntropyLoss
from torch.optim import AdamW

def main():
    parser = argparse.ArgumentParser(description="Train GPT2 Model")
    parser.add_argument("--batch_size", type=int, default=4, help="Specify batch size")
    parser.add_argument("--num_epoch", type=int, default=3, help="Specify number of epochs")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="Specify AdamW learning rate")
    parser.add_argument("--dps", default="output/train_dps.txt")
    parser.add_argument("--ids", default="output/train_ids.txt")
    parser.add_argument("--suffix", default="unnamed")
    parser.add_argument("--save_on_epoch", type=bool, default = False)

    args = parser.parse_args()

    setup = models.trav_trans.dataset.Setup("output", args.dps, args.ids)

    model = TransformerModel(
        len(setup.vocab.idx2vocab),
        CrossEntropyLoss(ignore_index=-1),
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
        save_model_on_epoch = args.save_on_epoch,
        suffix = args.suffix
    )

    trainer = Trainer(
        model,
        setup,
        training_args
    )

    trainer.train()


if __name__ == "__main__":
    main()
