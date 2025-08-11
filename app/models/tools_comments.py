from ..extentions import db
from datetime import datetime

class CommentTools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # Для связи комментария с объектом
    object_type = db.Column(db.String(50), nullable=False)  # например, 'tool', 'tool_section', 'idea' и т.п.
    object_id = db.Column(db.Integer, nullable=False)       # id соответствующего объекта