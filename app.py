from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date
import shutil

app = Flask(__name__)

# ---------------- DATABASE ----------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tuition.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "aaradhya-secret-key"

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    subject = db.Column(db.String(100))


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(50))
    subject = db.Column(db.String(100))
    teacher_id = db.Column(db.Integer)
    time = db.Column(db.String(20))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(50))
    subject = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    monthly_fee = db.Column(db.Integer)
    join_date = db.Column(db.String(20))
    leave_date = db.Column(db.String(20))
    batch_id = db.Column(db.Integer)


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


# ---------------- CREATE TABLE ----------------
with app.app_context():
    db.create_all()


# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        total_students=Student.query.count(),
        total_teachers=Teacher.query.count(),
        total_batches=Batch.query.count(),
        revenue=sum([f.amount for f in Fee.query.all()]),
        students=Student.query.order_by(Student.id.desc()).all()
    )


# ---------------- TEACHERS ----------------

@app.route("/teachers")
def teachers():
    return render_template("teachers.html", teachers=Teacher.query.all())


@app.route("/add_teacher", methods=["POST"])
def add_teacher():
    t = Teacher(
        name=request.form.get("name"),
        subject=request.form.get("subject")
    )
    db.session.add(t)
    db.session.commit()
    return redirect("/teachers")


# ---------------- STUDENTS ----------------

@app.route("/students")
def students():
    students = Student.query.all()
    history = Student.query.filter(Student.leave_date != "").all()

    return render_template(
        "students.html",
        students=students,
        history=history
    )


@app.route("/add_student", methods=["POST"])
def add_student():
    s = Student(
        name=request.form.get("name"),
        student_class=request.form.get("class"),
        subject=request.form.get("subject"),
        phone=request.form.get("phone"),
        monthly_fee=request.form.get("monthly_fee"),
        join_date=request.form.get("join_date"),
        leave_date=request.form.get("leave_date"),
        batch_id=None
    )

    db.session.add(s)
    db.session.commit()
    return redirect("/students")


# ---------------- BATCHES ----------------

@app.route("/batches")
def batches():
    return render_template(
        "batches.html",
        batches=Batch.query.all(),
        teachers=Teacher.query.all()
    )


@app.route("/create_batch", methods=["POST"])
def create_batch():
    b = Batch(
        name=request.form.get("name"),
        student_class=request.form.get("class"),
        subject=request.form.get("subject"),
        teacher_id=request.form.get("teacher"),
        time=request.form.get("time")
    )

    db.session.add(b)
    db.session.commit()
    return redirect("/batches")


# ---------------- ATTENDANCE ----------------

@app.route("/attendance")
def attendance():
    return render_template("attendance.html", batches=Batch.query.all())


@app.route("/mark_attendance/<int:batch_id>")
def mark_attendance(batch_id):
    students = Student.query.filter_by(batch_id=batch_id).all()

    return render_template(
        "mark_attendance.html",
        students=students,
        batch_id=batch_id
    )


@app.route("/save_attendance", methods=["POST"])
def save_attendance():
    today = str(date.today())

    for key in request.form:
        if key.startswith("student_"):
            sid = key.split("_")[1]
            status = request.form[key]

            db.session.add(Attendance(
                student_id=sid,
                date=today,
                status=status
            ))

    db.session.commit()
    return redirect("/attendance")


# ---------------- FEES ----------------

@app.route("/fees")
def fees():
    return render_template(
        "fees.html",
        students=Student.query.all(),
        fees=Fee.query.all()
    )


@app.route("/pay_fee/<int:student_id>", methods=["POST"])
def pay_fee(student_id):
    f = Fee(
        student_id=student_id,
        amount=request.form.get("amount"),
        month=request.form.get("month"),
        date_paid=str(date.today())
    )

    db.session.add(f)
    db.session.commit()
    return redirect("/fees")


# ---------------- REPORTS ----------------

@app.route("/reports")
def reports():
    return render_template(
        "reports.html",
        students=Student.query.all(),
        fees=Fee.query.all()
    )


# ---------------- PARENT LOGIN ----------------

@app.route("/parent_login", methods=["GET", "POST"])
def parent_login():
    if request.method == "POST":
        phone = request.form.get("phone")
        student = Student.query.filter_by(phone=phone).first()

        if student:
            session["parent"] = student.id
            return redirect("/parent_dashboard")

    return render_template("parent_login.html")


@app.route("/parent_dashboard")
def parent_dashboard():
    if "parent" not in session:
        return redirect("/parent_login")

    student = Student.query.get(session["parent"])
    fees = Fee.query.filter_by(student_id=student.id).all()

    return render_template(
        "parent_dashboard.html",
        student=student,
        fees=fees
    )


# ---------------- BACKUP ----------------

@app.route("/backup")
def backup():
    if os.path.exists("tuition.db"):
        shutil.copy("tuition.db", "backup.db")
        return "Backup created successfully"
    return "No database found"


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
