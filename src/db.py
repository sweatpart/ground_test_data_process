import pymongo
import json
import csv

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
        matches = collection.find({parm: value})
    else:
        matches = collection.find()
    return matches

def extract_result(match):
    return json.loads(match['result'])  #返回字典形式的计算结果

def result2csv(result, save_path):
    with open(save_path, 'w', newline='') as csvfile:
        fieldnames = ['torque'] + [str(angal) + '.0' for angal in range(0,27)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for torque, count in result:
            count['torque'] = str(torque)
            writer.writerow(count)

    return True

