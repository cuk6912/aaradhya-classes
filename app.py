from flask import Flask, render_template, request, redirect
from models import db, Student

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/students")
def students():
    students = Student.query.all()
    return render_template("students.html", students=students)

@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form["name"]
    student_class = request.form["class"]
    phone = request.form["phone"]

    student = Student(
        name=name,
        student_class=student_class,
        phone=phone
    )

    db.session.add(student)
    db.session.commit()

    return redirect("/students")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
