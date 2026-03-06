from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tuition.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============================
# DATABASE MODELS
# ============================

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


# ============================
# DASHBOARD
# ============================

@app.route("/")
def dashboard():

    students = Student.query.filter_by(leave_date="").all()
    total_students = len(students)

    fees = Fee.query.all()
    total_revenue = sum([f.amount for f in fees])

    pending = sum([s.monthly_fee for s in students]) - total_revenue
    overdue = 0

    return render_template(
        "dashboard.html",
        total_students=total_students,
        revenue=total_revenue,
        pending=pending,
        overdue=overdue
    )


# ============================
# STUDENTS
# ============================

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


# ============================
# BATCH MANAGEMENT
# ============================

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


@app.route("/batch_students/<int:batch_id>")
def batch_students(batch_id):

    batch = Batch.query.get(batch_id)
    students = Student.query.filter_by(batch_id=batch_id).all()

    return render_template(
        "batch_students.html",
        batch=batch,
        students=students
    )


# ============================
# ATTENDANCE
# ============================

@app.route("/attendance")
def attendance():

    batches = Batch.query.all()

    return render_template(
        "attendance.html",
        batches=batches
    )


@app.route("/mark_attendance/<int:batch_id>")
def mark_attendance(batch_id):

    students = Student.query.filter_by(batch_id=batch_id).all()

    today = date.today().strftime("%Y-%m-%d")

    return render_template(
        "mark_attendance.html",
        students=students,
        today=today,
        batch_id=batch_id
    )


@app.route("/save_attendance", methods=["POST"])
def save_attendance():

    today = date.today().strftime("%Y-%m-%d")

    for key in request.form:

        if key.startswith("student_"):

            student_id = key.split("_")[1]
            status = request.form[key]

            record = Attendance(
                student_id=student_id,
                date=today,
                status=status
            )

            db.session.add(record)

    db.session.commit()

    return redirect("/attendance")


# ============================
# FEE MANAGEMENT
# ============================

@app.route("/fees")
def fees():

    students = Student.query.all()

    return render_template(
        "fees.html",
        students=students
    )


@app.route("/pay_fee", methods=["POST"])
def pay_fee():

    payment = Fee(
        student_id=request.form["student_id"],
        amount=request.form["amount"],
        month=request.form["month"],
        date_paid=datetime.now().strftime("%Y-%m-%d")
    )

    db.session.add(payment)
    db.session.commit()

    return redirect("/fees")


# ============================
# REPORTS
# ============================

@app.route("/reports")
def reports():

    students = Student.query.all()

    return render_template(
        "reports.html",
        students=students
    )


@app.route("/daily_attendance")
def daily_attendance():

    today = date.today().strftime("%Y-%m-%d")

    records = Attendance.query.filter_by(date=today).all()

    return render_template(
        "daily_report.html",
        records=records,
        today=today
    )


@app.route("/student_attendance/<int:student_id>")
def student_attendance(student_id):

    student = Student.query.get(student_id)

    records = Attendance.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_attendance.html",
        student=student,
        records=records
    )


@app.route("/student_fee_report/<int:student_id>")
def student_fee_report(student_id):

    student = Student.query.get(student_id)

    fees = Fee.query.filter_by(student_id=student_id).all()

    return render_template(
        "student_fee_report.html",
        student=student,
        fees=fees
    )


# ============================
# LOGOUT
# ============================

@app.route("/logout")
def logout():
    return redirect("/")


# ============================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
