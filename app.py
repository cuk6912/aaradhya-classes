from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = "aaradhya_secret"

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =====================
# MODELS
# =====================

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
    teacher_id = db.Column(db.Integer)
    time = db.Column(db.String(50))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    monthly_fee = db.Column(db.Integer)

    batch_id = db.Column(db.Integer)

    join_date = db.Column(db.Date)
    leave_date = db.Column(db.Date)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer)
    batch_id = db.Column(db.Integer)

    date = db.Column(db.Date)
    status = db.Column(db.String(10))


class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer)
    amount = db.Column(db.Integer)

    month = db.Column(db.String(20))
    payment_date = db.Column(db.Date)


with app.app_context():
    db.create_all()

# =====================
# ADMIN DASHBOARD
# =====================

@app.route("/")
def dashboard():

    total_students = Student.query.count()

    revenue = db.session.query(func.sum(Fee.amount)).scalar() or 0

    return render_template(
        "dashboard.html",
        total_students=total_students,
        revenue=revenue
    )

# =====================
# STUDENTS
# =====================

@app.route("/students")
def students():

    students = Student.query.filter_by(leave_date=None).all()

    return render_template("students.html", students=students)


@app.route("/add_student", methods=["POST"])
def add_student():

    student = Student(
        name=request.form["name"],
        student_class=request.form["class"],
        subject=request.form["subject"],
        phone=request.form["phone"],
        monthly_fee=request.form["monthly_fee"],
        join_date=date.today()
    )

    db.session.add(student)
    db.session.commit()

    return redirect("/students")

# =====================
# PARENT LOGIN
# =====================

@app.route("/parent-login", methods=["GET","POST"])
def parent_login():

    if request.method == "POST":

        phone = request.form["phone"]

        student = Student.query.filter_by(phone=phone).first()

        if student:

            session["parent_student"] = student.id

            return redirect("/parent-dashboard")

    return render_template("parent_login.html")

# =====================
# PARENT DASHBOARD
# =====================

@app.route("/parent-dashboard")
def parent_dashboard():

    student_id = session.get("parent_student")

    student = Student.query.get(student_id)

    attendance = Attendance.query.filter_by(student_id=student_id).all()

    fees = Fee.query.filter_by(student_id=student_id).all()

    batch = Batch.query.get(student.batch_id)

    return render_template(
        "parent_dashboard.html",
        student=student,
        attendance=attendance,
        fees=fees,
        batch=batch
    )

# =====================
# FEES
# =====================

@app.route("/fees")
def fees():

    students = Student.query.all()

    fees = Fee.query.all()

    return render_template(
        "fees.html",
        students=students,
        fees=fees
    )


@app.route("/pay_fee", methods=["POST"])
def pay_fee():

    fee = Fee(
        student_id=request.form["student_id"],
        amount=request.form["amount"],
        month=request.form["month"],
        payment_date=date.today()
    )

    db.session.add(fee)
    db.session.commit()

    return redirect("/fees")

if __name__ == "__main__":
    app.run(debug=True)
