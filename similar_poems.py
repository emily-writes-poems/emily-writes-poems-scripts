import os
from pathlib import Path
import sys
import re

from gensim import corpora


stopwords = []


def load_stopwords(stopwords_file = "stopword.txt"):
    dirname = str(Path(__file__).parent.absolute())
    stopwords_file_path = Path(dirname, stopwords_file)

    global stopwords
    with open(stopwords_file) as f:
        stopwords = [word.strip() for word in f.readlines()]
    return stopwords


def lowercase_and_remove_stopwords(text):
    text_filtered = [word.lower() for word in text if word.lower() not in stopwords]
    return (" ".join(text_filtered))


def get_poem_documents(poem_dir):
    poem_file_paths = []
    for root, dirs, files in os.walk(poem_dir):
        for file in files:
            if file.endswith('.txt'):
                poem_file_paths.append(os.path.join(root, file))

    poem_documents = []
    for file_path in poem_file_paths:
        with open(file_path, 'r') as f:
            file_lines = f.readlines()

            # file_lines: (0) poem title, (1) my name, (2) poem date, (3) newline, (4-end) poem text
            poem_title = file_lines[0].rstrip()

            # Split by all chars except alphanumeric, dash, apostrophe
            # Remove newlines and filter out blanks
            poem_words = list(filter(None, re.split("[^\'’\-\w]", ("".join(file_lines[4:])).replace('\n', ' '))))

            poem_text = lowercase_and_remove_stopwords(poem_words)

            # Concat poem title and text
            poem_document = poem_title + ' ' + poem_text

            poem_documents.append(poem_document)

    return poem_documents


def get_corpora(documents):
    pass



if __name__ == '__main__':
    load_stopwords()
    documents = get_poem_documents(sys.argv[1])
    print(documents)
    #poem_corpora = get_corpora(documents)
