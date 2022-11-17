import rq8_evaluate
import pickle
import rq8_model as model


def main():

    model_ids = list(range(10))
    scores = []

    for i, id in enumerate(model_ids):
        print(f"== Evaluating model rq8-model-{id}.pt ==")
        scores.append(rq8_evaluate.eval(f"rq8-model-{id}.pt", "output/test_dps.txt", "output/test_ids.txt"))

    pickle.dump(scores, open('output/scores.pickle', 'wb'))

if __name__ == "__main__":
    main()