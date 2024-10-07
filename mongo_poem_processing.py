import os
from pathlib import Path
import sys

from utils import error_exit

import pymongo
import config

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client[config.MONGO_DB]
mongo_col = mongo_db[config.MONGO_POEMS_COLL]


def main(input_file):
    # directory
    if os.path.isdir(input_file):
        for dirname, dirs, files in os.walk(input_file):
            for file in files:
                if file.endswith('.txt') and not file.endswith('_ANNOTATED.txt'):
                    print('DEBUG: Found file: ' + file + ' in folder ' + dirname)
                    doc = format_poem(os.path.join(dirname, file))
                    mongo_insert_poem(doc)

    # single file
    elif os.path.isfile(input_file):
        if input_file.endswith('_ANNOTATED.txt'):
            error_exit("This is a details file!")
        if input_file.endswith('.txt'):
            print('DEBUG: Found file: ' + input_file)
            doc = format_poem(input_file)
            mongo_insert_poem(doc)
    else:
        error_exit("No appropriate file was found!")


def format_poem(input_file):
    doc = {}

    poem = open(input_file, 'r')

    doc['poem_id'] = os.path.basename(input_file).replace('.txt', '')
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

    print(doc)
    print(f'DEBUG: formatting "{doc["poem_title"]}" complete.')

    return(doc)


def mongo_insert_poem(doc):
    try:
        mongo_col.update_one( { "poem_id" : doc['poem_id'] }, { '$set' :  doc}, upsert=True )
        print('DEBUG: inserted poem into mongo')
        return 0
    except Exception as e:
        print(str(e))
        return -1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        error_exit("Please provide a file.")
    else:
        main(sys.argv[1])
