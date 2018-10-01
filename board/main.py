# -*- coding:utf-8 -*-
from flask import Flask, jsonify, g, request,session, send_from_directory
from flask import render_template,redirect, url_for
from werkzeug import secure_filename
import sqlite3
import hashlib

DATABASE='./db/test.db'
app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','docx'])
app.secret_key ='abcd'
def get_db():
    db = getattr(g, '_database', None)
    if db  is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None: db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def add_register(user_id,user_pw,user_em,nname,pnum):
    pw = hashlib.sha224(user_pw).hexdigest()
    sql = 'INSERT INTO register (user_id, user_pw, user_em,nname,pnum) VALUES ("%s", "%s", "%s", "%s","%s")' %(user_id, pw, user_em, nname, pnum)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def get_user(user_id, user_pw):
    pw = hashlib.sha224(user_pw).hexdigest()
    sql= 'SELECT * FROM register where user_id ="%s" and user_pw ="%s"' %(user_id,pw)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def get_email(user):
    sql = 'SELECT user_em FROM register where user_id="%s"' %(user)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res



@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_id = request.form.get('user_id')
        user_pw = request.form.get('user_pw')
        data = get_user(user_id, user_pw)
        print data
        if len(data) != 0:
            session['is_logged'] = True
            session['user_id'] = user_id
            session['user_pw'] = user_pw
            return redirect(url_for('secret'))
        else:
            return '<script>alert("로그인 실패"); history.go(-1)</script>'

@app.route('/register', methods=['GET', 'POST'])
def user_resgister():
    if request.method == 'GET':
        return render_template('user_register.html')
    else:
        user_id = request.form.get('user_id')
        user_pw = request.form.get('user_pw')
        user_em = request.form.get('user_em')
        nname = request.form.get('nname')
        pnum = request.form.get('pnum')
        if len(confirm_id(user_id)) == 0 and user_id != '':
            add_register(user_id,user_pw,user_em,nname,pnum)
            return redirect(url_for('login'))
        else:
            return '<script>alert("id가 중복됩니다"); history.go(-1)</script>'

def confirm_id(user):
    sql = 'SELECT * FROM register where user_id ="%s"' %(user)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res


@app.route('/secret')
def secret():
    if session['is_logged'] == True:
        userid=session['user_id']
        return render_template('secret.html',userid=userid)
    else:
        return '로그인해주세요<br><a href="/">로그인</a>'


@app.route('/logout')
def logout():
    if session['is_logged'] == True:
        session.pop('is_logged')
        session['is_logged'] = False
        return 'logout<br><a href="/">로그인</a>'

@app.route('/update', methods=['GET','POST'])
def update():
    if request.method =='GET':
        data = read_user(session['user_id'])[0]
        return render_template('update.html', data=data)
    else:
        update_pw = request.form.get('update_pw')
        update_em = request.form.get('update_em')
        update_nname = request.form.get('update_nname')
        update_pnum = request.form.get('update_pnum')
        userid= session['user_id']
        update_data(update_pw, update_em,update_nname,update_pnum,userid)
        session['user_pw'] = update_pw
        session['user_em'] = update_em
        return redirect(url_for("secret"))

def update_data(userpw,em,nname,pnum,user):
    pw = hashlib.sha224(userpw).hexdigest()
    sql = 'UPDATE register SET user_pw = "%s", user_em ="%s", nname="%s", pnum="%s" where user_id = "%s"' %(pw,em,nname,pnum,user)

    db = get_db()
    db.execute(sql)
    res = db.commit()

def read_user(user):
    sql = 'SELECT * FROM register where user_id = "%s"' %(user)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

@app.route('/board')
def board():
    data = read_board()
    return render_template('board.html', data = data)

def read_board():
    sql = 'SELECT * FROM board '
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res
@app.route('/userdel', methods=['GET','POST'])
def userdel():
    if request.method == "GET":
        return render_template('userdel.html',user_id=session['user_id'])
    else:
        pw = request.form.get('pw')
        if pw == session['user_pw']:
            usersdel(session['user_id'],pw)
            session.pop('is_logged')
            session['is_logged']= False
            session.pop('user_id')
            session.pop('user_pw')
            return '<script>alert("계정삭제 완료");</script><a href="/">로그인</a>'
        else:
            return '<script>alert("계정 삭제 실패"); history.go(-1)</script>'

def usersdel(user,password):
    pw= hashlib.sha224(password).hexdigest()
    sql = "DELETE FROM register WHERE user_id ='%s' and user_pw='%s' " %(user,pw)
    db = get_db()
    db.execute(sql)
    res = db.commit()

