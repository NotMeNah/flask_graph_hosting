from flask import jsonify

def make_response(code=200,msg="操作成功",data=None):
    return jsonify({
        "code":code,
        "msg":msg,
        "data":data
    }),code
