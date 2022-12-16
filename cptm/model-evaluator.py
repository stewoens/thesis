import evaluate
import pickle
import model as model


def main():

    model_ids = range(12)
    scores = []

    for i, id in enumerate(model_ids):
        print(f"== Evaluating model rq1/model-{id}.pt ==")
        scores.append(evaluate.eval(f"rq1/model-{id}.pt", "output/test_dps.txt", "output/test_ids.txt"))

    pickle.dump(scores, open('output/scores.pickle', 'wb'))

if __name__ == "__main__":
    main()