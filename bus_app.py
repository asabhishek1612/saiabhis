from flask import Flask
from flask import json
from flask_cors import CORS
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime 
import numpy as np
from sqlalchemy import and_, or_, not_

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@127.0.0.1/busapp'
db = SQLAlchemy(app)

@app.route('/login',methods=['POST','GET'])
def login():
	if request.method=='POST':
		data=request.get_json()
		username=data['username']
		password=data['password']
		refofuser=0
		userinfo=Passenger.query.all()
		for i in userinfo:
			if (i.email==username):
				refofuser=i
			if refofuser==0:
				return "failed"
			else:
				if(refofuser.password==password) and (refofuser.email==username):
					return "sucess"
				else:
					return "failed"

@app.route('/register',methods=['POST','GET'])
def reg():
    if request.method=='POST':
        data=request.get_json()
        
        passenger_name=data['name']
        address=data['address']
        email=data['emailId']
        mobile_no=data['phoneNo']
        password=data['password']
        age=data['age']
        gender=data['gender']
        
        userreg=Passenger(passenger_name=passenger_name,address=address,email=email,mobile_no=mobile_no,password=password,age=age,gender=gender)
        db.session.add(userreg)
        db.session.commit()
    return "added"

@app.route('/searchbus',methods=['POST','GET'])
def viewbuses():
    if request.method=='POST':
        data=request.get_json()
        print('in')
        start_point=data['from']
        to=data['to']
        departure=data['departure']
        seats=data['selected_seats']
        busdict=[]

        #if ref==Allorders,unfullfilled,fullfilled
        departbuses=busdetails.query.filter_by(departure_date=departure)
        for i in departbuses:
            if(str(i.available_seats)>=str(seats)):
                busid=i.bus_id
                businfo=bus.query.filter_by(bus_id=busid).first()
                details={}
                details['bus_id']=busid
                details['start_point']=businfo.from_location
                details['boarding']=start_point
                details['departure']=to
                details['end_point']=businfo.to_location
                details['arrival_time']=businfo.arrival_time
                details['route_id']=businfo.route_id
                details['departure_time']=businfo.departure_time
                details['available_seats']=i.available_seats
                details['amount']=i.price
                details['selected_seats']=seats
                busdict.append(details)
        return json.dumps(busdict)

@app.route('/bookbus',methods=['POST','GET'])
def booking():
    if request.method=='POST':
        data=request.get_json()
        passenger_id=data['passenger_id']
        busno=data['bus_id']
        busprice=busdetails.query.filter_by(bus_id=busno).first()
        seats=data['selected_seats']
        price=int(busprice.price*int(seats))
        departure_date=data['departure_date']
        buses=busdetails.query.filter_by(departure_date=departure_date)
        for i in buses:
            b=i.bus_id
            if(str(b)==str(busno)):
                #businfo=busdetails.query.filter_by(and_(bus_id=busno,departure_date=departure_date)).first()
                seat=i.available_seats
                update_seats=seat-int(seats)
                i.available_seats=update_seats
                db.session.commit()
                tkt=ticket(passenger_id=passenger_id,bus_id=busno,departure_date=departure_date,amount=price,seats=seats,status="confirmed")
                db.session.add(tkt)
                db.session.commit()
        return "sucess"
    

@app.route('/bookinghistory',methods=['POST','GET'])
def bookhistory():
    if request.method=='POST':
        data=request.get_json()
        passenger_id=data['passenger_id']
        history_dict=[]
        history=ticket.query.filter_by(passenger_id=passenger_id)
        for i in history:
        	details={}
        	details['ticket_no']=i.ticket_id
        	details['bus_id']=i.bus_id
        	businfo=bus.query.filter_by(bus_id=i.bus_id).first()
        	details['start_point']=businfo.from_location
        	details['end_point']=businfo.to_location
        	details['price']=i.amount
        	details['seats']=i.seats
        	details['status']=i.status
        	history_dict.append(details)
        return json.dumps(history_dict)
           
@app.route('/cancelbus',methods=['POST','GET'])
def cance():
    if request.method=='POST':
        data=request.get_json()
        ticket_id=data['ticket_id']
        ticketdetails=ticket.query.filter_by(ticket_id=ticket_id).first()
        bus_id=ticketdetails.bus_id
        departbuses=busdetails.query.filter_by(departure_date=ticketdetails.departure_date)
        for i in departbuses:
        	if(i.bus_id==bus_id and str(ticketdetails.status)==str("confirmed")):
        		seats=i.available_seats
        		update_seats=seats+ticketdetails.seats
        		i.available_seats=update_seats
        		ticketdetails.status="cancelled"
        		db.session.commit()

        return "sucess"

