from flask import Flask, render_template, request, redirect, url_for, flash, abort
# render_template: templates 폴더 안의 html 파일을 렌더링
# request: Flask에서 HTTP 요청(GET, POST 등)에 대한 정보를 다루는 데 사용
# redirect: 사용자가 요청한 페이지를 다른 페이지로 리디렉션
# url_for: url 생성
from flask_bootstrap import Bootstrap5
#--------------------------------------
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, backref
from sqlalchemy import Boolean, select
#--------------------------------------
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
#--------------------------------------
import os
from datetime import date
# from functools import wraps                         # 데코레이터 생성 시 원래 함수의 메타데이터 유지
import smtplib                                      # 파이썬 코드로 이메일을 전송하는 모듈
from email.mime.multipart import MIMEMultipart      # 이메일의 본문과 제목 관리
from email.mime.text import MIMEText                # UTF-8로 이메일의 본문 인코딩
#--------------------------------------
import project_morse_code as morse


#--------------------------------------
MY_EMAIL = os.environ.get("MY_EMAIL")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')  #SQLAlchemy 설정 코드
Bootstrap5(app)

#--------------------------------------
login_manager = LoginManager()      # 사용자 인증을 위해 LoginManager 객체 생성
login_manager.init_app(app)         # Flask 애플리케이션에 LoginManager를 연결

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#--------------------------------------
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///users.db")  # 환경변수 DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # 객체 상태 변화 추적 비활성화(메모리 절약)
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    cafes = db.relationship('Cafe', back_populates='author', lazy=True)                        # 한 유저가 Cafe(자식)로 여러 게시물 작성 가능
    cafe_comments = db.relationship('CafeComment', back_populates='comment_author', lazy=True) # 한 유저가 CafeComment(자식)로 여러 댓글 작성 가능

class Cafe(db.Model):
    __tablename__ = 'cafes'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 리스트에 카페를 추가한 user의 id 참조
    author = db.relationship('User', back_populates='cafes')                       # User(부모) 테이블과 관계 설정
    name = db.Column(db.String(250), nullable=False)
    city = db.Column(db.String(250))
    location = db.Column(db.String(250), nullable=False)
    phone_number = db.Column(db.String(250))
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(500), unique=True, nullable=False)
    img_url = db.Column(db.String(500), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    comments = db.relationship('CafeComment', back_populates='parent_cafe', lazy=True)        #

class CafeComment(db.Model):
    __tablename__ = 'cafe_comments'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 카페에 댓글을 작성한 user의 id 참조
    comment_author = db.relationship('User', back_populates='cafe_comments')       # User(부모) 테이블과 관계 설정
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafes.id'), nullable=False)    # 해당 댓글이 달린 카페의 id 참조
    parent_cafe = db.relationship('Cafe', back_populates='comments')               # Cafe(부모) 테이블과 관계 설정
    text = db.Column(db.String(500), nullable=False)


with app.app_context():
    db.create_all()

# home page --------------------------------------------------------------------------------------------
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")

# register new id --------------------------------------------------------------------------------------
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 입력한 이메일이 이미 데이터베이스에 있으면 로그인 페이지로 이동
        if User.query.filter_by(email=request.form.get('email')).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        # 비밀번호 해싱 & 솔팅
        encrypted_password = generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )

        # 데이터베이스에 새 유저 등록
        new_user = User(
            name=request.form.get('name'),
            email=request.form.get('email'),
            password=encrypted_password
        )
        db.session.add(new_user)
        db.session.commit()

        # 새로 등록된 유저 로그인 및 인증 진행
        login_user(new_user)
        return redirect(url_for("logined_page", name=new_user.name))

    return render_template("user_register.html")

# login with created id  -------------------------------------------------------------------------------
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        # 이메일이 데이터베이스에 존재하지 않을 경우 로그인 페이지로 돌아감
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("login"))

        # 입력한 비밀번호의 해시가 해당 유저의 비밀번호 해시값과 다른 경우 로그인 페이지로 돌아감
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for("login"))

        # 이메일이 데이터베이스에 존재하고 비밀번호도 올바를 경우 해당 유저를 Flask-Login으로 인증
        else:
            login_user(user)
            return redirect(url_for("logined_page", name=user.name))

    return render_template("user_login.html")

