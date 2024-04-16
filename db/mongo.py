import json
import os

import pymongo
from bson.json_util import dumps

MONGO_DB = os.environ.get('MONGO_DB')


def find(client, collection, query=None,query2=None, sort=None, limit=None, skip=None):
    if query is None:
        query = {}
    try:
        db = client.get_database(MONGO_DB)
        db_collection = db[collection]
        cursor = None
        if sort is not None and limit is None:
            if sort.get('order') == 'desc':
                cursor = db_collection.find(query,query2).sort(sort.get('key'), pymongo.DESCENDING)
            else:
                cursor = db_collection.find(query,query2).sort(sort.get('key'), pymongo.ASCENDING)
        elif sort is not None and limit is not None:
            if skip is not None:
                if sort.get('order') == 'desc':
                    cursor = db_collection.find(query,query2).sort(sort.get('key'), pymongo.DESCENDING).limit(limit).skip(skip)
                else:
                    cursor = db_collection.find(query,query2).sort(sort.get('key'), pymongo.ASCENDING).limit(limit).skip(skip)
            else:
                if sort.get('order') == 'desc':
                    cursor = db_collection.find(query,query2).sort(sort.get('key'), pymongo.DESCENDING).limit(limit)
                else:
                    cursor = db_collection.find(query,query2).sort(sort.get('key'), pymongo.ASCENDING).limit(limit)
        elif sort is None and limit is not None:
            if skip is not None:
                cursor = db_collection.find(query,query2).limit(limit).skip(skip)
            else:
                cursor = db_collection.find(query,query2).limit(limit)
        elif sort is None and limit is None:
            cursor = db_collection.find(query,query2)
        json_string = dumps(cursor, ensure_ascii=False).encode('utf-8')
        return json.dumps(json.loads(json_string))
    except Exception as e:
        print(e)
        return "[]"


def put_object(client, collection, query=None):
    if query is None:
        query = {}
    try:
        db = client.get_database(MONGO_DB)
        db_collection = db[collection]
        res = db_collection.insert_one(query)
        return res
    except Exception as e:
        print(e)
        return []


def count(client, collection, count_filter=None):
    if count_filter is None:
        count_filter = {}
    try:
        db = client.get_database(MONGO_DB)
        db_collection = db[collection]
        # res = db_collection.estimated_document_count({"category":"openwrt"})
        res = db_collection.count_documents(count_filter)
        print(res)
        return json.dumps(res)
    except Exception as e:
        print(e)
        return []

def replaceDoc(client, collection, query=None, new_object=None):
    if query is None:
        query = {}
    if new_object is None:
        new_object = {}
    try:
        db = client.get_database(MONGO_DB)
        db_collection = db[collection]
        db_collection.replace_one(query, new_object)
        res = {"msg": "success"}
        return json.dumps(res)
    except Exception as e:
        print(e)
        return []


def updateDoc(client, collection, query=None, update_query=None):
    if query is None:
        query = {}
    if update_query is None:
        update_query = {}
    try:
        db = client.get_database(MONGO_DB)
        db_collection = db[collection]
        update_result = db_collection.update_one(query, update_query)
        print("updateResult::",update_result.modified_count)
        res = {"modified_count": update_result.modified_count}
        return json.dumps(res)
    except Exception as e:
        print(e)
        return []


def deleteDoc(client, collection, query=None):
    if query is None:
        query = {}
    try:
        db = client.get_database(MONGO_DB)
        db_collection = db[collection]
        deleteResult = db_collection.delete_one(query)
        #DeleteResult({'n': 1, 'electionId': ObjectId('7fffffff0000000000000156'), 'opTime': {'ts': Timestamp(1712995656, 8), 't': 342}, 'ok': 1.0, '$clusterTime': {'clusterTime': Timestamp(1712995656, 8), 'signature': {'hash': b'N\xa7\x9fxq}:\xd9\x86\xe9\x93\x11\xa60\xd5\x1f^\xa0U$', 'keyId': 7299612402079760385}}, 'operationTime': Timestamp(1712995656, 8)}, acknowledged=True)
        res = {"deleted_count": deleteResult.deleted_count}
        return json.dumps(res)
    except Exception as e:
        print(e)
        return []