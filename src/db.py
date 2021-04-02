import pymongo

def get_db():
    client = pymongo.MongoClient()
    db = client['results']
    return db