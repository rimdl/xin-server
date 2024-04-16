import json
import os
import yaml
import uuid
from flask import Blueprint, request
from storage import S3

script_dir = os.path.dirname(os.path.abspath(__file__))
yaml_file_path = os.path.join(script_dir, '..', 'config.yaml')
fileoperate = Blueprint('fileoperate', __name__, url_prefix='/file')
with open(yaml_file_path, 'r') as file:
    config = yaml.safe_load(file)

S3_FILE_URL = os.environ.get('S3_FILE_URL')


@fileoperate.route('/')
def users_index():
    return "This is the file index page."


@fileoperate.route('/upload', methods=['POST'])
def upload():
    uploaded_files = request.files.getlist('files')
    res = []
    if len(uploaded_files) == 0:
        return 'No file found'
    else:
        for uploaded_file in uploaded_files:
            file_suffix = uploaded_file.filename.split('.')[-1]
            unique_id = str(uuid.uuid4())
            filename = unique_id + "." + file_suffix
            if config['storage'] == 'S3':
                up_res = S3.upload(uploaded_file.stream, filename)
                res.append(S3_FILE_URL+"/file/"+up_res)
            else:
                return "Not supported"
    return json.dumps(res)
