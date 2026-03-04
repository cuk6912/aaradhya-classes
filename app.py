from flask import Flask, render_template, request, redirect
from models import db, Student
import os

app = Flask(__name__)

# Get DATABASE_URL from Railway
database_url = os.getenv("DATABASE_URL")

# Railway sometimes gives postgres:// which SQLAlchemy does not accept
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Fallback for local run if DATABASE_URL not present
if not database_url:
    database_url = "sqlite:///local.db"

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def dashboard():

    students = Student.query.all()

    total_students = len(students)
    total_revenue = sum([s.monthly_fee for s in students]) if students else 0

    classes = set([s.student_class for s in students])
    subjects = set([s.subject for s in students])

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_revenue=total_revenue,
        total_classes=len(classes),
        total_subjects=len(subjects)
    )


@app.route("/students")
def students():
    students = Student.query.all()
    return render_template("students.html", students=students)


@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form["name"]
    student_class = request.form["class"]
    subject = request.form["subject"]
    phone = request.form["phone"]
    monthly_fee = int(request.form["fee"])

    new_student = Student(
        name=name,
        student_class=student_class,
        subject=subject,
        phone=phone,
        monthly_fee=monthly_fee
    )

    db.session.add(new_student)
    db.session.commit()

    return redirect("/students")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
@app.route("/teachers")
def teachers():
    return render_template("teachers.html")

@app.route("/batches")
def batches():
    return render_template("batches.html")

@app.route("/attendance")
def attendance():
    return render_template("attendance.html")

@app.route("/fees")
def fees():
    return render_template("fees.html")

@app.route("/reports")
def reports():
    return render_template("reports.html")
