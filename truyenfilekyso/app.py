# app.py
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = 'secretkey123'

USERS = ['user_a', 'user_b']

# Tạo thư mục lưu trữ nếu chưa có
for user in USERS:
    os.makedirs(f'storage/{user}/inbox', exist_ok=True)
    os.makedirs(f'storage/{user}/sent', exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username in USERS:
            session['user'] = username
            return redirect('/')
        else:
            return 'Người dùng không hợp lệ!'
    return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        file = request.files['file']
        recipient = request.form['recipient']
        filename = file.filename
        data = file.read()

        # Ký giả lập
        signed_data = b'--SIGNED--' + data

        sender = session['user']
        sent_path = f'storage/{sender}/sent/{filename}.signed'
        inbox_path = f'storage/{recipient}/inbox/{filename}.signed'

        with open(sent_path, 'wb') as f:
            f.write(signed_data)
        with open(inbox_path, 'wb') as f:
            f.write(signed_data)

        return redirect('/sent')
    return render_template('index.html', users=USERS, current=session['user'])

@app.route('/sent')
def sent():
    user = session['user']
    files = os.listdir(f'storage/{user}/sent')
    return render_template('sent.html', files=files)

@app.route('/inbox')
def inbox():
    user = session['user']
    files = os.listdir(f'storage/{user}/inbox')
    return render_template('inbox.html', files=files)

@app.route('/download/<box>/<filename>')
def download(box, filename):
    user = session['user']
    path = f'storage/{user}/{box}'
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
