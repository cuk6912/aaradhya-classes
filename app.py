from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "aaradhya_secret"

# ---------------- DATABASE CONFIG ----------------

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///local.db"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- MODELS ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    monthly_fee = db.Column(db.Integer)
    join_date = db.Column(db.String(20))
    leave_date = db.Column(db.String(20))


# ---------------- INIT DB ----------------

with app.app_context():

    db.create_all()

    if not User.query.filter_by(username="admin").first():

        admin = User(
            username="admin",
            password="admin123",
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session["user"] = user.username
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    students = Student.query.filter_by(leave_date=None).all()

    total_students = len(students)
    total_revenue = sum([s.monthly_fee for s in students]) if students else 0

    classes = set([s.student_class for s in students])
    subjects = set([s.subject for s in students])

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_revenue=total_revenue,
        total_classes=len(classes),
        total_subjects=len(subjects)
    )


# ---------------- STUDENTS ----------------

@app.route("/students")
def students():

    active_students = Student.query.filter_by(leave_date=None).all()

    history_students = Student.query.filter(Student.leave_date != None).all()

    return render_template(
        "students.html",
        students=active_students,
        history=history_students
    )


@app.route("/add_student", methods=["POST"])
def add_student():

    student = Student(
        name=request.form["name"],
        student_class=request.form["class"],
        subject=request.form["subject"],
        phone=request.form["phone"],
        monthly_fee=request.form["fee"],
        join_date=request.form["join_date"]
    )

    db.session.add(student)
    db.session.commit()

    return redirect("/students")


@app.route("/leave_student/<int:id>", methods=["POST"])
def leave_student(id):

    student = Student.query.get(id)
    student.leave_date = date.today()

    db.session.commit()

    return redirect("/students")


# ---------------- OTHER MODULES ----------------

@app.route("/teachers")
def teachers():
    return render_template("teachers.html")


@app.route("/attendance")
def attendance():
    return render_template("attendance.html")


@app.route("/fees")
def fees():
    return render_template("fees.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")
@app.route("/batches")
def batches():

    batches = Batch.query.all()
    teachers = Teacher.query.all()

    return render_template(
        "batches.html",
        batches=batches,
        teachers=teachers
    )


@app.route("/add_batch", methods=["POST"])
def add_batch():

    batch_name = request.form["batch_name"]
    class_name = request.form["class_name"]
    subject = request.form["subject"]
    teacher_id = request.form["teacher_id"]
    time = request.form["time"]

    batch = Batch(
        batch_name=batch_name,
        class_name=class_name,
        subject=subject,
        teacher_id=teacher_id,
        time=time
    )

    db.session.add(batch)
    db.session.commit()

    return redirect("/batches")
