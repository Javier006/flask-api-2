from flask_sqlalchemy import SQLAlchemy
#from flask_login import UserMixin

db = SQLAlchemy()
#UserMixin
class Users(db.Model):
    __tabalename__ = 'users'
    cod_users = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nick_name = db.Column(db.String(20), nullable=False, unique=True)
    u_password = db.Column(db.String(80), nullable=False)

class Profiles(db.Model):
    __tabalename__ = 'profiles'
    cod_profile = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

class Users_profiles(db.Model):
    __tabalename__ = 'users_profiles'
    cod_profile = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_users_id = db.Column(db.Integer, db.ForeignKey('users.cod_users'))
    cod_profile_id = db.Column(db.Integer, db.ForeignKey('profiles.cod_profile'))

class Type(db.Model):
    __tabalename__ = 'type'
    cod_type = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))

    def obtener(self):
        return{
            'cod_type':self.cod_type,
            'name':self.name
        }

class Model(db.Model):
    __tabalename__ = 'model'
    cod_model = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))

    def obtener(self):
        return{
            'cod_model':self.cod_model,
            'name':self.name
        }

class Brand(db.Model):
    __tabalename__ = 'brand'
    cod_brand = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))

    def obtener(self):
        return{
            'cod_brand':self.cod_brand,
            'name':self.name
        }

class Pc(db.Model):
    __tablename__= 'pc'
    cod_pc = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_computer = db.Column(db.String(30))
    serial_number = db.Column(db.String(50), nullable=False, unique=True)
    date_received = db.Column(db.DateTime)
    cod_model_id = db.Column(db.Integer, db.ForeignKey('model.cod_model'))
    cod_brand_id = db.Column(db.Integer, db.ForeignKey('brand.cod_brand'))
    cod_type_id = db.Column(db.Integer, db.ForeignKey('type.cod_type'))
    cod_users_id = db.Column(db.Integer, db.ForeignKey('users.cod_users'))


class State(db.Model):
    __tablename__= 'state'
    cod_state = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_state = db.Column(db.String(20))


class State_pc(db.Model):
    __tabalename__ = 'state_pc'
    cod_state_pc = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_pc_id = db.Column(db.Integer, db.ForeignKey('pc.cod_pc'))
    cod_state_id = db.Column(db.Integer, db.ForeignKey('state.cod_state'))
    cod_pusers_id = db.Column(db.Integer, db.ForeignKey('pc_users.cod_pusers'))
    deliver_date = db.Column(db.DateTime)
    commnet = db.Column(db.String(100))

class Pc_users(db.Model):
    __tabalename__ = 'pc_users'
    cod_pusers = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lastname_user = db.Column(db.String(100))
    create_date = db.Column(db.DateTime)
    




#crear tablas en db
#with app.app_context():
#    db.create_all()




