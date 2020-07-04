import os
from pathlib import Path
import sys
import re
import pymongo

from gensim import corpora
from gensim import models
from gensim import similarities


mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client['poems']
mongo_col = mongo_db['poems-list']

stopwords = []


def load_stopwords(stopwords_file = "stopword.txt"):
    dirname = str(Path(__file__).parent.absolute())
    stopwords_file_path = Path(dirname, stopwords_file)

    global stopwords
    with open(stopwords_file_path) as f:
        stopwords = [word.strip() for word in f.readlines()]
    return stopwords


def lowercase_and_remove_stopwords(text):
    text_filtered = [word.lower() for word in text if word.lower() not in stopwords]
    return text_filtered


def get_processed_poems(poem_dir):
    poem_file_paths = []
    for root, dirs, files in os.walk(poem_dir):
        for file in files:
            if file.endswith('.txt'):
                poem_file_paths.append(os.path.join(root, file))

    poem_documents = []  # title + text as list of words, filtered (lowercase, removed stopwords)
    poem_titles = []  # poem titles
    poem_ids = []  # for indexing into DB

    for file_path in poem_file_paths:
        poem_ids.append(os.path.basename(file_path).replace('.txt', ''))

        with open(file_path, 'r') as f:
            file_lines = f.readlines()

            # file_lines: (0) poem title, (1) my name, (2) poem date, (3) newline, (4-end) poem text
            poem_title = file_lines[0].rstrip()
            poem_titles.append(poem_title)

            # Split by all chars except alphanumeric, dash, apostrophe
            # Remove newlines and filter out blanks
            poem_title_formatted = list(filter(None, re.split("[^\'’\-\w]", poem_title.lower())))

            poem_words = list(filter(None, re.split("[^\'’\-\w]", ("".join(file_lines[4:])).replace('\n', ' '))))

            # Concat poem title and text
            poem_document = poem_title_formatted +  lowercase_and_remove_stopwords(poem_words)

            poem_documents.append(poem_document)

    return poem_titles, poem_documents, poem_ids


def get_dictionary(documents):
    dictionary = corpora.Dictionary(documents)
    return dictionary


def get_bow_vectors(documents, dictionary):
    bow_vectors = [dictionary.doc2bow(doc) for doc in documents]
    return bow_vectors


def tfidf_lsi_similarity(poem_titles, poem_documents, poem_ids, bow, dictionary):
    tfidf = models.TfidfModel(bow)
    corpus_tfidf = tfidf[bow]

    lsi_model = models.LsiModel(corpus_tfidf, id2word = dictionary, num_topics=5)
    corpus_lsi = lsi_model[corpus_tfidf]

    index = similarities.MatrixSimilarity(corpus_lsi)  # index using LSI

    top_similar_poems = {}

    for poem_idx, poem_sim in enumerate(index):  # compare all poems to all other poems in corpus
        #print('='*15 + f'{poem_ids[poem_idx]}: \'{poem_titles[poem_idx]}\' ' + '='*15)
        similar_poems_ids_and_titles = [[],[]]

        sorted_sim = sorted(enumerate(poem_sim), key=lambda item: -item[1])  # sort by highest similarity
        for (sim_poem_idx, sim_value) in sorted_sim[1:4]:
            similar_poems_ids_and_titles[0].append(poem_ids[sim_poem_idx])
            similar_poems_ids_and_titles[1].append(poem_titles[sim_poem_idx])
            #print(f'{poem_ids[sim_poem_idx]}: \'{poem_titles[sim_poem_idx]}\' {sim_value}')

        top_similar_poems[poem_ids[poem_idx]] = similar_poems_ids_and_titles

    #print(top_similar_poems)
    return top_similar_poems


def mongo_update_similar_poems(top_similar_poems):
    for poem_id, similar_poems in top_similar_poems.items():
        print(f'{poem_id} : {similar_poems}')
        mongo_col.find_one_and_update({ 'poem_id' : poem_id }, { '$set' : { 'similar_poems_ids' : similar_poems[0], 'similar_poems_titles' : similar_poems[1] } })


def main(poems_directory):
    load_stopwords()

    poem_titles, poem_documents, poem_ids = get_processed_poems(poems_directory)

    poem_dictionary = get_dictionary(poem_documents)

    poem_bow = get_bow_vectors(poem_documents, poem_dictionary)

    top_similar_poems = tfidf_lsi_similarity(poem_titles, poem_documents, poem_ids, poem_bow, poem_dictionary)

    mongo_update_similar_poems(top_similar_poems)

    print('DEBUG: Finished running similar_poems.py')


if __name__ == '__main__':
    poems_directory = sys.argv[1]

    main(poems_directory)
