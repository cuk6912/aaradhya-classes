from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
