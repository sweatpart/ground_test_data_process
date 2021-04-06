import pymongo
import json

def get_db():
    client = pymongo.MongoClient()
    db = client['results']
    return db

def insert_db(self, user_id, project, result):
        db = get_db()
        record = {
            'user_id': user_id,
            'project': project,
            'solver': self.__class__.__name__,
            'result': json.dumps(result) 
        }
        db['test'].insert_one(record)

def query_db(parm=None, value=None):
    db = get_db()
    collection = db['test']
    if parm and value:
        result = collection.find({parm: value})
    else:
        result = collection.find()
    return result
