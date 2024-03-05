from sqlalchemy import Column, Boolean, Float, Integer, String, DateTime,ForeignKey,Enum as SQLAEnum
from sqlalchemy.orm import relationship,joinedload
from sqlalchemy.orm import Session
from enum import Enum
from Connections.connections import Base,engine
import jwt, random
from Connections.token_and_keys import SECRET_KEY,ALGORITHM
import datetime
import secrets
from datetime import datetime,timedelta
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
    # farms = relationship("Farms", back_populates="farmer")

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

class ModelFarmers(Base):
    __tablename__ = 'modelfarmers'

    id = Column(Integer, primary_key=True, index=True) 
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, nullable= True, unique=True)
    role = Column(String)
    phonenumber = Column(String)
    password = Column(String)
    experience = Column(String)
    background = Column(String)
    farms = relationship("Farms", back_populates="modelfarmer")

    @staticmethod
    def create_model_farmer(firstname,lastname,email,phonenumber,password):
        print("""Creating user""")
        hashed_password = Harsher.get_hash_password(password)
        user = ModelFarmers(firstname=firstname,lastname=lastname,email=email,role="modelfarmer",phonenumber=phonenumber,password=hashed_password)
        return user
    
    @staticmethod
    def get_model_farmer(db_session, email_or_phone):
        return db_session.query(ModelFarmers).filter((ModelFarmers.email == email_or_phone) | (ModelFarmers.phonenumber == email_or_phone)).first()

    def verify_password(self, password):
        return Harsher.verify_password(password, self.password)
    
    def update_password(self, new_password):
        hashed_password = Harsher.get_hash_password(new_password)
        print(f"Updating password to: {hashed_password}") 
        self.password = hashed_password

    def get_model_farmer_by_id(db_session, id):
        return db_session.query(ModelFarmers).filter(ModelFarmers.id == id).first()

    @staticmethod
    def get_model_farmer_by_email_or_phone(db_session, email, phone):
        query = db_session.query(ModelFarmers)
        if email:
            query = query.filter(ModelFarmers.email == email)
        if phone:
            query = query.filter(ModelFarmers.phonenumber == phone)
        return query.first()
    
    @staticmethod
    def update_modal_farmer(db_session, id, experience, background):
        farmer = db_session.query(ModelFarmers).filter(ModelFarmers.id == id).first()
        farmer.experience = experience
        farmer.background = background
        db_session.commit()
        return farmer
    
class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True, index=True) 
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String, nullable= True, unique=True)
    phone_number = Column(String, nullable= True, unique=True)
    password = Column(String)
    role = Column(String , default="admin")

    @staticmethod
    def create_admin(db_session,firstname, lastname, email, phone_number, password):
        try:
            print("Creating admin")
            hashed_password = Harsher.get_hash_password(password)
            admin = Admin(firstname=firstname, lastname=lastname, email=email, phone_number=phone_number, password=hashed_password, role="admin")
            db_session.add(admin)
            db_session.commit()
            return admin
        except Exception as e:
            db_session.rollback()
            print(f"Error occurred during admin creation: {e}")
            raise e
    
    @staticmethod
    def get_admin(db_session, email_or_access):
        return db_session.query(Admin).filter((Admin.email == email_or_access) | (Admin.phone_number == email_or_access)).first()
    
    @staticmethod
    # def username_exists(db_session, employee_access):
    #     return db_session.query(Admin).filter(Admin.phone_number == employee_access).first() is not None
    
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
            query = query.filter(Admin.phone == phone)
        return query.first()
    
