import sys
import pymongo
import config

from utils import error_exit

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client['poems']
poems_mongo_col = mongo_db['poems-list']
collections_mongo_col = mongo_db['poem-collections-list']


def create_collection(args):
    if len(args) < 3:
        error_exit('Please provide collection id, collection name, and a collection summary.')

    collection_id, collection_name, collection_summary = args
    collection_dict = {
                        'collection_id' : collection_id,
                        'collection_name' : collection_name,
                        'collection_summary' : collection_summary
                      }
    collections_mongo_col.insert_one(collection_dict)
    print("inserted collection: { collection_id : \'" + collection_id +
          "\', collection_name : \'" + collection_name +
          "\', collection_summary : " + collection_summary + "}")
    return


def get_collection(collection_id):  # Return poem ids of all poems in specified collection
    if not collection_id:
        error_exit('Please provide collection id.')

    collection_dict = collections_mongo_col.find_one( { "collection_id" : collection_id } )

    poem_ids = " ".join(collection_dict['poem_ids'])

    return poem_ids


if __name__ == '__main__':
    if len(sys.argv) < 1:
        error_exit('Please provide arguments, including a collection command.')
    else:
        command = sys.argv[1]

        if command == 'create':
            create_collection(sys.argv[2:])
        elif command == 'get':
            get_collection(sys.argv[2].strip())
        elif command == 'edit':
            edit_collection(sys.argv[2:])
        else:
            error_exit('Unknown argument! Please choose create, get, or edit.')
