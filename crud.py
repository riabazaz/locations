from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
from flask_cors import CORS, cross_origin
import os


app = Flask(__name__, template_folder="/Users/Ria/Desktop/Shift/khalid/templates")
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'crud.sqlite')
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
db = SQLAlchemy(app)
ma = Marshmallow(app)

CORS(app)



users_locations = db.Table('users_locations',
                            db.Column('user_id', db.Integer, db.ForeignKey('user.username')),
                            db.Column('location_id', db.String, db.ForeignKey('location.id')))

class User(db.Model):
    username = db.Column(db.String(80),primary_key=True, unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), nullable=False)
    studylocations = db.relationship('Location', secondary='users_locations', backref=db.backref('user', lazy='dynamic'))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.studylocations = []



# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    
    new_user = User(username, email, password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user)

# endpoint to show all users
@app.route("/user", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)


# endpoint to get user detail by id
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    all_locations = user.studylocations
    result = locations_schema.dump(all_locations)
    user_list = []
    userDict = {
        "email": user.email,
        "password": user.password,
        "username": user.username,
        "studylocations" : result.data
    }
    user_list.append(userDict)
    # user_list.append(result.data)
    return jsonify(user_list)
   


# endpoint to update user
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    user.email = email
    user.username = username
    user.password = password

    db.session.commit()
    return user_schema.jsonify(user)

# endpoint to delete user


@app.route("/user/<id>", methods=["DELETE"])
def user_delete(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()

    return user_schema.jsonify(user)


class Location(db.Model):
    id = db.Column(db.String(300), primary_key=True)
    formatted_address = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(50), unique=False)
    lat = db.Column(db.String(50), unique=False)
    lng = db.Column(db.String(50), unique=False)


    def __init__(self, place_id, formatted_address, name, lat, lng):
        self.id = place_id
        self.formatted_address = formatted_address
        self.name = name
        self.lat = lat
        self.lng = lng



@app.route("/user/<id>/location", methods=["POST"])
@cross_origin()
def add_user_location(id):
    #if location not already in locations table
    print(request)
    user = User.query.get(id)
    location_id = request.json['id']
    formatted_address = request.json['formatted_address']
    name = request.json['name']
    lat = request.json['latitude']
    lng = request.json['longitude']

    inUserLocs = False

    if Location.query.get(location_id) == None:
        #if not in location table, this means not in user.studylocations as well
        new_location = Location(location_id, formatted_address, name, lat, lng)
        user.studylocations.append(new_location) 

    else:
        print(Location.query.get(location_id))
        new_location = Location.query.get(location_id)
        #if in Location tables, must check that it isn't in user.studylocations
        for item in user.studylocations:
            if item.id == location_id:
                inUserLocs = True;
        if inUserLocs == False:
            #adds it to user.studylocations if not already there
            user.studylocations.append(new_location)
    

    db.session.commit()

    return location_schema.jsonify(new_location)


@app.route("/user/<id>/location", methods=["GET"])
def get_user_locations(id):
    user = User.query.get(id)
    all_locations = user.studylocations
    result = locations_schema.dump(all_locations)
    return jsonify(result.data)


# endpoint to update user
# @app.route("/location/<id>", methods=["PUT"])
# def location_update(id):
#     location = Location.query.get(id)
#     formatted_address = request.json['formatted_address']
#     street_number = request.json['street_number']
#     route = request.json['route']
#     neighborhood = request.json['neighborhood']
#     locality = request.json['locality']
#     admin_area = request.json['admin_area']
#     country = request.json['country']
#     postal_code = request.json['postal_code']
#     formatted_address = formatted_address

#     street_number = street_number
#     route = route
#     neighborhood = neighborhood
#     locality = locality
#     admin_area = admin_area
#     country = country
#     postal_code = postal_code

#     db.session.commit()
#     return location_schema.jsonify(location)

# endpoint to delete user location
@app.route("/user/<userid>/location/<locationid>", methods=["DELETE"])
def user_location_delete(userid, locationid):
    user = User.query.get(userid)
    location = Location.query.get(locationid)
    if Location.query.get(locationid) != None:
        user.studylocations.remove(location)
        db.session.commit()

    return location_schema.jsonify(location)


class LocationSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id','formatted_address', 'name', 'lat', 'lng')

location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)

class UserSchema(ma.Schema):
    # locations = fields.Nested(LocationSchema, many=True)
    class Meta:
        # Fields to expose
        fields = ('username', 'email', 'password', 'studylocations')

user_schema = UserSchema()
users_schema = UserSchema(many=True)



if __name__ == '__main__':
	app.run(debug=True)








