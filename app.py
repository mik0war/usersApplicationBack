import os

import psycopg2
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, flash, send_from_directory

app = Flask(__name__)

def get_connection():
    connection = psycopg2.connect(database="users_application", user="administrator",
                                  password="root", host="localhost", port="5432")

    cursor = connection.cursor()

    return connection, cursor

def close_connection(conn, cur):
    conn.close()
    cur.close()

class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/create', methods=['POST'])
def create_user():
    login = request.form['login']
    password = request.form['password']

    connection, cursor = get_connection()

    cursor.execute('''INSERT INTO USERS(login, password) 
                        VALUES (%s, %s);''', (login, password))

    connection.commit()

    close_connection(connection, cursor)
    return redirect(url_for('index'))

@app.route('/user/create/mob', methods=['POST'])
def create_user_mob():
    json = request.json
    login = json['login']
    password = json['pass']

    connection, cursor = get_connection()
    try:

        cursor.execute('''INSERT INTO USERS(login, password) 
                            VALUES (%s, %s);''', (login, password))

        connection.commit()


    except Exception:
        return abort(400, 'Login must be unique')
    finally:
        connection.close()
        cursor.close()
    return jsonify(success='ok')

@app.route('/user/all')
@app.route('/user/<int:user_id>')
def get_user(user_id=None):
    connection, cursor = get_connection()

    if user_id is None:
        cursor.execute('''SELECT login, password FROM USERS''')
        users_data = cursor.fetchall()
        close_connection(connection, cursor)
        return [User(i[0], i[1]).__dict__ for i in users_data]

    cursor.execute('''
        SELECT * 
        FROM USERS 
        WHERE user_order=%s''', [user_id])

    user_data = cursor.fetchall()
    close_connection(connection, cursor)
    if user_data.__len__() == 0:
        return abort(404, f"User with id {user_id} not found")

    return User(user_data[0][0], user_data[0][1]).__dict__


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
