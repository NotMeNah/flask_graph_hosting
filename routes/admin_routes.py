import os
from os import listdir
from uuid import uuid4
from flask import Flask,request,send_from_directory,jsonify
from common.profile import Profile
from pathlib import Path
import base64


app=Flask(__name__)
app.config['MAX_CONTENT_LENGTH']=200*1024*1024

def file_to_base(file):
    data=file.read()
    base64_data=base64.b64encode(data).decode('utf-8')
    return base64_data

@app.errorhandler(413)
def file_too_large(error):
    return '文件过大啦！最大支持200MB的图片捏！',413

@app.route('/graph',methods=['GET','POST'])
def upload_graph():
    graph_file =request.files.get('graph')
    if not graph_file:
        return '未上传有效图片'

    graph_path=Profile.get_graph_path()
    graph_id=str(uuid4())
    graph_suffix=Path(graph_file.filename).suffix

    graph_suffix_lower=graph_suffix.lower()
    ALLOW_SUFFIX={'.png','.jpeg','.gif','.jpg'}
    if graph_suffix_lower not in ALLOW_SUFFIX:
        return '文件类型错误，仅支持png、jpeg、gif、jpg文件'
    graph_filename=f'{graph_id}{graph_suffix}'
    graph_fullpath=graph_path.joinpath(graph_filename)
    graph_file.save(graph_fullpath)
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
        return_format=request.args.get('format','stream').lower()

        if return_format=='base64':
            file_full_path=graph_path.joinpath(target_file)
            try:
                with open(file_full_path,'rb')as f:
                    base64_str=file_to_base(f)
                    return jsonify({
                        'code':200,
                        'msg':'获取base64成功',
                        'data':{
                            'graph_id':graph_id,
                            'base64_str':base64_str,
                            'file_format':target_file.split('.')[-1]
                        }
                    })
            except Exception as e:
                return jsonify({'code':500,'msg':f'转换Base64失败：{str(e)}'}),500
        else:
            return send_from_directory(up_folder,target_file)
    else:
        return '未找到对应图片'



if __name__ == '__main__':
        app.run()

