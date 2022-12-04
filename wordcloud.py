import os
from pathlib import Path
import sys
import re
from collections import Counter

from utils import error_exit

import config

poems_folder_path = config.POEMS_FOLDER


def main(poem_ids, stopwords_file = 'stopword.txt'):
    dirname = str(Path(__file__).parent.absolute())
    stopwords_file_path = Path(dirname, stopwords_file)

    stopwords = load_stopwords(stopwords_file_path)

    collection_poem_words_filtered = process_poem_words(poem_ids, stopwords)

    # Create counter
    c = Counter(collection_poem_words_filtered)
    # Return words/freqs if freq > 2, ordered by freq desc
    collection_top_words = [{"text": word, "value": count} for word, count in c.most_common() if count > 2]

    return collection_top_words


def process_poem_words(poem_ids, stopwords):
    collection_poem_words = []
    for poem_id in poem_ids:
        poem_file = poems_folder_path + poem_id + '.txt'
        try:
            with open(poem_file, 'r') as poem:
                poem_lines = poem.readlines()[5:]
                # Split by all chars except alphanumeric, dash, apostrophe, single quote (sometimes used as apostrophe). Also remove new lines.
                poem_words_filtered = list(filter(None, re.split("[^\'’\-\w]", ("".join(poem_lines)).replace('\n', ' '))))
                # Add to full word list
                collection_poem_words.extend(poem_words_filtered)

        except Exception as e:
            print(e)

    # Filter out stopwords and words that aren't alphanumeric, convert all words to lowercase
    collection_poem_words_filtered = [poem_word.lower() for poem_word in collection_poem_words if poem_word.isalnum() and len(poem_word) > 1 and poem_word.lower() not in stopwords]

    return collection_poem_words_filtered


def load_stopwords(stopwords_file):
    with open(stopwords_file) as f:
        stopwords = [word.strip() for word in f.readlines()]
    return stopwords

if __name__ == '__main__':
    if len(sys.argv) < 2:
        error_exit("Please provide a list of poem ids.")
    else:
        main(sys.argv[1:])
