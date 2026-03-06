from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///tuition.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(50))
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    monthly_fee = db.Column(db.Integer)
    join_date = db.Column(db.String(20))
    leave_date = db.Column(db.String(20))
    batch_id = db.Column(db.Integer)


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(50))
    subject = db.Column(db.String(100))
    teacher = db.Column(db.String(100))
    time = db.Column(db.String(20))


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    date = db.Column(db.String(20))
    status = db.Column(db.String(10))


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    month = db.Column(db.String(20))
    date_paid = db.Column(db.String(20))


@app.route("/")
def dashboard():

    total_students = Student.query.count()

    fees = Fee.query.all()
    revenue = sum([f.amount for f in fees])

    pending = 0

    return render_template(
        "dashboard.html",
        total_students=total_students,
        revenue=revenue,
        pending=pending
    )


@app.route("/students")
def students():

    students = Student.query.all()
    batches = Batch.query.all()

    return render_template(
        "students.html",
        students=students,
        batches=batches
    )


@app.route("/add_student", methods=["POST"])
def add_student():

    student = Student(
        name=request.form["name"],
        student_class=request.form["class"],
        subject=request.form["subject"],
        phone=request.form["phone"],
        monthly_fee=request.form["fee"],
        join_date=request.form["join_date"],
        leave_date=request.form["leave_date"],
        batch_id=request.form["batch"]
    )

    db.session.add(student)
    db.session.commit()

    return redirect("/students")


@app.route("/batches")
def batches():

    batches = Batch.query.all()

    return render_template("batches.html", batches=batches)


@app.route("/create_batch", methods=["POST"])
def create_batch():

    batch = Batch(
        name=request.form["name"],
        student_class=request.form["class"],
        subject=request.form["subject"],
        teacher=request.form["teacher"],
        time=request.form["time"]
    )

    db.session.add(batch)
    db.session.commit()

    return redirect("/batches")


@app.route("/attendance")
def attendance():

    batches = Batch.query.all()

    return render_template("attendance.html", batches=batches)


@app.route("/mark_attendance/<int:batch_id>")
def mark_attendance(batch_id):

    students = Student.query.filter_by(batch_id=batch_id).all()

    today = date.today()

    return render_template(
        "mark_attendance.html",
        students=students,
        today=today,
        batch_id=batch_id
    )


@app.route("/save_attendance", methods=["POST"])
def save_attendance():

    today = str(date.today())

    for key in request.form:

        if key.startswith("student_"):

            student_id = key.split("_")[1]
            status = request.form[key]

            attendance = Attendance(
                student_id=student_id,
                date=today,
                status=status
            )

            db.session.add(attendance)

    db.session.commit()

    return redirect("/attendance")


@app.route("/reports")
def reports():

    students = Student.query.all()

    return render_template(
        "reports.html",
        students=students
    )


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=8080)
