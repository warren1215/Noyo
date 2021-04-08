import sqlalchemy
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow
from sqlalchemy_continuum import make_versioned, version_class, parent_class
import os


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initializing 
db = SQLAlchemy(app)
make_versioned(user_cls=None)
ma = Marshmallow(app)


# Person Model
class Person(db.Model):
	__versioned__ = {}
	__tablename__ = 'person'

	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(100), nullable=False)
	middle_name = db.Column(db.String(100), nullable=True)
	last_name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	age = db.Column(db.Integer, nullable=False)

	def __init__(self, first_name, middle_name, last_name, email, age):
		self.first_name = first_name
		self.middle_name = middle_name
		self.last_name = last_name
		self.email = email
		self.age = age

# Person Schema
class PersonSchema(ma.Schema):
	class Meta:
		fields = ('id', 'first_name', 'middle_name', 'last_name', 'email', 'age')

# Init schema
person_schema = PersonSchema()
persons_schema = PersonSchema(many=True)

sqlalchemy.orm.configure_mappers()


# Create a Person
@app.route('/person', methods=['POST'])
def add_product():
	verification = verify_input()

	if verification is None:
		first_name = request.json['first_name']

		middle_name = ""
		if "middle_name" in request.json:
			middle_name = request.json['middle_name']

		last_name = request.json['last_name']
		email = request.json['email']
		age = request.json['age']

		new_person = Person(first_name, middle_name, last_name, email, age)

		db.session.add(new_person)
		db.session.commit()
		return person_schema.jsonify(new_person)

	return verification

# Get All People
@app.route('/person', methods=['GET'])
def get_all_people():
	db_check = valid_id(None)
	if db_check is not None:
		return db_check
	all_people = Person.query.all()
	result = persons_schema.dump(all_people)
	return jsonify(result)

# Get Single Person
@app.route('/person/<int:id>', methods=['GET'])
def get_person(id):
	check_id = valid_id(id)
	if check_id is not None:
		return check_id

	person = Person.query.get(id)
	return person_schema.jsonify(person)

# Get Single Person, specific version
@app.route('/person/<int:id>/<int:version>', methods=['GET'])
def get_person_version(id, version):
	check_id = valid_id(id)
	if check_id is not None:
		return check_id
	person = Person.query.get(id)
	print(person)
	check_version = valid_version(person, version)
	if check_version is not None:
		return check_version

	return person_schema.jsonify(person.versions[int(version)])

# Update a Person
@app.route('/person/<int:id>', methods=['PUT'])
def update_person(id):
	check_id = valid_id(id)
	if check_id is not None:
		return check_id
	person = Person.query.get(id)

	verification = verify_input()

	if verification is None:
		first_name = request.json['first_name']

		middle_name = ""
		if "middle_name" in request.json:
			middle_name = request.json['middle_name']

		last_name = request.json['last_name']
		email = request.json['email']
		age = request.json['age']

		person.first_name = first_name
		person.middle_name = middle_name
		person.last_name = last_name
		person.email = email
		person.age = age

		db.session.commit()
		return person_schema.jsonify(person)

	return verification

# Delete Person
@app.route('/person/<int:id>', methods=['DELETE'])
def delete_person(id):
	check_id = valid_id(id)
	if check_id is not None:
		return check_id
	person = Person.query.get(id)

	db.session.delete(person)
	db.session.commit()

	return person_schema.jsonify(person)

# Verifys the JSON input is not null for the required parameters.
def verify_input():
	if "first_name" not in request.json:
		return {"result": "failure", "msg": "First name cannot be empty", "error": "400"},400
	if "last_name" not in request.json:
		return {"result": "failure", "msg": "Last name cannot be empty", "error": "400"},400
	if "email" not in request.json:
		return {"result": "failure", "msg": "Email cannot be empty", "error": "400"},400
	if "age" not in request.json:
		return {"result": "failure", "msg": "Age cannot be empty", "error": "400"},400

	return None

# Checks if the person ID exists and that the database is not empty.
def valid_id(id):
	if id is not None:
		person = Person.query.get(id)
		if person is None:
			return {"result": "failure", "msg": "Invalid ID", "error": "400"},400

	all_people = Person.query.all()
	if len(all_people) == 0:
		return {"result": "failure", "msg": "Currently no people in the database. Please try again later", "error": "404"},404
	return None


# Checking if provided version exists for the given person.
def valid_version(person, version):
	try:
		person.versions[int(version)]
	except IndexError:
		return {"result": "failure", "msg": "Invalid Version", "error": "400"},400
	return None

# Catch any unhandled exceptions.
@app.errorhandler(Exception)
def error_page(e):
	return "Something went wrong"


# Run Server
if __name__ == '__main__':
	app.run(debug=True)