import requests, pandas


# FUNCTIONS
def get_json_from_openlibrary(query):
    response = requests.get(url=f"https://openlibrary.org/{query}.json")
    if response.status_code == 404:
        return False
    json_data = response.json()
    return json_data


def get_author_names(json_data, row):
    author_names = []
    if "authors" in json_data.keys():
        for author in json_data['authors']:
            author_json = get_json_from_openlibrary(author['key'])
            if "name" in author_json.keys():
                author_names.append(author_json["name"])
            elif "personal_name" in author_json.keys():
                author_names.append(author_json["personal_name"])
            else:
                author_names.append("[no author]")
        return author_names
    else:
        return [row["author"]]


def format_author_string(author_list):
    if author_list[0] == "[no author]":
        return "[no author]"
    else:
        first_author_names = author_list[0].split()
        first_author_names.insert(0, first_author_names.pop(-1))
        for name in first_author_names:
            if name == first_author_names[0]:
                if len(first_author_names) == 0:
                    formatted_first_author = f"{name}"
                else:
                    formatted_first_author = f"{name},"
            else:
                formatted_first_author += f" {name}"
    author_string = formatted_first_author
    if len(author_list) == 0:
        return author_string
    elif len(author_list) > 3:
        return author_string + " et al."
    else:
        for author in author_list[1:]:
            if author == author_list[-1]:
                author_string += f" and {author}"
            else:
                author_string += f", {author}"
        return author_string


def get_publisher(json_data):
    if "publishers" in json_data.keys():
        publisher = json_data["publishers"][0]
    else:
        publisher = "[no publisher]"
    return publisher


def remove_statement_of_responsibility(title_string):
    x = title_string.find("/")
    return title_string[:x].strip()


def remove_punctuation(string):
    punctuation = '''!()-[]{};:'’‘"\;,<>./?@#$%^&*_~'''
    no_punc = ""
    for char in string:
        if char not in punctuation:
            no_punc += char
    return no_punc


def format_title(string):
    title_proper = remove_statement_of_responsibility(string)
    formatted_title_proper = remove_punctuation(title_proper).lower().strip()
    split_string = formatted_title_proper.split()
    new_string = " ".join(split_string)
    return new_string


#CREATE HTML
with open("results.html", "w", encoding="utf-8") as file:
    file.write('''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Results</title>
</head>
<body>''')

# READ CSVs
leganto_list_data = pandas.read_csv("example_leganto_list.csv")
queens_library_data = pandas.read_csv("queens_library_holdings.csv")

counter = 1
results = []
for index, row in leganto_list_data.iterrows():
    print(f"Checking item {counter} of {len(leganto_list_data.index)}")
    counter += 1
    bib_data = {} #change variable name
    #TEST PRINT
    print(f"TITLE: {row['Citation Title']}")
    #STEP 1: CHECK IF THIS IS A BOOK
    if row["Citation Type"] in ["Book", "Book chapter"]: #verify book chapter is formatted properly; add ebook?
    #STEP 2: DOES QUEENS' HAVE A HOLDINGS RECORD ATTACHED?
        if "Queens'" in row["Citation Availability"]:
            bib_data["match"] = "holdings"
            print(bib_data["match"])
    #STEP 3: DOES THE ISBN MATCH QUEENS' ISBNs?
    if "match" not in bib_data.keys():
        leganto_ISBN = row["Citation ISBN"]
        library_ISBNs = []  # used in step 4
        for i, r in queens_library_data.iterrows():
            if isinstance(r["ISBN"], str):
                library_ISBNs += r["ISBN"].split("; ")
                if leganto_ISBN in r["ISBN"].split("; "):
                    bib_data["match"] = "ISBN"
                    print(bib_data["match"])
                    break
    #STEP 4: DO ANY OF THE OTHER OPEN LIBRARY EDITIONS MATCH QUEENS' ISBNs?
    if "match" not in bib_data.keys():
        ol_book_data = get_json_from_openlibrary("isbn/" + row["Citation ISBN"])
        if ol_book_data is not False:
            work_ID = ol_book_data["works"][0]["key"]
            ol_work_data = get_json_from_openlibrary(work_ID + "/editions")
            for edition in ol_work_data["entries"]:
                if "isbn_13" in edition.keys():
                    for edition_ISBN in edition['isbn_13']:
                        if int(edition_ISBN) in library_ISBNs:
                            bib_data["match"] = "work"
                            bib_data['match_info'] = f"{edition['publishers'][0]}, {edition['publish_date']}"
                            print(bib_data["match"])
                            break
    #STEP 5: ARE THERE ANY TEXT MATCHES FOR AUTHORS/TITLES AMONG QUEENS' HOLDINGS?
    if "match" not in bib_data.keys():
        leganto_title = format_title(row["Citation Title"])
        for i, r in queens_library_data.iterrows():
            queens_title = format_title(r["Title"])
            if leganto_title in queens_title:
                bib_data["match"] = "title"
                # bib_data['match_info']
                print(bib_data["match"])
                break
    if "match" not in bib_data.keys():
        print("no match")

    # #Write to HTML file in the main loop

# Assume input is Leganto list
# -- format citations for chapters, ebooks, websites etc.
# -- check if holdings attached first
# If no match is found through ISBNs then do a title/author text search
# Use titles and authors from both input CSV and from OpenLibrary "work"