class AdminSignUpToken(Base):
    __tablename__ = 'admin_sign_up_token'

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String, unique=True, nullable=False) 
    email = Column(String, nullable=False)
    time = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="False")
    added_by = Column(Integer, ForeignKey('admin.id'))

    @staticmethod
    def create_token(db_session, email, admin_id):
        print(f"Creating token for email {email} by admin {admin_id}")
        jti = str(random.randint(10000000, 99999999))
        existing_token = db_session.query(AdminSignUpToken).filter_by(email=email).first()
        if existing_token:
            existing_token.jti = jti
            existing_token.time = datetime.utcnow()
            existing_token.status = "False"
            existing_token.added_by = admin_id
            token_to_return = existing_token
        else:
            new_token_entry = AdminSignUpToken(jti=jti, email=email, added_by=admin_id)
            db_session.add(new_token_entry)
            db_session.flush()
            token_to_return = new_token_entry

        try:
            db_session.commit()
            return {
                "id": token_to_return.id,
                "token": token_to_return.jti,
                "email": token_to_return.email,
                "status": token_to_return.status,
                "time": token_to_return.time,
                "added_by": token_to_return.added_by
            }
        except Exception as e:
            db_session.rollback()
            print(f"Error in token creation or update: {e}")
            return None

    @staticmethod
    def validate_token(db_session, email, token):
        print(f"received token {token} for email {email}")
        try:
            token_record = db_session.query(AdminSignUpToken).filter(
                AdminSignUpToken.email == email,
                AdminSignUpToken.jti == token,
                AdminSignUpToken.status == "False"
            ).first()
            token_validity_period = timedelta(hours=24)

            if token_record:
                token_age = datetime.utcnow() - token_record.time
                if token_age <= token_validity_period:
                    token_record.status = "True"
                    db_session.commit()
                    return True
                else:
                    
                    print(f"Token {token} for email {email} has expired.")
                    return False
            else:
            
                print(f"No valid token found for email {email} with token {token}.")
                return False
        except Exception as e:
            print(f"Exception during token validation for email {email} with token {token}: {e}")
            return False

        
    @staticmethod
    def mark_token_as_used(db_session, jti):
        token_record = db_session.query(AdminSignUpToken).filter(AdminSignUpToken.jti == jti).first()
        if token_record:
            token_record.status = "True"
            db_session.commit()
            return True
        return False
    
    @staticmethod
    def get_token_by_admin(db_session, admin_id):
        return db_session.query(AdminSignUpToken).filter(AdminSignUpToken.added_by == admin_id).all()

    @staticmethod
    def delete_token(db_session, jti):
        token_record = db_session.query(AdminSignUpToken).filter(AdminSignUpToken.jti == jti).first()
        if token_record:
            db_session.delete(token_record)
            db_session.commit()
            return True
        return False

class UsernameChangeRequest(BaseModel):
    current_username: str
    new_username_prefix: str

class Farms(Base):
    __tablename__ = 'farms'
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey('modelfarmers.id'))
    Location = Column(String)
    status = Column(String)
    name = Column(String)
    method = Column(String)
    services = Column(String)
    farm_description = Column(String)
    method_description = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
    approved_by = Column(Integer, nullable=True)

    # farmer = relationship("Farmers", back_populates="farms")
    bookings = relationship("Booking", back_populates="farms")
    modelfarmer = relationship("ModelFarmers", back_populates="farms")
    images = relationship("FarmImage", back_populates="farms")

    @staticmethod
    def create_farm_data(farmer_id,Location, status, Name, Method, Services, farm_description, method_description):
        print("""Creating farm""")
        farm = Farms(Location=Location, name=Name, method=Method, services=Services,farm_description = farm_description, 
                    method_description = method_description, farmer_id=farmer_id, status=status)
        return farm

    @staticmethod
    def get_farm_data(db_session, farmer_id):
        return db_session.query(Farms).filter(Farms.farmer_id == farmer_id).all()
    
    @staticmethod
    def update_farm_stored_data(db_session, id, Location, Name, Method, Services, farm_description, method_description):
        farm_data = db_session.query(Farms).filter(Farms.id == id).first()
        farm_data.Location = Location
        farm_data.name = Name
        farm_data.method = Method
        farm_data.services = Services
        farm_data.farm_description = farm_description
        farm_data.method_description = method_description
        db_session.commit()
        return farm_data
    
    @staticmethod
    def get_farm_data_by_id(db: Session, id):
        # return db_session.query(Farms).filter(Farms.id == id).first()
        return db.query(Farms).options(joinedload(Farms.images),joinedload(Farms.modelfarmer)).filter(Farms.id == id).first()
    @staticmethod
    def get_all_farm_data(db_session):
        return db_session.query(Farms).all()
    
    @staticmethod
    def update_farm_data(db:Session, id, status, approved_by_id):
        farm_data = db.query(Farms).filter(Farms.id == id).first()
        if farm_data:
            farm_data.status = status
            farm_data.approved_by = approved_by_id
            db.commit()
            return farm_data
        else:
            raise Exception("Farm not found")
    
    @staticmethod
    def delete_farm_data(db_session, id):
        farm_data = db_session.query(Farms).filter(Farms.id == id).first()
        db_session.delete(farm_data)
        db_session.commit()
        return farm_data
    
    @staticmethod
    def get_approved_farms(db: Session):
        # return db_session.query(Farms).filter(Farms.status == "approved").all()
        return db.query(Farms).options(joinedload(Farms.images),joinedload(Farms.modelfarmer)).filter(Farms.status == "approved").all()
    
    @staticmethod
    def get_pending_farms(db: Session):
        return db.query(Farms).options(joinedload(Farms.images),joinedload(Farms.modelfarmer)).filter(Farms.status == "requesting").all()
    
    @staticmethod
    def get_pending_count(db_session):
        return db_session.query(Farms).filter(Farms.status == "requesting").count()
    
    @staticmethod
    def get_farm_count(db_session):
        return db_session.query(Farms).filter(Farms.status == "approved").count()
    
    @staticmethod
    def farms_owned_by_farmer(db_session, farmer_id):
        return db_session.query(Farms).filter(Farms.farmer_id == farmer_id).all()
    
