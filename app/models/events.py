from ..extentions import db
from datetime import datetime

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(250))
    start_date = db.Column(db.DateTime)  # 👉 начало
    end_date = db.Column(db.DateTime, nullable=True)  # 👉 окончание (может быть пустым)
    place = db.Column(db.String(250))
    text = db.Column(db.Text)
    slogan = db.Column(db.String(250))
    photo = db.Column(db.String(250))

     
    