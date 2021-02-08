from flask import Flask, render_template, request, abort
import secrets
import pymysql

app = Flask(__name__)

connection = pymysql.connect(host = 'r6ze0q02l4me77k3.chr7pe7iynqr.eu-west-1.rds.amazonaws.com', 
    user = 'uahbjr2zeau57agp', passwd = 'pme0dnemttcv0233', db = 'dpn3gul2huaqjq1l')                         
cursor = connection.cursor()

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/send_email/', methods=['post'])
def login():
    if request.method == 'POST':
        email_t = request.form.get('email')
        
    if cursor.execute('SELECT * FROM user_email WHERE email=%s', email_t) == 0:
        token = secrets.token_urlsafe(30)
        cursor.execute('INSERT INTO user_email (email, token) VALUES (%s, %s)', (email_t, token))
        connection.commit()  
        return render_template('send_ok.html', title = 'Link create', link = '/user/' + str(token))
    else:
        cursor.execute('SELECT token FROM user_email WHERE email=%s', email_t)
        token = cursor.fetchone()[0]
        return render_template('send_ok.html', title = 'Your link already exists', link = '/user/' + str(token))

@app.route('/user/<string:token>')
def email_link(token):
    if cursor.execute('SELECT * FROM user_email WHERE token=%s', token) == 0:
        return 'This user does not exist'
    else:
        cursor.execute('UPDATE user_email SET count = count + 1 WHERE token=%s', token)
        connection.commit()
        cursor.execute('SELECT count FROM user_email WHERE token=%s', token)
        cnt = cursor.fetchone()[0]
        return render_template('link_cnt.html', cnt = cnt)

if __name__ == '__main__':
    app.run()