import os
import sys
from pathlib import Path

from utils import error_exit
import similar_poems

import pymongo
import config

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client[config.MONGO_DB]
feat_mongo_col = mongo_db[config.MONGO_FEATS_COLL]
poems_mongo_col = mongo_db[config.MONGO_POEMS_COLL]
collections_mongo_col = mongo_db[config.MONGO_POEMCOLLS_COLL]


def remove_from_files(poem_file, poem_id):
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
        print("DEBUG: " + col["collection_id"] + " collection now: ")
        print(poem_ids)

        # Update the poem collection
        collections_mongo_col.find_one_and_update( { "collection_id" : col["collection_id"] }, { '$set' : { "poem_ids" : poem_ids, "poem_titles" : poem_titles } } )

    # Delete features
    feat_mongo_col.delete_many( { "poem_id" : poem_id } )


def main(args):
    poem_file, poem_id = args[1], os.path.basename(args[1]).replace('.txt', '')
    remove_from_files(poem_file, poem_id)
    remove_from_mongo(poem_id)
    print('Completed removing poem: ' + poem_id)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        error_exit('Not enough arguments. Please provide a poem file.')
    main(sys.argv)
