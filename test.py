import pandas

leganto_data = pandas.read_csv("example_leganto_list.csv")

for i, r in leganto_data.iterrows():
    x = r["Citation Title"].find("/")
    print(r["Citation Title"][:x-1])