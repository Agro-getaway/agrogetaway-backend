from sqlalchemy import Column, Boolean, Float, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from Connections.connections import Base,engine
import datetime
from hashing import Harsher
from pydantic import BaseModel

class Farmers(Base):
    __tablename__ = 'farmers'

    id = Column(Integer, primary_key=True, index=True) 
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, nullable= True, unique=True)
    role = Column(String)
    phonenumber = Column(String)
    password = Column(String)
    farms = relationship("Farms", back_populates="farmer")

    @staticmethod
    def create_user(firstname,lastname,email,role,phonenumber,password):
        print("""Creating user""")
        hashed_password = Harsher.get_hash_password(password)
        user = Farmers(firstname=firstname,lastname=lastname,email=email,role=role,phonenumber=phonenumber,password=hashed_password)
        return user
    
    @staticmethod
    def get_user(db_session, email_or_phone):
        return db_session.query(Farmers).filter((Farmers.email == email_or_phone) | (Farmers.phonenumber == email_or_phone)).first()

    def verify_password(self, password):
        return Harsher.verify_password(password, self.password)
    
    def update_password(self, new_password):
        hashed_password = Harsher.get_hash_password(new_password)
        print(f"Updating password to: {hashed_password}") 
        self.password = hashed_password

    def get_user_by_id(db_session, id):
        return db_session.query(Farmers).filter(Farmers.id == id).first()

    @staticmethod
    def get_user_by_email_or_phone(db_session, email, phone):
        query = db_session.query(Farmers)
        if email:
            query = query.filter(Farmers.email == email)
        if phone:
            query = query.filter(Farmers.phonenumber == phone)
        return query.first()

class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True, index=True) 
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, nullable= True, unique=True)
    employee_access = Column(String, unique=True)
    password = Column(String)

    @staticmethod
    def create_admin(firstname,lastname,email,employee_access,password):
        print("""Creating admin""")
        hashed_password = Harsher.get_hash_password(password)
        admin = Admin(firstname=firstname,lastname=lastname,email=email,employee_access=employee_access,password=hashed_password)
        return admin
    
    @staticmethod
    def get_admin(db_session, email_or_access):
        return db_session.query(Admin).filter((Admin.email == email_or_access) | (Admin.employee_access == email_or_access)).first()
    
    @staticmethod
    def username_exists(db_session, employee_access):
        return db_session.query(Admin).filter(Admin.employee_access == employee_access).first() is not None
    
    def verify_password(self, password):
        return Harsher.verify_password(password, self.password)
    
    def update_password(self, new_password):
        hashed_password = Harsher.get_hash_password(new_password)
        print(f"Updating password to: {hashed_password}") 
        self.password = hashed_password

    def get_all_admins_email(db_session):
        return db_session.query(Admin.email).all()

    @staticmethod
    def get_admin_by_email_or_phone(db_session, email, phone):
        query = db_session.query(Admin)
        if email:
            query = query.filter(Admin.email == email)
        if phone:
            query = query.filter(Admin.employee_access == phone)
        return query.first()
    
class UsernameChangeRequest(BaseModel):
    current_username: str
    new_username_prefix: str

class Farms(Base):
    __tablename__ = 'farms'
    id = Column(Integer, primary_key=True, index=True)
    Location = Column(String)
    Details = Column(String)
    Description = Column(String)
    Image_url = Column(String)
    farmer_id = Column(Integer, ForeignKey('farmers.id'))
    status  = Column(String)
    farmer = relationship("Farmers", back_populates="farms")
    bookings = relationship("Booking", back_populates="farms")

    @staticmethod
    def create_farm_data(Location,Details,Description,Image_url,farmer_id,status):
        print("""Creating farmer""")
        farmer = Farms(Location=Location,Details=Details,Description=Description,Image_url=Image_url,farmer_id=farmer_id,status=status)
        return farmer
    
    @staticmethod
    def get_farm_data(db_session, farmer_id):
        return db_session.query(Farms).filter(Farms.farmer_id == farmer_id).all()
    
    @staticmethod
    def update_farm_stored_data(db_session, id, Location,Details,Description,Image_url):
        farm_data = db_session.query(Farms).filter(Farms.id == id).first()
        farm_data.Location = Location
        farm_data.Details = Details
        farm_data.Description = Description
        farm_data.Image_url = Image_url
        db_session.commit()
        return farm_data
    
    @staticmethod
    def get_farm_data_by_id(db_session, id):
        return db_session.query(Farms).filter(Farms.id == id).first()
    
    @staticmethod
    def get_all_farm_data(db_session):
        return db_session.query(Farms).all()
    
    @staticmethod
    def update_farm_data(db_session, id, status):
        farm_data = db_session.query(Farms).filter(Farms.id == id).first()
        farm_data.status = status
        db_session.commit()
        return farm_data
    
    @staticmethod
    def delete_farm_data(db_session, id):
        farm_data = db_session.query(Farms).filter(Farms.id == id).first()
        db_session.delete(farm_data)
        db_session.commit()
        return farm_data
    
    @staticmethod
    def get_approved_farms(db_session):
        return db_session.query(Farms).filter(Farms.status == "Approved").all()
    
    @staticmethod
    def get_pending_farms(db_session):
        return db_session.query(Farms).filter(Farms.status == "Requesting").all()
    
    @staticmethod
    def get_pending_count(db_session):
        return db_session.query(Farms).filter(Farms.status == "Requesting").count()
    
    @staticmethod
    def get_farm_count(db_session):
        return db_session.query(Farms).filter(Farms.status == "Approved").count()
    
    @staticmethod
    def farms_owned_by_farmer(db_session, farmer_id):
        return db_session.query(Farms).filter(Farms.farmer_id == farmer_id).all()
    
