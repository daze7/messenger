import os, sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/user_info", methods=['POST', 'GET'])
def user_info():
    con = sqlite3.connect('data/datebase/server.db')
    cur = con.cursor()
    cur.execute(f"SELECT id,user_id,name,surname,date_register,password,e_mail,status FROM users")
    value = cur.fetchall()
    cur.close()
    con.close()
    result = {
        "id": None,
        'user_id': None,
        'name': None,
        'surname': None,
        'date_register': None,
        'password': None,
        'e-mail': None,
        'status': None
    }
    for i in value:
        result['id'] = i[0]
        result['user_id'] = i[1]
        result['name'] = i[2]
        result['surname'] = i[3]
        result['date_register'] = i[4]
        result['password'] = i[5]
        result['e-mail'] = i[6]
        result['status'] = i[7]
    return jsonify(result)


@app.route('/check_message', methods=['PORT', 'GET'])
def check_message():
    user_id = request.json.get('user_id')
    con = sqlite3.connect('data/datebase/server.db')
    cur = con.cursor()
    cur.execute(f"SELECT type FROM message "
                f"WHERE {user_id} = for_user_id AND status = 'new'")
    value = cur.fetchone()
    for i in value:
        if value == 'text':
            cur.execute(f"SELECT id,from_user_id,date,text FROM message "
                        f"WHERE {user_id} = for_user_id AND status = 'new'")
            message = cur.fetchall()
            result = {'id': [], 'from_user_id': [], 'date': [], 'text': []}
            for i in message:
                result['id'].append(i[0])
                result['from_user_id'].append(i[1])
                result['date'].append(i[2])
                result['text'].append(i[3])
                cur.execute(f"UPDATE messenger "
                            f"SET status='old' "
                            f"WHERE id = {i[0]}")
                con.commit()
            cur.close()
            con.close()
        if value == 'photo':
            continue
    return jsonify(result)


@app.route('/send_message', methods=['GER', 'POST'])
def send_message():
    for_user_id = request.json.get('for_user_id')
    from_user_id = request.json.get('from_user_id')
    date = request
    text = request.json.get('text')
    con = sqlite3.connect('data/datebase/server.db')
    cur = con.cursor()
    cur.execute(f"INSERT INTO message(for_user_id,from_user_id,date,type,text,photo,status) "
                f"VALUES ('{for_user_id}', ''{from_user_id}), '{date}, '{text}', 'None', 'new')'")
    con.commit()
    return True


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=5000)
