from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

app = Flask(__name__)

# DATABASE CONFIG
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# MODELS
# =========================

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(100))
    class_name = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    time = db.Column(db.String(50))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    monthly_fee = db.Column(db.Integer)

    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'))

    join_date = db.Column(db.Date)
    leave_date = db.Column(db.Date)


# =========================
# CREATE TABLES
# =========================

with app.app_context():
    db.create_all()


# =========================
# DASHBOARD
# =========================

@app.route("/")
def dashboard():

    total_students = Student.query.filter_by(leave_date=None).count()
    total_batches = Batch.query.count()
    total_teachers = Teacher.query.count()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_batches=total_batches,
        total_teachers=total_teachers
    )


# =========================
# STUDENTS
# =========================

@app.route("/students")
def students():

    students = Student.query.filter_by(leave_date=None).all()

    return render_template(
        "students.html",
        students=students
    )


@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form["name"]
    student_class = request.form["class"]
    subject = request.form["subject"]
    phone = request.form["phone"]
    monthly_fee = request.form["monthly_fee"]

    student = Student(
        name=name,
        student_class=student_class,
        subject=subject,
        phone=phone,
        monthly_fee=monthly_fee,
        join_date=date.today()
    )

    db.session.add(student)
    db.session.commit()

    return redirect("/students")


# =========================
# TEACHERS
# =========================

@app.route("/teachers")
def teachers():

    teachers = Teacher.query.all()

    return render_template(
        "teachers.html",
        teachers=teachers
    )


@app.route("/add_teacher", methods=["POST"])
def add_teacher():

    name = request.form["name"]
    subject = request.form["subject"]
    phone = request.form["phone"]

    teacher = Teacher(
        name=name,
        subject=subject,
        phone=phone
    )

    db.session.add(teacher)
    db.session.commit()

    return redirect("/teachers")


# =========================
# BATCHES
# =========================

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


# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
