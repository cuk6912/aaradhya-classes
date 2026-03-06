from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tuition.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------- MODELS ----------------

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    monthly_fee = db.Column(db.Integer)
    batch_id = db.Column(db.Integer)


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    student_class = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    time = db.Column(db.String(20))


# ---------------- DASHBOARD ----------------

@app.route("/")
def dashboard():

    total_students = Student.query.count()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        revenue=0,
        pending=0,
        overdue=0
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


# ---------------- REPORTS ----------------

@app.route("/reports")
def reports():

    students = Student.query.all()

    return render_template("reports.html", students=students)


# ---------------- START ----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run()
