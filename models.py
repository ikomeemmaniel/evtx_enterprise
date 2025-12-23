from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    uploads = db.relationship('Upload', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_path = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    converted_csv_path = db.Column(db.String(500))
    converted_xlsx_path = db.Column(db.String(500))
    event_count = db.Column(db.Integer, default=0)
    
    events = db.relationship('EventRecord', backref='upload', lazy=True, cascade='all, delete-orphan')

class EventRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'), nullable=False)
    event_id = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime)
    user_sid = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    security_id = db.Column(db.String(255))
    action = db.Column(db.String(255))
    keywords = db.Column(db.String(500))
    failure_reason = db.Column(db.Text)
    process_name = db.Column(db.String(500))
