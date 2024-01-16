from flask import Flask, render_template, request, send_file, session, redirect, url_for
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from helpers.minio_actions import (
    upload_to_minio,
    get_files,
    download_from_minio,
    delete_from_minio,
    check_if_object_exist,
)

app = Flask(__name__, static_url_path="/assets", static_folder="assets")
load_dotenv("./.env")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@127.0.0.1/admindb'  # Укажите свои данные для подключения
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Папка, в которой будут храниться загруженные файлы
UPLOAD_FOLDER = os.environ.get("MINIO_BUCKET")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "docx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    if "username" in session:
        # filenames = os.listdir(app.config["UPLOAD_FOLDER"])
        filenames = get_files(bucket=UPLOAD_FOLDER)
        return render_template(
            "dashboard.html", username=session["username"], filenames=filenames
        )
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # В данном примере используется простая имитация аутентификации
        if username == "admin" and password == "password":
            session["username"] = username
            return redirect(url_for("index"))

        return "Invalid username or password"

    return render_template("login.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "username" in session:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            result = upload_to_minio(file=file, bucket=UPLOAD_FOLDER)
            if result:
                return redirect(url_for("index"))

    return redirect(url_for("login"))


@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    if "username" in session:
        response = download_from_minio(filename=filename, bucket=UPLOAD_FOLDER)
        return send_file(
            response,
            as_attachment=True,
            mimetype=response.headers["content-type"],
            download_name=filename,
        )
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/delete/<filename>")
def delete_file(filename):
    if "username" in session:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        delete_from_minio(filename=filename, bucket=UPLOAD_FOLDER)
        return redirect(url_for("index"))

        return "File not found"
    return redirect(url_for("login"))

@app.route("/create_user", methods=["GET", "POST"])
def create_user():
    if "username" in session and session["username"] == "admin":
        if request.method == "POST":
            username = request.form["new_username"]
            password = request.form["new_password"]

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("index"))  # После создания пользователя переходим на главную страницу

        return render_template("create_user.html")

    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    app.run(host="0.0.0.0", port="5000",debug=False)
