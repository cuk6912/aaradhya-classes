from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tuition_final.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    subject = db.Column(db.String(100))


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    monthly_fee = db.Column(db.Integer)
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


# CREATE DB
with app.app_context():
    db.create_all()


# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    return render_template(
        "dashboard.html",
        students=Student.query.all(),
        teachers=Teacher.query.all(),
        batches=Batch.query.all(),
        fees=Fee.query.all()
    )


# ---------------- TEACHERS ----------------
@app.route("/teachers")
def teachers():
    return render_template("teachers.html", teachers=Teacher.query.all())


@app.route("/add_teacher", methods=["POST"])
def add_teacher():
    db.session.add(Teacher(
        name=request.form.get("name"),
        subject=request.form.get("subject")
    ))
    db.session.commit()
    return redirect("/teachers")


# ---------------- BATCH ----------------
@app.route("/batches")
def batches():
    return render_template("batches.html", batches=Batch.query.all())


@app.route("/create_batch", methods=["POST"])
def create_batch():
    db.session.add(Batch(name=request.form.get("name")))
    db.session.commit()
    return redirect("/batches")


# ---------------- STUDENT ----------------
@app.route("/students")
def students():
    return render_template(
        "students.html",
        students=Student.query.all(),
        batches=Batch.query.all()
    )


@app.route("/add_student", methods=["POST"])
def add_student():
    db.session.add(Student(
        name=request.form.get("name"),
        student_class=request.form.get("class"),
        phone=request.form.get("phone"),
        monthly_fee=request.form.get("monthly_fee"),
        batch_id=request.form.get("batch_id")
    ))
    db.session.commit()
    return redirect("/students")


# ---------------- ATTENDANCE ----------------
@app.route("/attendance")
def attendance():
    return render_template("attendance.html", batches=Batch.query.all())


@app.route("/mark_attendance/<int:batch_id>")
def mark_attendance(batch_id):
    students = Student.query.filter_by(batch_id=batch_id).all()
    return render_template("mark_attendance.html", students=students)


@app.route("/save_attendance", methods=["POST"])
def save_attendance():
    today = str(date.today())

    for key in request.form:
        if key.startswith("student_"):
            sid = key.split("_")[1]
            status = request.form.get(key)

            db.session.add(Attendance(
                student_id=int(sid),
                date=today,
                status=status
            ))

    db.session.commit()
    return redirect("/student_attendance")


@app.route("/student_attendance")
def student_attendance():
    return render_template(
        "student_attendance.html",
        students=Student.query.all(),
        attendance=Attendance.query.all()
    )


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
    db.session.add(Fee(
        student_id=student_id,
        amount=request.form.get("amount"),
        month=request.form.get("month"),
        date_paid=str(date.today())
    ))
    db.session.commit()
    return redirect("/fees")


# RUN
if __name__ == "__main__":
    app.run(debug=True)
