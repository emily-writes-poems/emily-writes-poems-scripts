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


def format_details(input_file):
    doc = {}

    poem = open(input_file, 'r')

    doc['poem_id'] = os.path.basename(input_file).replace('_ANNOTATED.txt', '')
    poem.readline()  # poem title
    poem.readline()  # extra newline before 'Title'
    assert poem.readline().rstrip() == 'Title'  # divider label
    doc['poem_behind_title'] = poem.readline()
    poem.readline()  # extra newline before 'Behind the poem'
    assert poem.readline().rstrip() == 'Behind the poem'  # divider label
    doc['poem_behind_poem'] = poem.readline().rstrip()

    print(f'DEBUG: annotations for "{doc["poem_id"]}" complete.')

    return(doc)


def mongo_update_details(doc):
    try:
        mongo_col.find_one_and_update({'poem_id' : doc['poem_id']}, {'$set': doc})
        print('DEBUG: updated annotations into mongo')
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main(sys.argv[1])