# logined user page --------------------------------------------------------------------------------------
@app.route('/user/<name>')
@login_required
def logined_page(name):
    return render_template("user_page.html", name=name, email=current_user.email)

# logout --------------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# send email -------------------------------------------------------------------------------------------
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    # (이메일 전송 페이지를 처음 열었을 때는 GET 요청)
    if request.method == "POST":
        data = request.form                                             # contact에서 작성한 이메일 폼 가져오기

        msg = MIMEMultipart()                                                # MIME 객체 생성
        msg["From"] = data["email"]                                          # 보내는 사람의 이메일
        msg["To"] = MY_EMAIL                                                 # 받는 사람(나)의 이메일
        msg["Subject"] = "Message from portfolio website\n\n"                # 이메일 제목 설정
        email_body = (f"Name: {data['name']}\n"                              # 이메일 본문
                      f"Email: {data['emai']}\n"
                      f"Message:\n{data['message']}")
        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))  # 본문에 한글 인코딩 추가

        with smtplib.SMTP("smtp.gmail.com") as connection:              # 이메일 제공자의 SMTP 이메일 서버에 연결
            connection.starttls()                                       # 메시지 암호화
            connection.login(user=MY_EMAIL, password=GMAIL_PASSWORD)    # 로그인
            connection.sendmail(from_addr=data["email"],                # MIME 객체를 문자열로 변환하여 이메일 전송
                                to_addrs=MY_EMAIL,
                                msg=msg.as_string())
        return render_template("contact.html", msg_sent=True)

    # 양식을 입력하고 이메일을 전송한 후에는 POST 요청
    return render_template("contact.html", msg_sent=False)


# sample pages --------------------------------------
@app.route("/sample")  # 샘플 페이지
def sample():
    return render_template("sample_page.html")

@app.route("/elements") # html 사용설명서
def elements():
    return render_template("sample_elements.html")

###############################################################################################################
@app.route("/morse_code_converter", methods=['GET', 'POST'])
def morse_code_converter():
    result = request.args.get('result') # GET 요청의 URL 매개변수에서 result 추출(초기 렌더링 시에는 result 없음)
    user_input = None                   # POST 요청에서 입력값을 처리하기 전까지는 None으로 초기화

    if request.method == 'POST':                    # 폼에서 제출된 데이터 처리
        user_input = request.form.get('string')     # 사용자 입력값 가져오기

        result = morse.str_to_morse(str(user_input))
        # 변환 결과(result)와 입력값(user_input)을 URL 매개변수에 추가하여 GET 요청으로 리다이렉트
        return redirect(url_for('morse_code_converter', result=result, user_input=user_input))

    user_input = request.args.get('user_input')     # 리다이렉션된 URL의 user_input 매개변수 가져오기
    return render_template("project_morse_code.html", result=result, user_input=user_input)

###############################################################################################################
@app.route("/laptop_friendly_cafes", defaults={'selected_city': 'Seoul'}, methods=['GET', 'POST'])  # 기본 도시 값 Seoul
@app.route("/laptop_friendly_cafes/<selected_city>", methods=['GET', 'POST'])
def laptop_friendly_cafes_home(selected_city):
    all_cities = db.session.execute(select(Cafe.city).distinct()).scalars().all()   # city 열에 존재하는 모든 값을 중복없이 모은 리스트

    selected_city = request.args.get('city')    # URL 파라미터로 전달된 city 값을 받아오기
    if not request.args.get('city'):            # city 값이 없으면 기본 도시인 Seoul로 리다이렉트
        return redirect(url_for('laptop_friendly_cafes_home', selected_city='Seoul', city='Seoul'))

    selected_cafes = Cafe.query.filter_by(city=selected_city).all()                 # selected_city에 맞는 카페 리스트 필터링
    return render_template("project_laptop_friendly_cafes_main.html", cafes=selected_cafes, cities=all_cities, selected_city=selected_city)


