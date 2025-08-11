# models/tools_chapter.py
from ..extentions import db

class ToolSection(db.Model):
    __tablename__ = 'tool_section'  # обязательно, если используете ForeignKey

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(250))
    photo = db.Column(db.String(250))
    icon = db.Column(db.String(250))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

    tools = db.relationship('Tool', back_populates='section', lazy='dynamic')  # связь на множество инструментов

