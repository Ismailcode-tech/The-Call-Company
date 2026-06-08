from website import db
from flask_login import UserMixin
#module used for hashing the passwords in the database
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class NetworkProvider(db.Model):
    __tablename__ = 'network_providers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10), nullable=False)
    plans = db.relationship('Plan', backref='provider', lazy=True)

    # returns a readable string representation of the object for debugging
    def __repr__(self):
        return f'<NetworkProvider {self.name}>'




class Member(db.Model, UserMixin):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(30), nullable=False)
    lname = db.Column(db.String(30), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_code = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    refresh_tokens =  db.relationship('RefreshToken', backref=db.backref('users', lazy=True))
    
    memberships = db.relationship('Membership', backref='member', lazy=True)

  
    def __repr__(self):
        return f'<Member {self.fname} {self.lname}>'
    

    #generates the hashed password that will be stored in the database
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    #checks if the hashed password corresponds to the original password( non hashed), which will later be used when the user tries to log in to their account
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Plan(db.Model):
    __tablename__ = 'plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #foreign key references:
    provider_id = db.Column(db.Integer, db.ForeignKey('network_providers.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    data_gb = db.Column(db.Numeric(5, 1), nullable=True)
    unlimited_data = db.Column(db.Boolean, default=False)
    calls = db.Column(db.String(10), nullable=True)
    texts = db.Column(db.String(10), nullable=True)
    phone_included = db.Column(db.String(30), nullable=True)
    monthly_price = db.Column(db.Numeric(6, 2), nullable=False)


    #specifying the relationship (one to many: one plan can have many memberships)
    memberships = db.relationship('Membership', backref='plan', lazy=True)

    def __repr__(self):
        return f'<Plan {self.name} - {self.monthly_price}>'




class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    membership_id = db.Column(db.Integer, nullable = False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    monthly_price = db.Column(db.Numeric(6, 2), nullable=False)
    spending_cap_active = db.Column(db.Boolean, default=False, nullable=False)
    spending_cap_amount = db.Column(db.Numeric(6, 2), default=None, nullable=True)
    age_restricted = db.Column(db.Boolean, default=False, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')


    def __repr__(self):
        return f'<Membership {self.id} - {self.status}>'
    

class RefreshToken(db.Model):
	__tablename__ = "refresh_tokens"

	id = db.Column(db.BigInteger, primary_key=True)
	token = db.Column(db.String(200), unique=True, nullable=False)
	member_id = db.Column(db.Integer, db.ForeignKey(Member.id, onupdate='CASCADE', ondelete='CASCADE'),nullable=False)
	expired_at = db.Column(db.DateTime, nullable=False)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    

    
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    monthly_price = db.Column(db.Numeric(6, 2), nullable=False)
    is_payment_confirmed = db.Column(db.Boolean, default=False, nullable=False)


    def __repr__(self):
        return f'<Payment {self.id} - confirmed: {self.is_payment_confirmed}>'




"""
Important consideration:

In order to allow the creation of the tables in the database, in the __init__.py file, you should add the following:

    from . import models             this was missing

    create_database(app)             this was missing as well

    return app

def create_database(app):           this ensures that the database is created
    with app.app_context():
        db.create_all()
        print('Created Database!')

"""

#user_id
#plan_id
#is_confirmed True or False
#reference(payement_id)
#amount
