from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# 로그인 관련
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# DB 설정
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)

# User 모델
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), nullable=False)
    userID = db.Column(db.String(14), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Post 모델
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    content = db.Column(db.String(1000), nullable=False)
    post_text = db.Column(db.String(1000), nullable=True)
    likes = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    image_path = db.Column(db.String(100), nullable=True)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))

# DB 생성
with app.app_context():
    db.create_all()

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        userID = request.form['userID']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, userID=userID, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('회원가입에 성공하였습니다!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# 로그인
@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']

        user = User.query.filter_by(userID=userID).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('유효하지 않은 사용자 이름 또는 비밀번호입니다.', 'error')
            return redirect(url_for('login'))

    return render_template('index.html')

# 로그아웃
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# 이미지 업로드
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/posts/create", methods=['GET','POST'])
@login_required
def home():
    if request.method == 'POST':
        post_content = request.form.get('content')
        image_file = request.files.get('imageUpload')

        # Create a new post object
        new_post = Post(content=post_content, user=current_user)

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                image_file.save(image_path)
                new_post.image_path = image_path  # Set image path after successful save
                db.session.add(new_post)
                db.session.commit()
                flash('새 포스트가 성공적으로 생성되었습니다.', 'success')
            except Exception as e:
                # Log the error for better debugging
                app.logger.error(f"Error during image upload or database save: {str(e)}")
                flash('이미지 업로드 또는 데이터베이스 저장 중 오류가 발생했습니다.', 'error')
        else:
            flash('올바른 이미지 파일을 업로드해주세요.', 'error')

        return redirect(url_for('home'))

    # DB User 테이블 데이터 가져오기
    user_list = User.query.all()

    # DB Post 데이블 데이터 가져오기
    post_list = Post.query.all()
    return render_template('index.html', user=user_list, posts=post_list)

if __name__ == "__main__":
    app.run(debug=True)


# 포스트 수정

@app.route("/posts/edit/<int:post_id>", methods=["PATCH"])
def edit_post(post_id):
    data = request.get_json()  # JSON 형식의 요청 본문을 파싱
    updated_content = data.get('content')

    # 데이터베이스에서 해당 포스트를 찾아서 내용을 업데이트합니다.
    post = Post.query.get(post_id)
    if post:
        post.content = updated_content
        db.session.commit()
        return jsonify({"success": "Post updated successfully"}), 200
    else:
        return jsonify({"error": "Post not found"}), 404
