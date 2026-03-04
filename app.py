from flask import Flask, render_template, request, redirect
from models import db, Student
import os

app = Flask(__name__)

# Railway PostgreSQL connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# Create tables automatically
with app.app_context():
    db.create_all()


# Dashboard
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


# Student Page
@app.route("/students")
def students():

    students = Student.query.all()

    return render_template("students.html", students=students)


# Add Student
@app.route("/add_student", methods=["POST"])
def add_student():

    name = request.form["name"]
    student_class = request.form["class"]
    subject = request.form["subject"]
    phone = request.form["phone"]
    monthly_fee = request.form["fee"]

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


# Run locally
if __name__ == "__main__":
    app.run(debug=True)