@app.route('/write',methods=['GET','POST'])
def write_board():
    if request.method == 'GET':
        return render_template('write.html')
    else:
        title = request.form.get('title')
        if title != '':
            data = request.form.get('data')
            user_id = session['user_id']
            if '_file' in request.files:
                f = request.files['_file']
                if f and allowed_file(f.filename):
                    f.save('./uploads/'+secure_filename(f.filename))
                    path = secure_filename(f.filename)
                    write(title, data, user_id,path)
                    return redirect(url_for('board'))
                else:
                    return '<script>alert("not valid extensions"); history.go(-1)</script>'
            else:
                path = ''
                write(title, data, user_id, path)
                return redirect(url_for('board'))
        else:
            return '<script>alert("input title"); history.go(-1)</script>'

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def write(title, data, user,path):
    sql = "INSERT INTO board (title, data, user_id,upload) VALUES ('%s','%s','%s','%s')" %(title, data, user,path)
    db = get_db() 
    rv = db.execute(sql)
    res = db.commit()

@app.route('/data',methods=['GET','POST'])
def board_data():
    index = request.args.get('index')
    session['index']=index
    data = read_data(index)[0]
    session['write']=data['user_id']
    result = request.form.get('replydata')
    reply_list = None
    if result != None and result != '':
        write_reply(result,index,session['user_id'])
    if read_reply(index) != []:
        reply_list = read_reply(index)
    return render_template('data.html', data=data,index_=index,reply_list =reply_list)

def read_reply(index):
    sql ="SELECT * FROM contexttb where myindex = '%s'" %(index)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def write_reply(reply,index,user):
    sql="INSERT INTO contexttb (context,user_id,myindex) VALUES ('%s','%s','%s')" %(reply,user,index) 
    db = get_db()
    rv = db.execute(sql)
    res = db.commit()

def read_data(index):
    sql = "SELECT * FROM board where idx ='%s'" %(index)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    db.commit()
    return res


@app.route('/board_update',methods=['GET','POST'])
def dataupdate1():
    if session['user_id'] == session['write']:
        if request.method=='GET':
            return render_template('board_update.html')
        else:
            tit = request.form.get('title')
            da = request.form.get('data')
            if tit != '':
                data_modi(tit,da,session['index'])
                return render_template('board_update.html',myindex=session['index'])
            else:
                return '<script>alert("제목을 입력해주세요"); history.go(-1)</script>'
    else:
        return '<script>alert("수정권한이 없습니다."); history.go(-1)</script>'

def data_modi(title,data,index):
    sql = "UPDATE board SET title = '%s' where idx = '%s'" %(title,index)
    sql1 = "UPDATE board SET data = '%s' where idx = '%s'" %(data,index)
    db = get_db()
    db.execute(sql)
    db.execute(sql1)
    res = db.commit()

@app.route("/board_delete",methods=['GET','POST'])
def boarddelete():
    if session['user_id'] == session['write']:
        if len(iscontext(session['index'])) == 0:
            board_delete(session['index'])
            return redirect(url_for('board'))
        else:
            return '<script>alert("댓글이 존재합니다."); history.go(-1)</script>'
    else:
        return '<script>alert("삭제 권한이 없습니다."); history.go(-1)</script>'

def board_delete(index):
    sql = "DELETE FROM board where idx = '%s'" %(index)
    db = get_db()
    db.execute(sql)
    res = db.commit()

def iscontext(index):
    sql = "SELECT 1 FROM contexttb where myindex ='%s'" %(index)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    db.commit()
    print res
    return res

@app.route("/modi", methods=['GET','POST'])
def replymodi():
    replyindex = request.args.get('replyindex')
    dataindex = request.args.get('index')
    modi=request.form.get('modireply') 
    remodi(replyindex,dataindex,modi)
    return render_template('replymodi.html',index=dataindex, replyindex=replyindex)

def remodi(replyindex,dataindex,modi):
    sql = "UPDATE contexttb SET context = '%s' where idx= '%s' and myindex = '%s'" %(modi,replyindex,dataindex)
    db = get_db()
    db.execute(sql)
    res = db.commit()

@app.route("/replydelete", methods=['GET','POST'])
def replydele():
    replyindex = request.args.get('replyindex')
    dataindex = request.args.get('index')
    delreply(replyindex,dataindex)
    return '<a href=/board>댓글 삭제완료</a>'

def delreply(replyindex,dataindex):
    sql = "DELETE FROM contexttb WHERE idx='%s' and myindex ='%s' "%(replyindex,dataindex)
    db = get_db()
    db.execute(sql)
    res = db.commit()

@app.route("/upload/<path:filename>", methods=['GET','POST'])
def download(filename):
    return send_from_directory(directory='uploads', filename=filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8081)
