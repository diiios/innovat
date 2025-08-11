from ..extentions import db

class Resources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    photo = db.Column(db.String(250))
    dop = db.Column(db.String(250))
    description = db.Column(db.String(250))
    file = db.Column(db.String(250))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    test = db.Column(db.String(5000))
