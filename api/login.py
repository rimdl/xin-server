import io
import json
import os
import requests
import yaml
from flask import Blueprint, current_app, request, url_for, redirect, jsonify, send_file
from db import mongo
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt
)
from utils import captcha
from utils import cacheutil


script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, '..', 'config.yaml')
login = Blueprint('login', __name__, url_prefix='/login')
GITEE_SECRET = os.environ.get('GITEE_SECRET')

with open(yaml_file_path, 'r') as file:
    config = yaml.safe_load(file)


@login.route('/')
def papers_index():
    print("执行一次index")
    return "This is the login index page."


@login.route('/gitee')
def gitee_login():
    code = request.args.get('code')
    state = request.args.get('state')
    redirect_uri = "http://192.168.4.102:5000/api/login/gitee"
    auth_url = f"https://gitee.com/oauth/token?grant_type=authorization_code&code={code}&client_id={config['gitee']['client_id']}&redirect_uri={redirect_uri}&client_secret={GITEE_SECRET}"
    resp = requests.post(auth_url)
    res = getuser_from_gitee(resp.json()['access_token'])
    if res:
        print(res)
    new_redirect_uri = config['base_url'] + state + '?access_token=' + resp.json()[
        'access_token'] + '&expires_in=' + str(resp.json()['expires_in']) + '&login_type=gitee'
    return redirect(new_redirect_uri)


def getuser_from_gitee(access_token):
    client = current_app.extensions['mongo_client']
    user_data = requests.get("https://gitee.com/api/v5/user?access_token="+access_token)
    if user_data.status_code == 200:
        userid = user_data.json()['id']
        username = user_data.json()['name']
        avatar = user_data.json()['avatar_url']
        email = user_data.json()['email']
        db_user = mongo.find(client, 'users', query={'userid': 'gitee:'+str(userid)})
        print(db_user,"---------")
        if not json.loads(db_user):
            res = mongo.put_object(client, "users",{'userid': 'gitee:'+str(userid),'username': username,'avatar':avatar,'email':email,'role': 'user','password': ''})
            return res
    else:
        print(user_data.status_code)
        return False

@login.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    role = get_jwt().get('role')
    print(role)
    if role == 'admin':
        # 获取当前用户的身份
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200
    else:
        return {"msg": "not admin"}, 403


@login.route("/captcha")
def get_captcha():
    id = request.args.get("id")
    code = captcha.generate_random_string(4)
    print(os.getcwd())
    image = captcha.create_captcha_image(code,os.getcwd()+"/font.ttf")
    save_captcha(id,code)
    image.save("captcha.jpg")
    buffer = io.BytesIO()
    image.save(buffer,'JPEG')
    buffer.seek(0)
    return send_file(buffer, mimetype='image/jpeg')

def save_captcha(id,code):
    cacheutil.set_in_global_cache(id, code)
    print(id)