import os
import base64
import json
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, send
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    text = db.Column(db.Text, nullable=True)
    file = db.Column(db.Text, nullable=True)  # Для изображений, аудио, видео

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered!"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([{"user": msg.user, "text": msg.text, "file": msg.file} for msg in messages])

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    new_msg = Message(user=data["user"], text=data.get("text"), file=data.get("file"))
    db.session.add(new_msg)
    db.session.commit()
    send(data, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаём таблицы при запуске
    socketio.run(app, debug=True, host='0.0.0.0')
