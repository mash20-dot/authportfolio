from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, set_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

db = SQLAlchemy()
from dotenv import load_dotenv
load_dotenv()
#Telling python to use pymysql as a replacement for MySQLdb
pymysql.install_as_MySQLdb()
app = Flask(__name__)

#db model for buyer authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True,)
    password = db.Column(db.String(300),)

# JWT Secret Key
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-default-secret')

#setting up MySQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# This disables SQLAlchemy's event system for tracking object modifications (saves memory and avoids warnings)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initializing extensions
db.init_app(app)
jwt = JWTManager(app)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')

    Missing_fields = []
    if not firstname:
        Missing_fields.append('firstname')
    if not lastname:
        Missing_fields.append('lastname')
    if not email:
        Missing_fields.append('email')
    if not password:
        Missing_fields.append('password')
    if Missing_fields:   
           return jsonify({"Error": f"Missing_fields: {Missing_fields}"}), 400
    
    
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already exist'}), 400
    
    
    hashed_password = generate_password_hash(password)

    new_user = User(firstname=firstname, lastname=lastname, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Account created sucessfuly'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    Missing_fields = []
    if not email:
        Missing_fields.append('email')
    if not password:
        Missing_fields.append('password')

    if Missing_fields:
        return jsonify({"Error": f"Missing_fields: {Missing_fields}"}), 400
    
    log_user = User.query.filter_by(email=email).first()
    if not log_user:
        return jsonify({'message': 'Invalid email'}), 400

    if check_password_hash(log_user.password, password):
        pass
    else:
        return jsonify({'message': 'Invalid password'}), 400


    access_token = create_access_token(identity=email)

    response = jsonify({
        'message': 'logged in successfully',
        'access_token': access_token
        })

    set_access_cookies(response, access_token)
    return response





# Create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)