class Tourist(Base):
    __tablename__ = 'tourists'
    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String)
    Email = Column(String)
    Phonenumber = Column(String)
    Number = Column(Integer)
    status  = Column(String)
    bookings = relationship("Booking", back_populates="tourist")

    @staticmethod
    def create_tourist_data(Name,Email,Phonenumber,Number,status):
        print("""Creating tourist""")
        tourist = Tourist(Name=Name, Email = Email, Phonenumber=Phonenumber, Number=Number, status=status)
        return tourist
    
    @staticmethod
    def get_tourist_data(db_session, id):
        return db_session.query(Tourist).filter(Tourist.id == id).first()
    
    @staticmethod
    def get_tourist_data_by_id(db_session, id):
        return db_session.query(Tourist).filter(Tourist.id == id).first()
    
    @staticmethod
    def get_all_tourist_data(db_session):
        return db_session.query(Tourist).all()
    
    @staticmethod
    def update_tourist_data(db_session,data):
        tourist_data = db_session.query(Tourist).filter(Tourist.id == data["id"]).first()
        tourist_data.Name = data["Name"]
        tourist_data.Email = data["Email"]
        tourist_data.Phonenumber = data["Phonenumber"]
        tourist_data.Number = data["Number"]
        db_session.commit()
        return {"message": "Tourist updated successfully", "status": 200}
    
    @staticmethod
    def delete_tourist_data(db_session, id):
        tourist_data = db_session.query(Tourist).filter(Tourist.id == id).first()
        db_session.delete(tourist_data)
        db_session.commit()
        return tourist_data

class Booking(Base):
    __tablename__ = 'booking'
    id = Column(Integer, primary_key=True, index=True)
    Farmid = Column(Integer, ForeignKey('farms.id'))
    Touristid = Column(Integer, ForeignKey('tourists.id'))
    status  = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    payment_status = Column(String)
    payment_amount = Column(Float)
    is_cancelled = Column(Boolean, default=False)
    cancellation_fee = Column(Float, default=0.0)
    rescheduled_to = Column(DateTime, nullable=True)
    farms = relationship("Farms", back_populates="bookings")
    tourist = relationship("Tourist", back_populates="bookings")

    @staticmethod
    def create_booking(Farmid,Touristid,status,start_datetime,end_datetime,payment_status,payment_amount):
        print("""Creating booking""")
        booking = Booking(Farmid=Farmid,Touristid=Touristid,status=status,start_datetime=start_datetime,end_datetime=end_datetime,payment_status=payment_status,payment_amount=payment_amount)
        return booking
    
    @staticmethod
    def get_booking(db_session, id):
        return db_session.query(Booking).filter(Booking.id == id).first()
    
    @staticmethod
    def get_pending_bookings(db_session, Farmid):
        return db_session.query(Booking).filter(Booking.Farmid == Farmid,Booking.status == "pending").all()
    
    @staticmethod
    def get_done_bookings(db_session, Farmid):
        return db_session.query(Booking).filter(Booking.Farmid == Farmid,Booking.status == "mark_as_done").all()
    
    @staticmethod
    def update_booking_data(db_session, id, status):
        booking_data = db_session.query(Booking).filter(Booking.id == id).first()
        booking_data.status = status
        db_session.commit()
        return booking_data
    
    @staticmethod
    def get_bookings_for_farmer(db_session, farmer_id):
        return db_session.query(Booking).filter(Booking.Farmid == farmer_id).all()

    #retrving all bookings for a farm
    @staticmethod
    def get_bookings_for_farm(db_session, farm_ids):
        return db_session.query(Booking).filter(Booking.Farmid.in_(farm_ids)).all()
    
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
        