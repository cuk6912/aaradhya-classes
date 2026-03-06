from flask import Flask, render_template, request, redirect
from models import db, Student, Batch, Attendance, Fee
from datetime import date

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tuition.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# ---------------- DASHBOARD ----------------

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


# ---------------- STUDENTS ----------------

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


# ---------------- BATCHES ----------------

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


# ---------------- ATTENDANCE ----------------

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
        today=today
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


# ---------------- REPORTS ----------------

@app.route("/reports")
def reports():

    students = Student.query.all()

    return render_template(
        "reports.html",
        students=students
    )


# ---------------- START ----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
