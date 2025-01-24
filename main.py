from flask import Flask, render_template, request, redirect, url_for
# render_template: templates 폴더 안의 html 파일을 렌더링
# request: Flask에서 HTTP 요청(GET, POST 등)에 대한 정보를 다루는 데 사용
# redirect: 사용자가 요청한 페이지를 다른 페이지로 리디렉션
# url_for: url 생성
import project_morse_code as morse
import os
import smtplib                                      # 파이썬 코드로 이메일을 전송하는 모듈
from email.mime.multipart import MIMEMultipart      # 이메일의 본문과 제목 관리
from email.mime.text import MIMEText                # UTF-8로 이메일의 본문 인코딩

MY_EMAIL = os.environ.get("MY_EMAIL")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")

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


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    # 이메일 전송 페이지를 처음 열었을 때는 GET 요청
    if request.method == "POST":
        data = request.form                                             # contact에서 작성한 이메일 폼 가져오기

        msg = MIMEMultipart()                                                # MIME 객체 생성
        msg["From"] = data["email"]                                          # 보내는 사람의 이메일
        msg["To"] = MY_EMAIL                                                 # 받는 사람(나)의 이메일
        msg["Subject"] = "Message from portfolio website\n\n"                # 이메일 제목 설정
        email_body = (f"Name: {data["name"]}\n"                              # 이메일 본문
                      f"Email: {data["email"]}\n"
                      f"Message:\n{data["message"]}")
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


@app.route("/sample")  # 샘플 페이지
def sample():
    return render_template("sample_page.html")

@app.route("/elements") # html 사용설명서 페이지
def elements():
    return render_template("sample_elements.html")

################################################  로컬 서버 구동  ################################################
if __name__ == "__main__":
    app.run(debug=False)

    # app.run(debug=True, host="127.0.0.1", port=5001)