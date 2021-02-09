from flask import Flask, render_template, request, abort
import secrets
import pymysql
from sqlalchemy import Table, Column, Integer, String, create_engine, MetaData

app = Flask(__name__)

engine = create_engine('mysql+pymysql://uahbjr2zeau57agp:pme0dnemttcv0233@r6ze0q02l4me77k3.chr7pe7iynqr.eu-west-1.rds.amazonaws.com:3306/dpn3gul2huaqjq1l')
connection = engine.connect()

meta = MetaData(engine)
user_email = Table('user_email', meta, autoload = True)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/send_email/', methods=['post'])
def login():
    if request.method == 'POST':
        email_t = request.form.get('email')

    is_exist = 0

    query = user_email.select().where(user_email.c.email == email_t)
    result = connection.execute(query)
    for row in result:
        is_exist = 1

    if is_exist == 0:
        token = secrets.token_urlsafe(30)
        query = user_email.insert().values(email = email_t, token = token)
        connection.execute(query)  
        return render_template('send_ok.html', title = 'Link create', link = '/user/' + str(token))
    else:
        query = user_email.select().where(user_email.c.email == email_t)
        result = connection.execute(query)
        for row in result:
            token = row[1]
            print(token)
        return render_template('send_ok.html', title = 'Your link already exists', link = '/user/' + str(token))

@app.route('/user/<string:token>')
def email_link(token):
    is_exist = 0

    query = user_email.select().where(user_email.c.token == token)
    result = connection.execute(query)
    for row in result:
        is_exist = 1

    if is_exist == 0:
        return 'This user does not exist'
    else:
        query = user_email.update().where(user_email.c.token == token).values(count = user_email.c.count + 1)
        connection.execute(query)

        query = user_email.select(user_email.c.count).where(user_email.c.token == token)
        result = connection.execute(query)
        cnt = 0
        for row in result:
            cnt = row[2]

        return render_template('link_cnt.html', cnt = cnt)

if __name__ == '__main__':
    app.run()