import os
from os import listdir
from uuid import uuid4
from flask import Flask,request,send_from_directory
from common.profile import Profile
from pathlib import Path


app=Flask(__name__)
@app.route('/graph',methods=['GET','POST'])
def upload_graph():
    graph_file =request.files.get('graph')

    if not graph_file:
        return '未上传有效图片'
    graph_path=Profile.get_graph_path()
    graph_id=str(uuid4())
    graph_suffix=Path(graph_file.filename).suffix
    graph_filename=f'{graph_id}{graph_suffix}'
    graph_fullpath=graph_path.joinpath(graph_filename)
    graph_file.save(graph_path.joinpath(graph_filename))
    return f'图片上传成功，id：{graph_id}'


@app.route('/graph/<string:graph_id>')
def download_graph(graph_id):
    target_file=None
    graph_path = Profile.get_graph_path()
    up_folder=str(graph_path)
    for filename in listdir(up_folder):
        if filename.startswith(f'{graph_id}.'):
            target_file=filename
            break
    if target_file:
        return send_from_directory(up_folder,target_file)
    else:
        return '未找到对应图片'



if __name__ == '__main__':
        app.run()

