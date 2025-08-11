# models/tools.py
from ..extentions import db

class Tool(db.Model):
    __tablename__ = 'tool'  # обязательно

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.String(50))
    photo = db.Column(db.String(250))
    file = db.Column(db.String(250))

    section_id = db.Column(db.Integer, db.ForeignKey('tool_section.id'))
    section = db.relationship('ToolSection', back_populates='tools')