import sys
import pymongo
import config

from utils import error_exit

mongo_client = pymongo.MongoClient(config.CONN_STRING)
mongo_db = mongo_client['poems']
feat_mongo_col = mongo_db['featured']
poems_mongo_col = mongo_db['poems-list']


def main(poem_id, feature_text, set_current):
    try: # find poem title from poem_id
        poem_title = poems_mongo_col.find_one( { 'poem_id' : poem_id } )['poem_title']
    except:
        error_exit('Poem id was not found: ' + poem_id)

    feature_dict = {
                    'poem_id' : poem_id,
                    'poem_title' : poem_title,
                    'featured_text' : feature_text
                   }

    if set_current == 'true':  # remove current feature, then insert new feature and set as current feature
        feat_mongo_col.find_one_and_update( { 'currently_featured' : True }, { '$set' : { 'currently_featured' : False }  } )
        feature_dict['currently_featured'] = True
    else:
        feature_dict['currently_featured'] = False

    feat_mongo_col.insert_one(feature_dict)
    print("inserted feature: { poem_id : \'" + poem_id +
          "\', poem_title : \'" + poem_title +
          "\', featured_text : \'" + feature_text +
          "\', currently_featured : " + set_current + "}")
    return


if __name__ == '__main__':
    if len(sys.argv) < 4:
        error_exit('Please provide poem id, feature text, and if you\'d like to set this as the current feature.')
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
