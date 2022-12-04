import sys

import pymongo
import config

from utils import error_exit
import wordcloud

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client[config.MONGO_DB]
mongo_col = mongo_db[config.MONGO_POEMCOLLS_COLL]


def main(collection_id):
    poem_ids = find_collection_poems(collection_id)

    wordcloud_data = wordcloud.main(poem_ids)

    mongo_update_collection(collection_id, wordcloud_data)

    print('DEBUG: Finished updating wordcloud for collection: ' + collection_id)


def find_collection_poems(collection_id):
    poem_ids = mongo_col.find_one( { "collection_id" : collection_id } )["poem_ids"]
    return poem_ids


def mongo_update_collection(collection_id, wordcloud_data):
    try:
        mongo_col.find_one_and_update( { "collection_id" : collection_id }, { '$set' : { "wordcloud" : wordcloud_data } } )
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    if len(sys.argv) < 1:
        error_exit("Please provide a collection id.")
    else:
        main(sys.argv[1])
