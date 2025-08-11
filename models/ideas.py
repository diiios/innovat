from ..extentions import db

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(250))
    tags = db.Column(db.String(250))
    links = db.Column(db.String(250))
    photo = db.Column(db.String(250))
    file = db.Column(db.String(250))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
