from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://wepungsan:719412@cluster0.wx86a.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta_plus_week4

SECRET_KEY = 'SPARTA'

import jwt

from datetime import datetime

import hashlib

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.epl.find({}, {'_id': False}))
        return render_template('index.html', posts=posts)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login"))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/posting')
def posting():
    return render_template('posting.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash})

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/api/post', methods=['POST'])
def api_post():
    title_receive = request.form['title_give']
    team_receive = request.form['team_give']
    content_receive = request.form['content_give']

    file = request.files["file_give"]

    extension = file.filename.split('.')[-1]

    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

    filename = f'file-{mytime}'

    save_to = f'static/{filename}.{extension}'
    file.save(save_to)

    doc = {
        'title': title_receive,
        'content': content_receive,
        'team': team_receive,
        'file': f'{filename}.{extension}'
    }

    db.epl.insert_one(doc)

    return jsonify({'msg': '작성 완료'})

@app.route('/api/check', methods=['POST'])
def api_check():
    check_receive = request.form['check_give']

    id_list = list(db.user.find({'id':check_receive}, {'_id': False}))
    if(len(id_list) > 0):
        return jsonify({'result':'unavailable'})
    else:
        return jsonify({'result':'available'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

