from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import date

app = Flask(__name__)

# ---------------- DATABASE CONFIG ----------------

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
else:
    DATABASE_URL = "sqlite:///tuition.db"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
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


# ---------------- CREATE TABLES ----------------

with app.app_context():
    db.create_all()


# ---------------- ROUTES ----------------

@app.route("/")
def dashboard():
    total_students = Student.query.count()
    fees = Fee.query.all()
    revenue = sum([f.amount for f in fees])

    return render_template("dashboard.html",
                           total_students=total_students,
                           revenue=revenue)


@app.route("/students")
def students():
    students = Student.query.all()
    batches = Batch.query.all()
    return render_template("students.html", students=students, batches=batches)


@app.route("/add_student", methods=["POST"])
def add_student():
    student = Student(
        name=request.form["name"],
        student_class=request.form["class"],
        phone=request.form["phone"],
        monthly_fee=request.form["fee"],
        join_date=request.form["join_date"],
        leave_date=request.form["leave_date"],
        batch_id=request.form["batch"]
    )
    db.session.add(student)
    db.session.commit()
    return redirect("/students")


@app.route("/fees")
def fees():
    students = Student.query.all()
    return render_template("fees.html", students=students)


@app.route("/pay_fee/<int:student_id>", methods=["POST"])
def pay_fee(student_id):
    fee = Fee(
        student_id=student_id,
        amount=request.form["amount"],
        month=request.form["month"],
        date_paid=str(date.today())
    )
    db.session.add(fee)
    db.session.commit()
    return redirect("/fees")


# ---------------- BACKUP ROUTE (IMPORTANT) ----------------

@app.route("/backup")
def backup():
    import datetime
    filename = f"backup_{datetime.datetime.now().strftime('%Y%m%d')}.txt"

    data = ""
    students = Student.query.all()

    for s in students:
        data += f"{s.name},{s.phone},{s.monthly_fee}\\n"

    with open(filename, "w") as f:
        f.write(data)

    return f"Backup created: {filename}"


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
