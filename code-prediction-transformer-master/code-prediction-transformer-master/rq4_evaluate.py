import torch
import argparse

from torch._C import StringType
import model

from rq4_dataset import Dataset
from tokenizers import Tokenizer
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description="Evaluate new tokenizer GPT-2 model")
    parser.add_argument("--model", default="rq4/rq4_model.pt", help="Specify model file")
    parser.add_argument("--dps", default="output/rq4_test_dps.txt", help="Specify data file (dps) on which to evaluate")
    parser.add_argument("--ids", default="output/rq4_test_ids.txt", help="Specify data file (ids) on which to evaluate")
    parser.add_argument("--tokenizer", default="output/tokenizer.json", help="Specify tokenizer file")

    args = parser.parse_args()

    tokenizer = Tokenizer.from_file(args.tokenizer)

    eval(args.model, args.dps, args.ids, tokenizer)

def mean_reciprocal_rank(labels, predictions):
    scores = []
    for i, l in enumerate(labels):
        score = 0
        for j, p in enumerate(predictions[i]):
            if l == p:
                score = 1 / (j + 1)
                break
        scores.append(score)
    if len(scores) > 0:
        return sum(scores) / len(scores)
    else:
        return 0

def eval(model_fp, dps, ids, tokenizer):
    dataset = Dataset(dps, ids)
    pad_idx = tokenizer.encode("[PAD]").ids[0]
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=1,
        collate_fn = lambda b: dataset.collate(b, pad_idx)
    )
    m = model.from_file(model_fp, tokenizer.get_vocab_size(), pad_idx)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    m = m.to(device)
    m.eval()
    print("Evaluating {} batches".format(len(dataloader)))

    # Values (Predict type + value)
    # one score value per batch
    value_scores = {
        "attr_ids": {"v_scores": [], "t_scores": []},
        "num_ids": {"v_scores": [], "t_scores": []},
        "name_ids": {"v_scores": [], "t_scores": []},
        "param_ids": {"v_scores": [], "t_scores": []},
        "string_ids": {"v_scores": [], "t_scores": []}
    }

    # Types (Predict type only)
    type_scores = {
        "call_ids": [],
        "assign_ids": [],
        "return_ids": [],
        "list_ids": [],
        "dict_ids": [],
        "raise_ids": []
    }

    for i, batch in tqdm(enumerate(dataloader)):
        if True:
            with torch.no_grad():
                x = batch["input_seq"][0]
                y = batch["target_seq"][0]

                x = x.to(device)
                output = m(x, None)

                ### Evaluate leaf node scores, type + value ###
                for key in value_scores:
                    # print("{}".format(key))
                    value_ids = [a - 1 for a in batch["ids"][key] if a > 0]
                    type_ids = [a - 2 for a in batch["ids"][key] if a > 1]

                    # leaf node value scoring
                    if len(value_ids) > 0:
                        # Generate top10 predictions for each value for 20 times if possible, keep predctions if #1 prediction starts with ##
                        limit = 20
                        # Holds top predictions for each value ID, each prediction with i > 0 has to start with ## because of wordpiece
                        value_predictions = []
                        for v in value_ids:
                            # Holds the top 10 predictions for the next 20 words
                            predictions = torch.topk(output[v:v+min(limit, len(output) - v)], 10)[1].tolist()
                            # Prediction in form of (top10pred_tokens, offset, id_value)
                            if len(predictions) == 0:
                                continue
                            value_predictions.append((predictions[0], 0, v))
                            for j in range(1, len(predictions)):
                                # If a prediction > 0 doesn't start with ##, the subwort is over
                                if tokenizer.decode([predictions[j][0]]).strip().startswith("##"):
                                    value_predictions.append((predictions[j], j, v))
                                else:
                                    break
                        # value scoring
                        y_ids = [y_id[1] + y_id[2] for y_id in value_predictions]
                        predictions = [pred[0] for pred in value_predictions]
                        value_scores[key]["v_scores"].append(mean_reciprocal_rank(y[y_ids], predictions))

                    # leaf node type scoring
                    if len(type_ids) > 0:
                        # Generate top10 predictions for each value for 20 times if possible, keep predctions if #1 prediction starts with ##
                        limit = 20
                        # Holds top predictions for each value ID, each prediction with i > 0 has to start with ## because of wordpiece
                        type_predictions = []
                        for t in type_ids:
                            # Holds the top 10 predictions for the next 20 words
                            predictions = torch.topk(output[t:t+min(limit, len(output) - t)], 10)[1].tolist()
                            # Prediction in form of (top10pred_tokens, offset, id_value)
                            if len(predictions) == 0:
                                continue
                            type_predictions.append((predictions[0], 0, t))
                            for j in range(1, len(predictions)):
                                # If a prediction > 0 doesn't start with ##, the subwort is over
                                if tokenizer.decode([predictions[j][0]]).strip().startswith("##"):
                                    type_predictions.append((predictions[j], j, t))
                                else:
                                    break
                        # value scoring
                        y_ids = [y_id[1] + y_id[2] for y_id in type_predictions]
                        predictions = [pred[0] for pred in type_predictions]
                        value_scores[key]["t_scores"].append(mean_reciprocal_rank(y[y_ids], predictions))


                    # leaf node type scoring
                    # if len(type_ids) > 0:
                    #     type_predictions = [torch.topk(o, 10)[1].tolist() for o in output[type_ids]]
                    #     value_scores[key]["t_scores"].append(mean_reciprocal_rank(y[type_ids], type_predictions))
                
                ### Evaluate internal node scores, type ###
                for key in type_scores:
                    type_ids = [a - 1 for a in batch["ids"][key] if a > 0]
                    
                    # internal node scoring
                    if len(type_ids) > 0:
                        # Generate top10 predictions for each value for 20 times if possible, keep predctions if #1 prediction starts with ##
                        limit = 20
                        # Holds top predictions for each value ID, each prediction with i > 0 has to start with ## because of wordpiece
                        type_predictions = []
                        for t in type_ids:
                            # Holds the top 10 predictions for the next 20 words
                            predictions = torch.topk(output[t:t+min(limit, len(output) - t)], 10)[1].tolist()
                            # Prediction in form of (top10pred_tokens, offset, id_value)
                            if len(predictions) == 0:
                                continue
                            type_predictions.append((predictions[0], 0, t))
                            for j in range(1, len(predictions)):
                                # If a prediction > 0 doesn't start with ##, the subwort is over
                                if tokenizer.decode([predictions[j][0]]).strip().startswith("##"):
                                    type_predictions.append((predictions[j], j, t))
                                else:
                                    break
                        # value scoring
                        y_ids = [y_id[1] + y_id[2] for y_id in type_predictions]
                        predictions = [pred[0] for pred in type_predictions]
                        type_scores[key].append(mean_reciprocal_rank(y[y_ids], predictions))

                    # if len(type_ids) > 0:
                    #     type_predictions = [torch.topk(o, 10)[1].tolist() for o in output[type_ids]]
                    #     type_scores[key].append(mean_reciprocal_rank(y[type_ids], type_predictions))

    for k, s in value_scores.items():
        print("{}".format(k))
        if len(value_scores[k]["t_scores"]) > 0:
            print("\tType Prediction: {}".format(sum(value_scores[k]["t_scores"])/len(value_scores[k]["t_scores"])))
        else:
            print("\tType Prediction: None")
        if len(value_scores[k]["v_scores"]) > 0:
            print("\tValue Prediction: {}".format(sum(value_scores[k]["v_scores"])/len(value_scores[k]["v_scores"])))
        else:
            print("\tValuePrediction: None")

    for k, s in type_scores.items():
        print("{}".format(k))
        if len(type_scores[k]) > 0:
            print("\tType Prediction: {}".format(sum(type_scores[k])/len(type_scores[k])))
        else:
            print("\tType Prediction: None")


if __name__ == "__main__":
    main()