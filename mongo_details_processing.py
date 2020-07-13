import os
from pathlib import Path
import sys
import re
from collections import Counter

import pymongo
import config

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client['poems']
mongo_col = mongo_db['poems-list']

stopwords = []

def main(input_file, stopwords_file = 'stopword.txt'):
    dirname = str(Path(__file__).parent.absolute())
    stopwords_file_path = Path(dirname, stopwords_file)

    global stopwords
    stopwords = load_stopwords(stopwords_file_path)

    # directory
    if os.path.isdir(input_file):
        for dirname, dirs, files in os.walk(input_file):
            for file in files:
                if file.endswith('_ANNOTATED.txt'):
                    print('DEBUG: Found file: ' + file + ' in folder ' + dirname)
                    doc = format_details(dirname + file)
                    mongo_update_details(doc)
    # single file
    elif os.path.isfile(input_file):
        if input_file.endswith('.txt'):
            print('DEBUG: Found file: ' + input_file)
            doc = format_details(input_file)
            mongo_update_details(doc)
    else:
        print('DEBUG: No appropriate files found.')
        return


def format_details(input_file, update_top_words = True, num_words = 5):
    doc = {}
    doc['poem_id'] = os.path.basename(input_file).replace('_ANNOTATED.txt', '')

    with open(input_file, 'r') as f:
        file_lines = f.readlines()

        # Scan in details
        poem_name = file_lines[0].rstrip()
        assert file_lines[2].rstrip() == 'Title'  # divider label
        doc['poem_behind_title'] = file_lines[3].rstrip()
        assert file_lines[5].rstrip() == 'Behind the poem'  # divider label
        doc['poem_behind_poem'] = file_lines[6].rstrip()

        if update_top_words: # divider label exists
            assert file_lines[8] == 'Poem lines\n'
            # Split by all chars except alphanumeric, dash, apostrophe, single quote (sometimes used as apostrophe)
            # Remove newlines and filter out blanks
            poem_words = list(filter(None, re.split("[^\'’\-\w]", ("".join(file_lines[9:])).replace('\n', ' '))))
            #print(poem_words)

            doc['top_words'] = get_top_words(poem_words, num_words)

    return doc


def get_top_words(poem_words, num_words):
    # Filter out stopwords, convert all words to lowercase
    poem_words_filtered = [poem_word.lower() for poem_word in poem_words if poem_word.lower() not in stopwords]
    # Create counter
    c = Counter(poem_words_filtered)
    # Return words/freqs if freq > 1
    top_words = dict([(word, count) for word, count in c.most_common(num_words) if count > 1])

    return top_words


def load_stopwords(stopwords_file):
    with open(stopwords_file) as f:
        stopwords = [word.strip() for word in f.readlines()]
    return stopwords


def mongo_update_details(doc):
    try:
        mongo_col.find_one_and_update({ 'poem_id' : doc['poem_id'] }, { '$set' : doc })
        print('DEBUG: updated details into mongo')
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main(sys.argv[1])
