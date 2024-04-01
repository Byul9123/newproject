# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
app = Flask(__name__)

# DB 기본 코드
import os
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

## DB Person 테이블 생성
class Person(db.Model):
    person_id = db.Column(db.Integer, primary_key=True)
    person_like = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'{self.person_id} | {self.person_like}'

## DB book 테이블 생성
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, nullable=False)
    book_text = db.Column(db.String(1000), nullable=True)
    insert_dt = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'{self.book_id} | {self.person_id} | {self.book_text} | {self.insert_dt}'

with app.app_context():
    db.create_all()

@app.route("/")
def home():

    ## DB Person 테이블 데이터 가져오기
    person_list = Person.query.all()
    print(person_list)

    ## DB Book 데이블 데이터 가져오기
    book_list = Book.query.all()
    print(book_list)

    return render_template('index.html',data = person_list, book = book_list)

## 좋아요 기능 구현
@app.route("/addLike")
def add_like():

    ## html 에서 데이터 가져오기 ( 어느 프로필에서 좋아요를 클릭했는지 )
    person_id = request.args.get("person_id")
    print(person_id)

    ## DB에 해당하는 프로필 데이터 좋아요수 업데이트
    person = Person.query.filter_by(person_id = person_id).first()
    person.person_like = person.person_like + 1
    db.session.commit()

    return redirect(url_for('home'))

## 방명록 기능 구현
@app.route("/addBook")
def add_book():

    ## html에서 데이터 가져오기
    book_text = request.args.get("book_text")
    person_id = request.args.get("person_id")

    ## DB에 해당하는 프로필( person_id )에 맞게 방명록 등록
    book = Book( person_id = person_id, book_text = book_text)
    db.session.add(book)
    db.session.commit()

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)