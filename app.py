from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

app = Flask(__name__)

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
# DASHBOARD
# =====================

@app.route("/")
def dashboard():

    total_students = Student.query.filter_by(leave_date=None).count()

    revenue = db.session.query(db.func.sum(Fee.amount)).scalar() or 0

    pending = db.session.query(
        db.func.sum(Student.monthly_fee)
    ).scalar() or 0

    return render_template(
        "dashboard.html",
        total_students=total_students,
        revenue=revenue,
        pending=pending
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
# TEACHERS
# =====================

@app.route("/teachers")
def teachers():

    teachers = Teacher.query.all()

    return render_template("teachers.html", teachers=teachers)


@app.route("/add_teacher", methods=["POST"])
def add_teacher():

    teacher = Teacher(
        name=request.form["name"],
        subject=request.form["subject"],
        phone=request.form["phone"]
    )

    db.session.add(teacher)
    db.session.commit()

    return redirect("/teachers")

# =====================
# BATCHES
# =====================

@app.route("/batches")
def batches():

    batches = Batch.query.all()
    teachers = Teacher.query.all()

    return render_template("batches.html", batches=batches, teachers=teachers)


@app.route("/add_batch", methods=["POST"])
def add_batch():

    batch = Batch(
        batch_name=request.form["batch_name"],
        class_name=request.form["class_name"],
        subject=request.form["subject"],
        teacher_id=request.form["teacher_id"],
        time=request.form["time"]
    )

    db.session.add(batch)
    db.session.commit()

    return redirect("/batches")

# =====================
# ATTENDANCE
# =====================

@app.route("/attendance")
def attendance():

    batches = Batch.query.all()

    return render_template("attendance.html", batches=batches)


@app.route("/mark_attendance/<batch_id>")
def mark_attendance(batch_id):

    students = Student.query.filter_by(batch_id=batch_id).all()

    return render_template(
        "mark_attendance.html",
        students=students,
        batch_id=batch_id
    )


@app.route("/save_attendance/<batch_id>", methods=["POST"])
def save_attendance(batch_id):

    students = Student.query.filter_by(batch_id=batch_id).all()

    for student in students:

        status = request.form.get(str(student.id))

        record = Attendance(
            student_id=student.id,
            batch_id=batch_id,
            date=date.today(),
            status=status
        )

        db.session.add(record)

    db.session.commit()

    return redirect("/attendance")

# =====================
# FEES
# =====================

@app.route("/fees")
def fees():

    students = Student.query.filter_by(leave_date=None).all()

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