class FarmImage(Base):
    __tablename__ = 'farm_images'

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey('farms.id')) 
    image_url = Column(String, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    farms = relationship("Farms", back_populates="images")

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
    touristname = Column(String)
    touristcontact = Column(String)
    touristnumber = Column(Integer)
    status  = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    payment_status = Column(String)
    payment_amount = Column(Float)
    is_institution = Column(Boolean, default=False)
    student_number = Column(Integer, nullable=True)
    main_teacher_fullname = Column(String, nullable=True)
    is_cancelled = Column(Boolean, default=False)
    cancellation_fee = Column(Float, default=0.0)
    rescheduled_to = Column(DateTime, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow) 
    farms = relationship("Farms", back_populates="bookings")
    tourist = relationship("Tourist", back_populates="bookings")

    @staticmethod
    def create_booking(Farmid, Touristid, status, start_datetime, end_datetime, payment_status, payment_amount, is_institution, student_number, main_teacher_fullname, tourist_name, tourist_contact, tourist_number):
        print("""Creating booking""")
        booking = Booking(Farmid=Farmid, Touristid=Touristid, status=status, start_datetime=start_datetime, 
                          end_datetime=end_datetime, payment_status=payment_status, payment_amount=payment_amount, is_institution=is_institution,
                            student_number=student_number, main_teacher_fullname=main_teacher_fullname, touristname=tourist_name, touristcontact=tourist_contact, touristnumber=tourist_number)
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
        booking_data.updated_at = datetime.utcnow()
        db_session.commit()
        return booking_data
    
    @staticmethod
    def get_bookings_for_farmer(db_session, farmer_id):
        return db_session.query(Booking).filter(Booking.Farmid == farmer_id).all()

    #retrving all bookings for a farm
    @staticmethod
    def get_bookings_for_farm(db_session, farm_ids):
        return db_session.query(Booking).filter(Booking.Farmid.in_(farm_ids)).all()
    
class Agents(Base):
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    email = Column(String)
    phone_number = Column(String)
    password = Column(String)
    status = Column(String)
    role = Column(String, default="agent")

    @staticmethod
    def create_agent(Firstname, Lastname, Email,Phonenumber,Password,status):
        print("""Creating agent""")
        agent = Agents(firstname=Firstname, lastname = Lastname, email = Email, phone_number=Phonenumber, password=Password, status=status)
        return agent
    
    @staticmethod
    def get_agent(db_session, email_or_phone):
        return db_session.query(Agents).filter((Agents.email == email_or_phone) | (Agents.phone_number == email_or_phone)).first()
    
    @staticmethod
    def get_agent_data_by_id(db_session, id):
        return db_session.query(Agents).filter(Agents.id == id).first()
    
    @staticmethod
    def get_all_agent_data(db_session):
        return db_session.query(Agents).all()
    
    @staticmethod
    def update_agent_data(db_session,data):
        agent_data = db_session.query(Agents).filter(Agents.id == data["id"]).first()
        agent_data.first_name = data["Name"]
        agent_data.email = data["Email"]
        agent_data.phone_number = data["Phonenumber"]
        db_session.commit()
        return {"message": "Agent updated successfully", "status": 200}
    
    @staticmethod
    def delete_agent_data(db_session, id):
        agent_data = db_session.query(Agents).filter(Agents.id == id).first()
        db_session.delete(agent_data)
        db_session.commit()
        return agent_data
    
class Community(Base):
    __tablename__ = 'community'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    profile_picture = Column(String)
    created_by = Column(Integer, ForeignKey('modelfarmers.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    followers = relationship("CommunityFollowers", back_populates="community")
    # posts = relationship("CommunityPosts", back_populates="community")
    @staticmethod
    def create_community(Name, Profile_picture,created_by):
        print("""Creating community""")
        community = Community(name=Name, profile_picture = Profile_picture, created_by=created_by)
        return community
    
    @staticmethod
    def get_community(db_session, id):
        return db_session.query(Community).filter(Community.id == id).first()

    @staticmethod
    def get_all_community(db_session):
        return db_session.query(Community).all()
    
    @staticmethod
    def update_community(db_session,data):
        community = db_session.query(Community).filter(Community.id == data["id"]).first()
        community.name = data["name"]
        community.profile_picture = data["profile_picture"]
        community.created_by = data["created_by"]
        db_session.commit()
        return {"message": "Community updated successfully", "status": 200}
    
    @staticmethod
    def delete_community(db_session, id):
        community = db_session.query(Community).filter(Community.id == id).first()
        db_session.delete(community)
        db_session.commit()
        return community

# class RoleEnum(Enum):
#     ADMIN = "admin"
#     OWNER = "owner"
#     FOLLOWER = "follower"
    
class CommunityFollowers(Base):
    __tablename__ = 'community_followers'

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey('community.id'))
    follower_id = Column(Integer)
    followed_at = Column(DateTime, default=datetime.utcnow)
    role = Column(String, default="follower")
    community = relationship("Community", back_populates="followers")
    # posts = relationship("CommunityPosts", back_populates="community")

    @staticmethod
    def create_community_follower(db_session, community_id, follower_id, role):

        # if role not in [RoleEnum.ADMIN.value, RoleEnum.OWNER.value, RoleEnum.FOLLOWER.value]:
        #     raise ValueError("Invalid role specified")

        community_follower = CommunityFollowers(community_id=community_id, follower_id=follower_id, role=role)
        db_session.add(community_follower)
        db_session.commit()
        return community_follower
    
    @staticmethod
    def create_community_owner(db_session, community_id, follower_id):
        community_follower = CommunityFollowers(community_id=community_id, follower_id=follower_id, role="owner")
        db_session.add(community_follower)
        db_session.commit()
        return community_follower

    @staticmethod
    def get_community_follower(db_session, id):
        return db_session.query(CommunityFollowers).filter(CommunityFollowers.id == id).first()

    @staticmethod
    def get_all_community_followers(db_session):
        return db_session.query(CommunityFollowers).all()
    
    @staticmethod
    def update_community_follower(db_session,data):
        community_follower = db_session.query(CommunityFollowers).filter(CommunityFollowers.id == data["id"]).first()
        community_follower.community_id = data["community_id"]
        community_follower.follower_id = data["follower_id"]
        db_session.commit()
        return {"message": "Community follower updated successfully", "status": 200}
    
    @staticmethod
    def delete_community_follower(db_session, id):
        community_follower = db_session.query(CommunityFollowers).filter(CommunityFollowers.id == id).first()
        db_session.delete(community_follower)
        db_session.commit()
        return community_follower
    
# class CommunityFollower(Base):
#     __tablename__ = 'community_follower'

#     id = Column(Integer, primary_key=True, index=True)
#     community_id = Column(Integer, ForeignKey('community.id'))
#     follower_id = Column(Integer)
#     followed_at = Column(DateTime, default=datetime.utcnow)
#     role = Column(String, default="follower")
#     community = relationship("Community", back_populates="followers")
#     # posts = relationship("CommunityPosts", back_populates="community")

#     @staticmethod
#     def create_community_follower(db_session, community_id, follower_id, role):

#         # if role not in [RoleEnum.ADMIN.value, RoleEnum.OWNER.value, RoleEnum.FOLLOWER.value]:
#         #     raise ValueError("Invalid role specified")

#         community_follower = CommunityFollower(community_id=community_id, follower_id=follower_id, role=role)
#         db_session.add(community_follower)
#         db_session.commit()
#         return community_follower
    
#     @staticmethod
#     def create_community_owner(db_session, community_id, follower_id):
#         community_follower = CommunityFollower(community_id=community_id, follower_id=follower_id, role="owner")
#         db_session.add(community_follower)
#         db_session.commit()
#         return community_follower

#     @staticmethod
#     def get_community_follower(db_session, id):
#         return db_session.query(CommunityFollower).filter(CommunityFollower.id == id).first()

#     @staticmethod
#     def get_all_community_followers(db_session):
#         return db_session.query(CommunityFollower).all()
    
#     @staticmethod
#     def update_community_follower(db_session,data):
#         community_follower = db_session.query(CommunityFollower).filter(CommunityFollower.id == data["id"]).first()
#         community_follower.community_id = data["community_id"]
#         community_follower.follower_id = data["follower_id"]
#         db_session.commit()
#         return {"message": "Community follower updated successfully", "status": 200}
    
#     @staticmethod
#     def delete_community_follower(db_session, id):
#         community_follower = db_session.query(CommunityFollower).filter(CommunityFollower.id == id).first()
#         db_session.delete(community_follower)
#         db_session.commit()
#         return community_follower

class CommunityMessages(Base):
    __tablename__ = 'community_messages'

    id = Column(Integer, primary_key=True, index=True)
    community_id = Column(Integer, ForeignKey('community.id'))
    sender_id = Column(Integer, ForeignKey('farmers.id'))
    message = Column(String)
    sent_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def create_community_message(community_id, sender_id, message):
        print("""Creating community message""")
        community_message = CommunityMessages(community_id=community_id, sender_id=sender_id, message=message)
        return community_message
    
    @staticmethod
    def get_community_message(db_session, id):
        return db_session.query(CommunityMessages).filter(CommunityMessages.id == id).first()

    @staticmethod
    def get_all_community_messages(db_session):
        return db_session.query(CommunityMessages).all()
    
    @staticmethod
    def Edit_community_message(db_session,data):
        community_message = db_session.query(CommunityMessages).filter(CommunityMessages.id == data["id"]).first()
        community_message.community_id = data["community_id"]
        community_message.sender_id = data["sender_id"]
        community_message.message = data["message"]
        db_session.commit()
        return {"message": "Community message updated successfully", "status": 200}
    
    @staticmethod
    def delete_community_message(db_session, id):
        community_message = db_session.query(CommunityMessages).filter(CommunityMessages.id == id).first()
        db_session.delete(community_message)
        db_session.commit()
        return community_message

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    image_url = Column(String)
    status = Column(String, default="requesting")
    added_by = Column(Integer)
    approved_by = Column(Integer, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def create_event(db_session, name, description, start_time, end_time, image_url,added_by):
        event = Event(name=name, description=description, start_time=start_time, end_time=end_time, image_url=image_url, added_by=added_by)

        db_session.add(event)
        db_session.commit()
        return event
    
    @staticmethod
    def get_event(db_session, id):
        return db_session.query(Event).filter(Event.id == id).first()
    
    @staticmethod
    def get_all_events(db_session):
        return db_session.query(Event).all()
    
    @staticmethod
    def get_event_for_a_user(db_session, added_by):
        return db_session.query(Event).filter(Event.added_by == added_by).all()
    
    @staticmethod
    def approving_an_event(db_session, id, admin_id):
        event = db_session.query(Event).filter(Event.id == id).first()
        if event:
            event.status = "approved"
            event.approved_by = admin_id
            db_session.commit()
            return event
        else:
            raise Exception("Event not found")
        
    @staticmethod
    def displaying_approved_events(db_session):
        return db_session.query(Event).filter(Event.status == "approved").all()
    
    @staticmethod
    def displaying_pending_events(db_session):
        return db_session.query(Event).filter(Event.status == "requesting").all()
    
    @staticmethod
    def get_pending_count(db_session):
        return db_session.query(Event).filter(Event.status == "requesting").count()
    
    @staticmethod
    def update_event(db_session, id, name, description, start_time, end_time, image_url):
        event = db_session.query(Event).filter(Event.id == id).first()
        event.name = name
        event.description = description
        event.start_time = start_time
        event.end_time = end_time
        event.image_url = image_url
        db_session.commit()
        return event
    
    @staticmethod
    def delete_event(db_session, id):
        event = db_session.query(Event).filter(Event.id == id).first()
        db_session.delete(event)
        db_session.commit()
        return event
    
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
        