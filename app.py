from flask import Flask, render_template, request, redirect
from models import db, Student
import os
from datetime import date

app = Flask(__name__)

database_url = os.getenv("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

if not database_url:
    database_url = "sqlite:///local.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def dashboard():

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

    new_student = Student(
        name=request.form["name"],
        student_class=request.form["class"],
        subject=request.form["subject"],
        phone=request.form["phone"],
        monthly_fee=request.form["fee"],
        join_date=request.form["join_date"]
    )

    db.session.add(new_student)
    db.session.commit()

    return redirect("/students")


@app.route("/leave_student/<int:id>", methods=["POST"])
def leave_student(id):

    student = Student.query.get(id)

    student.leave_date = date.today()

    db.session.commit()

    return redirect("/students")


@app.route("/teachers")
def teachers():
    return render_template("teachers.html")


@app.route("/batches")
def batches():
    return render_template("batches.html")


@app.route("/attendance")
def attendance():
    return render_template("attendance.html")


@app.route("/fees")
def fees():
    return render_template("fees.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


if __name__ == "__main__":
    app.run()
