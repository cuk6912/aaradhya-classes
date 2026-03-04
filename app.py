import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL connection from Railway
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    student_class = db.Column(db.String(20))

    subject = db.Column(db.String(50))

    phone = db.Column(db.String(20))

    monthly_fee = db.Column(db.Integer)


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

    subject = request.form["subject"]

    phone = request.form["phone"]

    fee = request.form["fee"]

    new_student = Student(

        name=name,

        student_class=student_class,

        subject=subject,

        phone=phone,

        monthly_fee=fee
    )

    db.session.add(new_student)

    db.session.commit()

    return redirect("/students")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
