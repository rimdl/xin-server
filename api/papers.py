import json
import os

from bson import ObjectId
from flask import Blueprint, current_app, request
from flask_jwt_extended import jwt_required, get_jwt

from db import mongo

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, '..', 'config.yaml')
papers = Blueprint('papers', __name__, url_prefix='/papers')


@papers.route('/')
def papers_index():
    client = current_app.extensions['mongo_client']
    count_filter = request.args.get('count_filter')
    if count_filter is None:
        count_filter = {}
    else:
        count_filter = json.loads(count_filter)
    data = mongo.count(client, 'papers', count_filter=count_filter)
    return data


@papers.route('/getallpapers')
def getallpapers():
    client = current_app.extensions['mongo_client']
    papers_data = mongo.find(client, 'papers',sort={'key': 'date','order': 'desc'})
    return papers_data


@papers.route('/getpaperslimit')
def getpaperslimit():
    client = current_app.extensions['mongo_client']
    limit = request.args.get('limit')
    skip = request.args.get('skip')
    if limit is not None:
        if skip is not None:
            papers_data = mongo.find(client, 'papers', sort={'key': 'date', 'order': 'desc'}, limit=int(limit),skip=int(skip))
        else:
            papers_data = mongo.find(client, 'papers', sort={'key': 'date', 'order': 'desc'}, limit=int(limit))
        return papers_data
    else:
        return "Please input the limit number!"


@papers.route('/getpaperbyid')
def getpaperbyid():
    client = current_app.extensions['mongo_client']
    id = request.args.get('_id')
    papers_data = mongo.find(client, 'papers', {'_id': ObjectId(id)})
    print(papers_data)
    return papers_data



@papers.route('/getpaperswords')
def getpaperswords():
    client = current_app.extensions['mongo_client']
    papers_data = mongo.find(client, 'papers', query={}, query2={'words':1,'_id':0})
    return papers_data


@papers.route('/getpapersbycategory')
def getpapersbycategory():
    client = current_app.extensions['mongo_client']
    limit = request.args.get('limit')
    skip = request.args.get('skip')
    category = request.args.get('category')
    if limit is not None:
        if skip is not None:
            papers_data = mongo.find(client, 'papers',query={'category':category}, sort={'key': 'date', 'order': 'desc'}, limit=int(limit),skip=int(skip))
        else:
            papers_data = mongo.find(client, 'papers', query={'category':category},sort={'key': 'date', 'order': 'desc'}, limit=int(limit))
        return papers_data
    else:
        return "Please input the limit number!"



@papers.route('/getpapersbytag')
def getpapersbytag():
    client = current_app.extensions['mongo_client']
    limit = request.args.get('limit')
    skip = request.args.get('skip')
    tag = request.args.get('tag')
    tag = tag
    if limit is not None:
        if skip is not None:
            papers_data = mongo.find(client, 'papers',query={'tags': {"$regex":"^"+tag}}, sort={'key': 'date', 'order': 'desc'}, limit=int(limit),skip=int(skip))
        else:
            papers_data = mongo.find(client, 'papers', query={'tags': {"$regex":"^"+tag}},sort={'key': 'date', 'order': 'desc'}, limit=int(limit))
        print(papers_data)
        return papers_data
    else:
        return "Please input the limit number!"


@papers.route('/searchpapers')
def searchpapers():
    client = current_app.extensions['mongo_client']
    col = request.args.get('col')
    limit = request.args.get('limit')
    skip = request.args.get('skip')
    keyword = request.args.get('keyword')
    papers_data = mongo.find(client, 'papers',query={col:{'$regex':keyword}},query2={col:1,'title':1},sort={'key': 'date','order': 'desc'})
    return papers_data


@papers.route('/countpapergtedate')
def countpapergtedate():
    client = current_app.extensions['mongo_client']
    date = request.args.get('date')
    papers_data = mongo.find(client, 'papers',query={"date":{'$gte':date}},sort={'key': 'date','order': 'desc'})
    return papers_data


@papers.route('/addpaper', methods=['POST'])
@jwt_required()
def addpaper():
    role = get_jwt().get('role')
    if role == 'admin':
        client = current_app.extensions['mongo_client']
        paper = request.get_json()
        print(paper)
        mongo.put_object(client, 'papers', paper)
        res = {
            "msg": "success"
        }
        return json.dumps(res)
    else:
        return {"msg": "not admin"}, 403


@papers.route('/updatepaper', methods=['POST'])
@jwt_required()
def updatepaper():
    role = get_jwt().get('role')
    if role == 'admin':
        client = current_app.extensions['mongo_client']
        data = request.get_json()
        print(data)
        query = {"_id": ObjectId(data.get('paperid'))}
        update_query = {"$set":data.get('paper')}
        res = mongo.updateDoc(client, 'papers', query=query,update_query=update_query)
        return res
    else:
        return {"msg": "not admin"}, 403



@papers.route('/deletepaper', methods=['DELETE'])
@jwt_required()
def deletepaper():
    role = get_jwt().get('role')
    if role == 'admin':
        client = current_app.extensions['mongo_client']
        idList = request.get_json()
        print(idList)
        deleted_count = 0
        for item in idList:
            _id = item['_id']
            delete_res = mongo.deleteDoc(client, 'papers', query={'_id': ObjectId(_id.get('$oid'))})
            deleted_count += json.loads(delete_res).get("deleted_count")
        return json.dumps({"deleted_count": deleted_count})
    else:
        return {"msg": "not admin"}, 403
