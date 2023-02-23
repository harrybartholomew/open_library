import requests, csv, pandas

#FUNCTIONS
def get_json_from_openlibrary(query):
    response = requests.get(url=f"https://openlibrary.org/{query}.json")
    response.raise_for_status()
    json_data = response.json()
    return json_data


def get_author_names(json_data):
    author_names = []
    for author in json_data['authors']:
        author_json = get_json_from_openlibrary(author['key'])
        if "name" in author_json.keys():
            author_names.append(author_json["name"])
        elif "personal_name" in author_json.keys():
            author_names.append(author_json["personal_name"])
        else:
            author_names.append("[no author]")
    return author_names


def get_publisher(json_data):
    if "publishers" in json_data.keys():
        publisher = data["publishers"][0]
    else:
        publisher = "[no publisher]"
    return publisher


#READ CSVs
reading_list_data = pandas.read_csv("reading_list.csv")
library_ISBNs = pandas.read_csv("library_ISBNs.csv")['ISBN'].to_list()

counter = 1
results = []
for ISBN in reading_list_data['ISBN']:
    print(f"Checking item {counter} of {len(reading_list_data['ISBN'].to_list())}")
    counter += 1
    data = get_json_from_openlibrary("isbn/" + str(ISBN))
    bibliographic_data = {
        "work_ID": data["works"][0]["key"],
        "authors": get_author_names(data),
        "title": data["title"],
        "publisher": get_publisher(data),
        "year": data["publish_date"]
    }
    if int(ISBN) in library_ISBNs:
        bibliographic_data["match"] = "edition"
    else:
        work_data = get_json_from_openlibrary(bibliographic_data['work_ID'] + "/editions")
        for edition in work_data["entries"]:
            if "isbn_13" in edition.keys():
                for other_edition_ISBN in edition['isbn_13']:
                    if int(other_edition_ISBN) in library_ISBNs:
                        bibliographic_data["match"] = "work"
                        bibliographic_data['match_info'] = f"{edition['publishers'][0]}, {edition['publish_date']}"
                        break
    if "match" not in bibliographic_data.keys():
        bibliographic_data['match'] = "no match"
    if bibliographic_data['match'] in ["edition", "no match"]:
        bibliographic_data['match_info'] = "..."
    results.append(bibliographic_data)

for result in results:
    print(f"{result['authors'][0]}, {result['title'].upper()} ({result['publisher']}, {result['year']}) -- {result['match']}: {result['match_info']}")



