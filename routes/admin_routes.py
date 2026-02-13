from os import listdir
from uuid import uuid4
from flask import Flask,request,send_from_directory,jsonify,Blueprint
from flask_login import login_required,current_user

from common.profile import Profile
from pathlib import Path
import base64

from models.graph import Graph
from enter.extensions import db

admin_bp=Blueprint('admin',__name__)

def file_to_base(file):
    data=file.read()
    base64_data=base64.b64encode(data).decode('utf-8')
    return base64_data

@admin_bp.errorhandler(413)
def file_too_large(error):
    return '文件过大啦！最大支持200MB的图片捏！',413

@admin_bp.route('/graph',methods=['GET','POST'])
@login_required
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

    permission=request.form.get('permission','private')
    if permission not in ['public','private']:
        return '权限只能是public或private'

    graph_filename=f'{graph_id}{graph_suffix}'
    graph_fullpath=graph_path.joinpath(graph_filename)
    graph_file.save(graph_fullpath)

    new_graph=Graph(
        graph_uuid=graph_id,
        permission=permission,
        user_id=current_user.id
    )
    db.session.add(new_graph)
    db.session.commit()

    return f'图片上传成功，id：{graph_id}'


@admin_bp.route('/graph/<string:graph_id>')
def download_graph(graph_id):
    target_file=None
    graph_path = Profile.get_graph_path()
    up_folder=str(graph_path)

    graph=Graph.query.filter_by(graph_uuid=graph_id).first()
    if not graph:
        return '未找到对应图片'

    if graph.permission =='private':
        if not current_user.is_authenticated:
            return '请先登录',401
        if graph.user_id!=current_user.id:
            return '无权限访问私有图片'

    for filename in listdir(up_folder):
        if filename.startswith(f'{graph_id}.'):
            target_file=filename
            break

    if  not target_file:
        return '未找到对应图片'
    return_format=request.args.get('format','stream').lower()

    if return_format!='base64':
        return send_from_directory(up_folder, target_file)
    file_full_path=graph_path.joinpath(target_file)

    try:
        with open(file_full_path,'rb')as f:
            base64_str=file_to_base(f)
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'转换Base64失败：{str(e)}'}), 500

    return jsonify({
        'code':200,
        'msg':'获取base64成功',
        'data':{
            'graph_id':graph_id,
            'base64_str':base64_str,
            'file_format':Path(target_file).suffix[1:]
        }
    })