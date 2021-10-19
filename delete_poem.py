import os
import sys
from pathlib import Path

from utils import error_exit
import similar_poems

import pymongo
import config

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client['poems']
feat_mongo_col = mongo_db['featured']
poems_mongo_col = mongo_db['poems-list']
collections_mongo_col = mongo_db['poem-collections-list']


def find_in_mongo(poem_id, mongo_collection, search_field, return_field):
    ret = []

    for result in mongo_collection.find( { search_field : poem_id } ):
        ret.append(result[return_field])

    print(ret)


def run_similar_poems_script(poem_file, poem_id):
    # Get file directory and name
    poem_dir, poem_filename = Path(poem_file).parent.absolute(), Path(poem_file).name

    # Create subdirectory to move file into (if not existing)
    subdir = Path(poem_dir / "hidden")
    if not os.path.exists(subdir):
        os.makedirs(subdir)

    # Move file into subdirectory
    os.rename(poem_file, Path(subdir, poem_filename))

    # Re-run similar_poems script
    similar_poems.main(poem_dir)


def remove_from_mongo(poem_id):
    # Delete poem from poems-list
    poems_mongo_col.delete_one( { "poem_id" : poem_id } )

    # Delete poem from poem collections
    for col in collections_mongo_col.find( { "poem_ids" : poem_id } ):
        poem_ids, idx = col["poem_ids"], col["poem_ids"].index(poem_id)
        poem_titles = col["poem_titles"]

        if len(poem_ids) == 1:  # Delete entire poem collection
            collections_mongo_col.delete_one( { "collection_id" : col["collection_id"] } )
            continue

        # Remove the poem from poem collection
        poem_ids.pop(idx)
        poem_titles.pop(idx)
        print(poem_ids, poem_titles)

        # Update the poem collection
        collections_mongo_col.find_one_and_update( { "collection_id" : col["collection_id"] }, { '$set' : { "poem_ids" : poem_ids, "poem_titles" : poem_titles } } )


def delete_feature(poem_id):
    feat_mongo_col.delete_many( { "poem_id" : poem_id } )


def invalidate_feature(poem_id):
    feat_mongo_col.update_many( { "poem_id" : poem_id }, { '$set' : { "currently_featured" : False } } )


def main(args):
    poem_file, option, poem_id = args[1], args[2], os.path.basename(args[1]).replace('.txt', '')
    if option == 'find':
        # similar_poems
        find_in_mongo(poem_id, poems_mongo_col, "similar_poems_ids", "poem_title")
        # collections
        find_in_mongo(poem_id, collections_mongo_col, "poem_ids", "collection_name")
        # features
        find_in_mongo(poem_id, feat_mongo_col, "poem_id", "featured_text")
        print(poem_id)
        print(poem_file)
        return
    elif option == 'delete':
        run_similar_poems_script(poem_file, poem_id)
        remove_from_mongo(poem_id)
        feat_option = args[3]
        if feat_option == 'delete':
            delete_feature(poem_id)
        else:
            invalidate_feature(poem_id)
        print('Completed removing poem.')

    else:
        error_exit('Command not found! Please specify what option you want for the delete poem script.')


if __name__ == '__main__':
    main(sys.argv)
