import ast
import json
import random

from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, HiddenField
from wtforms.validators import InputRequired, Regexp

csrf = CSRFProtect()
app = Flask(__name__)
app.secret_key = 'lalala'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
csrf.init_app(app)


def read_json(filename):
    with open(__file__[:-6] + "json/" + filename + ".json", 'rb') as file:
        return json.load(file)


for name in ["teachers", "goals", "week", "time"]:
    exec(name + "= read_json(name)")


class Teacher(db.Model):
    __tablename__ = "teachers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    about = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    picture = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    goals = db.Column(db.String, nullable=False)
    free = db.Column(db.String, nullable=False)
    booking = db.relationship("Booking")


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    day = db.Column(db.String, nullable=False)
    teacher_name = db.Column(db.Integer, db.ForeignKey("teachers.name"))
    teacher = db.relationship("Teacher")


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    goal = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)


class Form(FlaskForm):
    name = StringField('Ваc зовут', validators=[InputRequired()])
    phone = StringField('Ваш телефон', validators=[InputRequired(),
                                                   Regexp("^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$",
                                                          message="Неверно указан номер")])


class BookingForm(Form):
    weekday = HiddenField()
    time = HiddenField()
    teacher = HiddenField()


db.create_all()
if not db.session.query(Teacher).all():
    for teacher in teachers:
        query = Teacher(name=teacher['name'], about=teacher["about"], rating=teacher["rating"],
                        picture=teacher["picture"], price=teacher["price"],
                        goals=str(teacher["goals"]), free=str(teacher["free"]))
        db.session.add(query)
    db.session.commit()


@app.route('/')
def render_main():
    teachers_sample = [db.session.query(Teacher).filter(Teacher.id == i).first() for i in
                       random.sample(range(1, 11), 6)]
    return render_template("index.html", teachers=teachers_sample, goals=goals)


@app.route('/goals/<goal>/')
def render_goals(goal):
    teachers_sample = db.session.query(Teacher).filter(Teacher.goals.like(f"%{goal}%")).order_by(Teacher.rating.desc())
    return render_template("goal.html", teachers=teachers_sample.all(), goal=goal, goals=goals)


@app.route('/profiles/<int:id_teacher>/')
def render_profiles(id_teacher):
    teacher = db.session.query(Teacher).filter(Teacher.id == id_teacher).first_or_404()
    teacher_goals = ast.literal_eval(teacher.goals)
    teacher_free = dict(ast.literal_eval(teacher.free))
    return render_template("profile.html", id_teacher=id_teacher, goals=goals,
                           teacher=teacher, teacher_goals=teacher_goals,
                           teacher_free=teacher_free, week=week)


@app.route('/request/', methods=["GET", "POST"])
def render_request():
    form = Form()
    if request.method == "POST" and form.validate_on_submit():
        request_data = {"name": form.name.data, "phone": form.phone.data,
                        "goal": request.form['goal'], "time": request.form['time']}
        req = Request(name=form.name.data, phone=form.phone.data,
                      goal=request.form['goal'], time=request.form['time'])
        db.session.add(req)
        db.session.commit()
        return render_template("request_done.html", data=request_data, goals=goals)
    return render_template("request.html", goals=goals, time=time, form=form)


@app.route('/booking/<int:id_teacher>/<day>/<int:time>/', methods=['GET', 'POST'])
def render_booking(id_teacher, day, time):
    form = BookingForm()
    if request.method == "POST" and form.validate_on_submit():
        booking_data = {"name": form.name.data, "phone": form.phone.data,
                        "day": form.weekday.data, "time": form.time.data,
                        "teacher": form.teacher.data}
        booking = Booking(name=form.name.data, phone=form.phone.data,
                          day=form.weekday.data, time=form.time.data,
                          teacher_name=form.teacher.data)
        db.session.add(booking)
        db.session.commit()
        return render_template("booking_done.html", data=booking_data, week=week, day=day, time=time,
                               picture=db.session.query(Teacher).filter(Teacher.id == id_teacher).first().picture)
    return render_template("booking.html", form=form, day=day, week=week, time=time, id=id_teacher,
                           teacher=db.session.query(Teacher).filter(Teacher.id == id_teacher).first())


@app.route('/booking_done/', methods=["POST"])
def render_booking_done():
    form = BookingForm()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
