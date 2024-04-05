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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'database.db')
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


# 좋아요 모델
class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    liked = db.Column(db.Boolean, default=False)


# DB 생성

# DB book 테이블 생성
class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id')) #추가
    book_text = db.Column(db.String(1000), nullable=True)
    insert_dt = db.Column(db.DateTime, default=datetime.now)

    # user = db.relationship('User', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f'{self.book_id} | {self.userID} | {self.post_id} | {self.book_text} | {self.insert_dt}'


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

        new_user = User(username=username, userID=userID,
                        password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('회원가입에 성공하였습니다!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# 로그인관련
@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))


# 홈
@app.route("/")
def home():
    user_list = User.query.all()
    post_list = Post.query.all()

    # Likes 리스트
    like_list = []
    if current_user.is_active:
        like_list = Likes.query.filter_by(
            user_id=current_user.id, liked=1).all()
    likes_list = [like.post_id for like in like_list]

    # Book 리스트
    book_list = Book.query.all()

    return render_template('index.html', user=user_list, posts=post_list, likes=likes_list, books=book_list)


# 로그인
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


@app.route("/posts/create", methods=['GET', 'POST'])

# 포스트 생성
@app.route("/posts/create", methods=['POST'])

@login_required
def home1():
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
                app.logger.error(
                    f"Error during image upload or database save: {str(e)}")
                flash('이미지 업로드 또는 데이터베이스 저장 중 오류가 발생했습니다.', 'error')
        else:
            flash('올바른 이미지 파일을 업로드해주세요.', 'error')

        return redirect(url_for('home'))

    # DB User 테이블 데이터 가져오기
    user_list = User.query.all()

    # DB Post 데이블 데이터 가져오기
    post_list = Post.query.all()
    return render_template('index.html', user=user_list, posts=post_list)


# 포스트 삭제
@app.route("/posts/delete/<int:post_id>", methods=["DELETE"])
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    try:
        Book.query.filter_by(post_id=post_id).delete() #추가: 댓글 정보 삭제
        Likes.query.filter_by(post_id=post_id).delete() #추가: 좋아요 정보 삭제
        print("post_id:", post_id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({"success": "Post deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 댓글 작성
@app.route("/addBook", methods=['POST'])
@login_required
def add_book():
    
    if request.method == 'POST':
        # HTML에서 데이터 가져오기
        userID = request.form.get("userID")
        book_text = request.form.get("book_text")
        post_id = request.form.get("post_id")
        # DB에 해당하는 프로필(userID)에 맞게 방명록 등록
        book = Book(userID=userID, post_id=post_id, book_text=book_text)
        db.session.add(book)
        db.session.commit()
        
        return redirect(url_for('home'))

# 댓글 수정
@app.route("/book/edit/<int:book_id>", methods=['PATCH'])
def edit_book(book_id):
    data = request.get_json()
    updated_book_text = data.get('book_text')
    book = Book.query.get(book_id)
    if book:
        book.book_text = updated_book_text
        db.session.commit()
        return jsonify({"success": "Book updated successfully"}), 200

    else:
        return jsonify({"error": "Book not found"}), 404


# 댓글 삭제
@app.route("/book/delete/<int:book_id>", methods=["DELETE"])
def book_delete(book_id):
    book = Book.query.get_or_404(book_id)
    try:
        print("book_id:", book_id)
        db.session.delete(book)
        db.session.commit()
        return jsonify({"success": "Book deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 포스트 수정
@app.route("/posts/edit/<int:post_id>", methods=["PATCH"])
def edit_post(post_id):
    data = request.get_json()
    updated_content = data.get('content')
    post = Post.query.get(post_id)
    if post:
        post.content = updated_content
        db.session.commit()
        return jsonify({"success": "Post updated successfully"}), 200
    else:
        return jsonify({"error": "Post not found"}), 404
    


# 좋아요 기능 구현
@app.route("/addLike/<int:post_id>", methods=["POST"])
@login_required
def add_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Likes.query.filter_by(
        user_id=current_user.id, post_id=post_id).first()
    if not like:
        like = Likes(user_id=current_user.id, post_id=post_id, liked=True)
        db.session.add(like)
        post.likes += 1
    else:
        if like.liked:
            post.likes -= 1
        else:
            post.likes += 1
        like.liked = not like.liked
    db.session.commit()
    return jsonify({"success": "Like added successfully", "current_likes": post.likes})


if __name__ == "__main__":
    app.run(debug=True)
