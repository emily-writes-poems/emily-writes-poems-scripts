import os
import sys
import pymongo

mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client['poems']
mongo_col = mongo_db['poems-list']

def main(input_file):
    # directory
    if os.path.isdir(input_file):
        for dirname, dirs, files in os.walk(input_file):
            for file in files:
                if file.endswith('.txt'):
                    print('DEBUG: Found file: ' + file + ' in folder ' + dirname)
                    doc = format_poem(dirname + file)
                    mongo_insert_poem(doc)
    # single file
    elif os.path.isfile(input_file):
        if input_file.endswith('.txt'):
            print('DEBUG: Found file: ' + input_file)
            doc = format_poem(input_file)
            mongo_insert_poem(doc)
    else:
        print('DEBUG: No appropriate files found.')
        return


def format_poem(input_file):
    doc = {}

    poem = open(input_file, 'r')

    doc['poem_title'] = poem.readline().rstrip()
    poem.readline().rstrip() # line that has my name
    doc['poem_date'] = poem.readline().rstrip()
    poem.readline() # extra newline before poem text

    poem_text = []  # get list of all lines
    for line in poem:
        poem_text.append(line.rstrip())  # strip new line characters

    doc['poem_text'] = poem_text
    doc['poem_linecount'] = len(poem_text)
    doc['poem_wordcount'] = sum(len(line.split()) for line in poem_text)

    print(f'DEBUG: formatting "{doc["poem_title"]}" complete.')
    print(doc)

    return(doc)


def mongo_insert_poem(doc):
    try:
        mongo_col.insert_one(doc)
        print('DEBUG: inserted poem into mongo')
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main(sys.argv[1])
