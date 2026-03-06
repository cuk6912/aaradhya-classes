from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tuition.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------------
# DATABASE MODELS
# -------------------------

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    monthly_fee = db.Column(db.Integer)
    join_date = db.Column(db.String(20))
    leave_date = db.Column(db.String(20))
    batch_id = db.Column(db.Integer)

class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    subject = db.Column(db.String(100))
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

# -------------------------
# DASHBOARD
# -------------------------

@app.route("/")
def dashboard():

    students = Student.query.filter_by(leave_date="").all()
    total_students = len(students)

    fees = Fee.query.all()
    revenue = sum([f.amount for f in fees])

    pending = 0

    return render_template(
        "dashboard.html",
        total_students=total_students,
        revenue=revenue,
        pending=pending
    )

# -------------------------
# STUDENTS
# -------------------------

@app.route("/students")
def students():

    students = Student.query.filter_by(leave_date="").all()
    batches = Batch.query.all()

    return render_template(
        "students.html",
        students=students,
        batches=batches
    )

@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form["name"]
    student_class = request.form["class"]
    subject = request.form["subject"]
    phone = request.form["phone"]
    monthly_fee = request.form["fee"]
    join_date = request.form["join_date"]
    leave_date = ""
    batch_id = request.form["batch"]

    student = Student(
        name=name,
        student_class=student_class,
        subject=subject,
        phone=phone,
        monthly_fee=monthly_fee,
        join_date=join_date,
        leave_date=leave_date,
        batch_id=batch_id
    )

    db.session.add(student)
    db.session.commit()

    return redirect("/students")

# -------------------------
# BATCHES
# -------------------------

@app.route("/batches")
def batches():

    batches = Batch.query.all()

    return render_template("batches.html", batches=batches)

@app.route("/create_batch", methods=["POST"])
def create_batch():

    name = request.form["name"]
    student_class = request.form["class"]
    subject = request.form["subject"]
    time = request.form["time"]

    batch = Batch(
        name=name,
        student_class=student_class,
        subject=subject,
        time=time
    )

    db.session.add(batch)
    db.session.commit()

    return redirect("/batches")

@app.route("/batch_students/<batch_id>")
def batch_students(batch_id):

    students = Student.query.filter_by(batch_id=batch_id).all()
    batch = Batch.query.get(batch_id)

    return render_template(
        "batch_students.html",
        students=students,
        batch=batch
    )

# -------------------------
# ATTENDANCE
# -------------------------

@app.route("/attendance")
def attendance():

    batches = Batch.query.all()

    return render_template("attendance.html", batches=batches)

@app.route("/mark_attendance/<batch_id>")
def mark_attendance(batch_id):

    students = Student.query.filter_by(batch_id=batch_id).all()

    today = date.today()

    return render_template(
        "mark_attendance.html",
        students=students,
        today=today
    )

@app.route("/save_attendance", methods=["POST"])
def save_attendance():

    for key in request.form:

        if "student_" in key:

            student_id = key.split("_")[1]
            status = request.form[key]
            today = date.today()

            attendance = Attendance(
                student_id=student_id,
                date=str(today),
                status=status
            )

            db.session.add(attendance)

    db.session.commit()

    return redirect("/attendance")

# -------------------------
# REPORTS
# -------------------------

@app.route("/reports")
def reports():

    students = Student.query.all()

    return render_template(
        "reports.html",
        students=students
    )

@app.route("/daily_attendance")
def daily_attendance():

    today = str(date.today())

    records = Attendance.query.filter_by(date=today).all()

    return render_template(
        "daily_report.html",
        records=records
    )

@app.route("/student_attendance/<student_id>")
def student_attendance(student_id):

    records = Attendance.query.filter_by(student_id=student_id).all()
    student = Student.query.get(student_id)

    return render_template(
        "student_attendance.html",
        records=records,
        student=student
    )

@app.route("/student_fee_report/<student_id>")
def student_fee_report(student_id):

    fees = Fee.query.filter_by(student_id=student_id).all()
    student = Student.query.get(student_id)

    return render_template(
        "student_fee_report.html",
        fees=fees,
        student=student
    )

# -------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