class Passenger(db.Model):
    __tablename__='passenger_table'
    passenger_id=db.Column(db.Integer, primary_key=True)
    passenger_name=db.Column(db.String(78))
    age=db.Column(db.Integer)
    email= db.Column(db.String(80), unique = True)
    mobile_no=db.Column(db.Integer)
    password=db.Column(db.String(78))
    gender=db.Column(db.String(78))
    address=db.column(db.String(78))
    
    passtktref=db.relationship('ticket',backref='passtab')
    def __init__(self,passenger_name,age,email,mobile_no,password,gender,address):
        self.passenger_name=passenger_name
        self.age=age
        self.email=email
        self.mobile_no=mobile_no
        self.password=password
        self.gender=gender
        self.address=address
    def to_dict(self):
    	data={}
    	data['passenger_name']=self.passenger_name
    	data['age']=self.age
    	data['email']=self.email
    	data['mobile_no']=self.mobile_no
    	data['password']=self.password
    	data['gender']=self.gender
    	data['address']=self.address
    	return data

class bus(db.Model):
    __tablename__='bus_table'
    bus_id=db.Column(db.Integer, primary_key=True)
    from_location=db.Column(db.String(78))
    to_location=db.Column(db.String(78))
    route_id=db.Column(db.String(78))
    seats=db.Column(db.Integer)
    departure_time=db.Column(db.String(78))
    arrival_time=db.Column(db.String(78))
    #bustableref=db.relationship('bus_details',backref='bustab')
    #bustabletkt=db.relationship('ticket',backref='bustabtkt')
    def __init__(self,from_location,to_location,route_id,seats,departure_time,arrival_time):
        self.from_location=from_location
        self.to_location=to_location
        self.route_id=route_id
        self.departure_time=departure_time
        self.arrival_time=arrival_time
    def to_dict(self):
        data={}
        data['bus_id']=self.bus_id
        data['from_location']=self.from_location
        data['to_location']=self.to_location
        data['route_id']=self.route_id
        data['departure_time']=self.departure_time
        data['arrival_time']=self.arrival_time
        return data

class busdetails(db.Model):
	__tablename__='bus_details'
	s_no=db.Column(db.Integer,primary_key=True)
	bus_id=db.Column(db.Integer,db.ForeignKey('bus_table.bus_id'))
	departure_date=db.Column(db.String(78))
	price=db.Column(db.Integer)
	available_seats=db.Column(db.Integer)
	#busdetailstkt=db.relationship('ticket',backref='busdetailtkt')
	def __init__(self,bus_id,departure_date,price,available_seats):
		self.bus_id=bus_id
		self.departure_date=departure_date
		self.price=price
		self.available_seats=available_seats

	def to_dict(self):
		data={}
		bus_id=bus.query.filter_by(bus_id=self.bus_id).first()
		data['bus_id']=bus_id.bus_id
		data['departure_date']=self.departure_date
		data['price']=self.price
		data['available_seats']=self.available_seats
		return data
	
class ticket(db.Model):
    __tablename__='ticket_details'
    ticket_id=db.Column(db.Integer, primary_key=True)
    passenger_id=db.Column(db.Integer,db.ForeignKey('passenger_table.passenger_id'))
    bus_id=db.Column(db.Integer,db.ForeignKey('bus_table.bus_id'))
    departure_date=db.Column(db.String(78))
    amount=db.Column(db.Integer)
    seats=db.Column(db.Integer)
    status=db.Column(db.String(78))
    def __init__(self,passenger_id,bus_id,departure_date,amount,seats,status):

    	self.passenger_id=passenger_id
    	self.bus_id=bus_id
    	self.departure_date=departure_date
    	self.amount=amount
    	self.seats=seats
    	self.status=status
    def to_dict(self):
    	data={}
    	data['ticket_id']=self.ticket_id
    	data['bus_id']=self.bus_id
    	data['passenger_id']=self.passenger_id
    	data['departure_date']=self.departure_date
    	data['seats']=self.seats
    	data['amount']=self.amount
    	return data

if __name__ == '__main__':
    app.run(debug=True)