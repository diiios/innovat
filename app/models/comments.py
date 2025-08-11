from ..extentions import db
from datetime import datetime

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)