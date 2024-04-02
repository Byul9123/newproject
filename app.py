from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
# 로그인 관련
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# DB 기본 코드
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


# DB User 테이블 생성
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), nullable=False)
    userID = db.Column(db.String(14), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'{self.userID} | {self.username} | {self.userID} | {self.password_hash}'


# DB Post 테이블 생성
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    content = db.Column(db.String(1000), nullable=False)
    post_text = db.Column(db.String(1000), nullable=True)
    likes = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'{self.id} | {self.userID} | {self.content} | {self.post_text} | {self.timestamp}'

    # User 모델과의 관계 추가
    user = db.relationship('User', backref=db.backref('posts', lazy=True))


with app.app_context():
    db.create_all()


@app.route("/")
def home():

    # DB User 테이블 데이터 가져오기
    user_list = User.query.all()

    # DB Post 데이블 데이터 가져오기
    post_list = Post.query.all()

    return render_template('index.html', user=user_list, posts=post_list)


# 회원가입
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        userID = request.form['userID']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, userID=userID,
                        password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('회원가입에 성공하였습니다!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html')


# 로그인 관련
@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))


# 로그인 페이지
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']

        user = User.query.filter_by(userID=userID).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return 'Invalid username or password'
    return render_template('index.html')


# 로그아웃
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# 좋아요 기능 구현
@app.route("/addLike/<int:post_id>", methods=["POST"])
def add_like(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        post.likes += 1  # 좋아요 수 증가
        db.session.commit()
        return jsonify({"success": "Like added successfully", "current_likes": post.likes})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 포스트 생성
@app.route("/posts/create", methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content')
    if content:
        new_post = Post(content=content, userID=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('새 포스트가 성공적으로 생성되었습니다.')
        return redirect(url_for('home'))
    else:
        flash('포스트 내용을 입력해주세요.')
    return render_template('index.html')

# 포스트 조회


@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        posts = Post.query.all()
        posts_data = [
            {'id': post.id, 'content': post.content, 'timestamp': post.timestamp}
            for post in posts]
        print(posts_data)
        return jsonify(posts_data)
    except Exception as e:
        return jsonify({"error": str(e)})


# 포스트 삭제
@app.route("/posts/delete/<int:post_id>", methods=["DELETE"])
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"success": "Post deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