@app.route("/laptop_friendly_cafes/add", methods=['GET', 'POST'])
def laptop_friendly_cafes_add():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form["name"].strip(),
            city=request.form["city"].strip().capitalize(),
            location=request.form["location"].strip(),
            phone_number=request.form.get("phone_number").strip(),
            has_sockets=bool(request.form.get("has_sockets")),
            has_wifi=bool(request.form.get("has_wifi")),
            has_toilet=bool(request.form.get("has_toilet")),
            seats=request.form["seats"].strip(),
            coffee_price=request.form["coffee_price"].strip(),
            map_url=request.form["map_url"].strip(),
            img_url=request.form["img_url"].strip(),
            date = date.today().strftime("%B %d, %Y"),
            author=current_user    # User 객체 직접 참조
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('laptop_friendly_cafes_home', city=new_cafe.city))
    return render_template("project_laptop_friendly_cafes_add.html")


@app.route('/laptop_friendly_cafes/show/<int:cafe_id>', methods=["GET", "POST"])
def laptop_friendly_cafes_show(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    edit_id = request.args.get("edit", type=int)  # edit 값 정수로 가져오기

    if request.method == "POST":
        comment_id = request.form.get("comment_id")
        text = request.form.get("comment_text")

        if comment_id:  # 댓글 수정
            comment_to_edit = CafeComment.query.get_or_404(int(comment_id))
            if comment_to_edit.comment_author == current_user or current_user.id == 1:
                comment_to_edit.text = text
                db.session.commit()
        else:           # 새 댓글 작성
            new_comment = CafeComment(
                text=text,
                comment_author=current_user,
                parent_cafe=cafe
            )
            db.session.add(new_comment)
            db.session.commit()
        # 리디렉션 시 edit 파라미터 제거
        return redirect(url_for("laptop_friendly_cafes_show", cafe_id=cafe_id))
    # edit_id를 템플릿에 넘겨줌
    return render_template("project_laptop_friendly_cafes_show.html", cafe=cafe, edit_id=edit_id)


@app.route('/laptop_friendly_cafes/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def laptop_friendly_cafes_delete_comment(comment_id):     # 댓글 삭제
    comment = CafeComment.query.get_or_404(comment_id)
    if comment.comment_author.id != current_user.id and current_user.id != 1:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer)


@app.route("/laptop_friendly_cafes/edit/<cafe_id>", methods=['GET', 'POST'])
@login_required
def laptop_friendly_cafes_edit(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    if cafe.author != current_user and current_user.id != 1:    # 권한 없는 사람이 접근하면 Forbidden 에러 반환
        abort(403)

    if request.method == 'POST':
        cafe.name = request.form["name"].strip()
        cafe.city = request.form["city"].strip().capitalize()
        cafe.location = request.form["location"].strip()
        cafe.phone_number = request.form.get("phone_number").strip()
        cafe.has_sockets = bool(request.form.get("has_sockets"))
        cafe.has_wifi = bool(request.form.get("has_wifi"))
        cafe.has_toilet = bool(request.form.get("has_toilet"))
        cafe.seats = request.form["seats"].strip()
        cafe.coffee_price = request.form["coffee_price"].strip()
        cafe.map_url = request.form["map_url"].strip()
        cafe.img_url = request.form["img_url"].strip()
        db.session.commit()
        return redirect(url_for('laptop_friendly_cafes_show', cafe_id=cafe.id))
    # GET 요청 시 수정 폼 보여주기
    return render_template("project_laptop_friendly_cafes_edit.html", cafe=cafe)


@app.route("/laptop_friendly_cafes/delete_cafe/<int:cafe_id>", methods=["POST"])
@login_required
def laptop_friendly_cafes_delete_cafe(cafe_id):
    cafe = Cafe.query.get_or_404(cafe_id)
    if cafe.author != current_user and current_user.id != 1:
        abort(403)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('laptop_friendly_cafes_home', selected_city=cafe.city, city=cafe.city))








# Local server -------------------------------------
## git에 commit할 때:  app.run(debug=False)
## local에서 실행할 때:  app.run(debug=True, host="127.0.0.1", port=5000) → 403 에러 시 5001로 변경
if __name__ == "__main__":
    app.run(debug=False)
    # app.run(debug=True, host="127.0.0.1", port=5001)