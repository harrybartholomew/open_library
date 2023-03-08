import pandas

leganto_list_data = pandas.read_csv("example_leganto_list.csv")

sections = leganto_list_data['Section Name'].unique()
for i in range(len(sections)):
    print(i)
    print(sections[i])