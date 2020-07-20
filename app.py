from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField
import json
import random

app = Flask(__name__)
app.secret_key = 'lalala'


def read_json(filename):
    with open("data/" + filename + ".json") as file:
        return json.load(file)


def append_json(filename, data_write):
    data = read_json(filename)
    data.update({f"{int(list(data.keys())[-1]) + 1}": data_write})
    with open("data/" + filename + ".json", "w") as file:
        json.dump(data, file, ensure_ascii=False)


for name in ["goals", "teachers", "week", "time"]:
    exec(name + "= read_json(name)")


class Form(FlaskForm):
    name = StringField('Ваc зовут')
    phone = StringField('Ваш телефон')


class BookingForm(Form):
    weekday = HiddenField()
    time = HiddenField()
    teacher = HiddenField()


@app.route('/')
def render_main():
    teachers_sample = [teachers[i] for i in random.sample(range(0, 11), 6)]
    return render_template("index.html", teachers=teachers_sample, goals=goals)


@app.route('/goals/<goal>/')
def render_goals(goal):
    teachers_sample = {i: teachers[i] for i in range(len(teachers))}
    teachers_sample = [value for value in teachers_sample.values() if goal in value["goals"]]
    teachers_sample = sorted(teachers_sample, key=lambda by: by["rating"], reverse=True)
    return render_template("goal.html", teachers=teachers_sample, goal=goal, goals=goals)


@app.route('/profiles/<int:id_teacher>/')
def render_profiles(id_teacher):
    return render_template("profile.html", goals=goals, week=week,
                           id_teacher=id_teacher, teacher=teachers[id_teacher])


@app.route('/request/')
def render_request():
    print(request.path)
    form = Form()
    return render_template("request.html", goals=goals, time=time, form=form)


@app.route('/request_done/', methods=["POST"])
def render_request_done():
    form = Form()
    request_data = {"name": form.name.data, "phone": form.phone.data,
                    "goal": request.form['goal'], "time": request.form['time']}
    append_json("request", request_data)
    return render_template("request_done.html", data=request_data, goals=goals)


@app.route('/booking/<int:id_teacher>/<day>/<int:time>/', methods=['GET', 'POST'])
def render_booking(id_teacher, day, time):
    form = BookingForm()
    return render_template("booking.html", form=form, day=day, week=week,
                           teacher=teachers[id_teacher], time=time, id=id_teacher)


@app.route('/booking_done/', methods=["POST"])
def render_booking_done():
    form = BookingForm()
    booking_data = {"name": form.name.data, "phone": form.phone.data,
                    "day": form.weekday.data, "time": form.time.data,
                    "teacher": form.teacher.data}
    append_json("booking", booking_data)
    return render_template("booking_done.html", data=booking_data, week=week)


if __name__ == '__main__':
    app.run()
