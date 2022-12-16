import data

d = data.CodeDataset()
d.load_from_file("output/converted_train.txt")
d.cache_dataset("output/inputs.pkl")