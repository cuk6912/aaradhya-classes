from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    student_class = db.Column(db.String(20))

    subject = db.Column(db.String(100))

    phone = db.Column(db.String(20))

    monthly_fee = db.Column(db.Integer)

    join_date = db.Column(db.String(20))

    leave_date = db.Column(db.String(20))
