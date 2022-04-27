import datetime
import os, sqlite3

from flask import Flask, jsonify, request, render_template
from werkzeug.utils import redirect

from data import db_session
from data.forms.user_regist import RegisterForm
from data.User import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MESSENGER_SEKRET_KEY'


@app.route("/user_info", methods=['POST', 'GET'])
def user_info():
    con = sqlite3.connect('data/datebase/server.db')
    cur = con.cursor()
    cur.execute("SELECT id,id_user,name,surname,date_register,hashed_password,login,status FROM users")
    value = cur.fetchall()
    cur.close()
    con.close()
    result = {}
    for i in value:
        result[i[0]] = {}
        result[i[0]]['user_id'] = i[1]
        result[i[0]]['name'] = i[2]
        result[i[0]]['surname'] = i[3]
        result[i[0]]['date_register'] = i[4]
        result[i[0]]['password'] = i[5]
        result[i[0]]['login'] = i[6]
        result[i[0]]['status'] = i[7]
    return jsonify(result)


@app.route('/check_server', methods=['POST', 'GET'])
def check_server():
    return True


@app.route('/check_message', methods=['POST', 'GET'])
def check_message():
    user_id = request.json['user_id']
    con = sqlite3.connect('data/datebase/server.db')
    cur = con.cursor()
    cur.execute(f"SELECT type FROM message "
                f"WHERE from_user_id = '{user_id}'")
    if len(cur.fetchall()) == 0:
        return jsonify({'error': 'not found this user_id'})
    cur.execute(f"SELECT type FROM message "
                f"WHERE from_user_id = '{user_id}' AND status = 'new'")
    value = cur.fetchone()
    if len(value) == 0:
        return jsonify({'result': 'no new messages found'})
    cur.execute(f"SELECT id,for_user_id,from_user_id,date,type,text,status FROM message "
                f"WHERE from_user_id = '{user_id}' AND status = 'new' AND type = 'text'")
    messages = cur.fetchall()
    result = {}
    for y in messages:
        result[y][0] = {'for_user_id': y[1], 'from_user_id': y[2], 'date': y[3],
                        'type': y[4], 'text': y[5], 'status': y[6]}
        cur.execute(f"UPDATE messenger "
                    f"SET status='old' "
                    f"WHERE id = '{y[0]}'")
        con.commit()
    cur.close()
    con.close()
    return jsonify(result)


@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    for_user_id = request.json['for_user_id'][0]
    from_user_id = request.json['from_user_id'][0]
    date = request.json['date']
    text = request.json['text']
    con = sqlite3.connect('data/datebase/server.db')
    cur = con.cursor()
    cur.execute(f"INSERT INTO message(for_user_id,from_user_id,date,type,text,photo,status) "
                f"VALUES('{for_user_id}','{from_user_id}','{date}','text','{text}','','new')")
    con.commit()
    cur.close()
    con.close()
    return jsonify({'result': 'ok'})


@app.route('/registration_users', methods=['GET', 'POST'])
def registration_user():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data, login=form.login.data, surname=form.surname.data)
        user.set_password(form.password.data)
        user_id = f'***{form.name.data}{form.surname.data}{datetime.datetime.now()}{form.login.data}***'
        user.set_user_id(user_id)
        db_sess.add(user)
        db_sess.commit()
        return render_template('register.html', title='Регистрация',
                               form=form,
                               message="Успешно")
    return render_template('register.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("data/datebase/server.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=5000)
