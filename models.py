from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    cod_user = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nick_name = db.Column(db.String(20), nullable=False, unique=True)
    u_password = db.Column(db.String(80), nullable=False)

class Profiles(db.Model):
    __tablename__ = 'profiles'
    cod_profile = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

    def obtener(self):
        return{
            'cod_profile' : self.cod_profile,
            'name_profile' : self.name
        }

class Users_profiles(db.Model):
    __tablename__ = 'users_profiles'
    cod_profile = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cod_user_id = db.Column(db.Integer, db.ForeignKey('users.cod_user'))
    cod_profile_id = db.Column(db.Integer, db.ForeignKey('profiles.cod_profile'))

class Type(db.Model):
    __tablename__ = 'type'
    cod_type = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_type = db.Column(db.String(20))

    def obtener(self):
        return{
            'cod_type':self.cod_type,
            'name_type':self.name_type
        }
    
class State(db.Model):
    __tablename__= 'state'
    cod_state = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_state = db.Column(db.String(20))

    def obtener(self):
        return{
            'cod_state': self.cod_state,
            'name_state': self.name_state
        }

class Model(db.Model):
    __tabalename__ = 'model'
    cod_model = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_model = db.Column(db.String(20))

    def obtener(self):
        return{
            'cod_model':self.cod_model,
            'name_model':self.name_model
        }

class Brand(db.Model):
    __tablename__ = 'brand'
    cod_brand = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_brand = db.Column(db.String(20))

    def obtener(self):
        return{
            'cod_brand':self.cod_brand,
            'name_brand':self.name_brand
        }

class Pc(db.Model):
    __tablename__= 'pc'
    cod_pc = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name_computer = db.Column(db.String(50), nullable=False, unique=True)
    service_tag = db.Column(db.String(50), nullable=False, unique=True)
    date_received = db.Column(db.DateTime)
    cod_model_id = db.Column(db.Integer, db.ForeignKey('model.cod_model'))
    cod_brand_id = db.Column(db.Integer, db.ForeignKey('brand.cod_brand'))
    cod_type_id = db.Column(db.Integer, db.ForeignKey('type.cod_type'))
    cod_user_id = db.Column(db.Integer, db.ForeignKey('users.cod_user'))
    cod_state_id = db.Column(db.Integer, db.ForeignKey('state.cod_state'))


class Employes(db.Model):
    __tablename__ = 'employes'
    cod_employes = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gps_id = db.Column(db.String(12))
    lastname_user = db.Column(db.String(100))
    archivo = db.Column(db.String(200))
    create_date = db.Column(db.DateTime)
    cod_employe_id = db.Column(db.Integer, db.ForeignKey('employes_state.cod_employe_state'))
    cod_pc_id = db.Column(db.Integer, db.ForeignKey('pc.cod_pc'))
    date_delivery = db.Column(db.DateTime)

class Employes_state(db.Model):
    __tablename__= 'employes_state'
    cod_employe_state = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_employe = db.Column(db.String(12))

class Log(db.Model):
    __tablename__= 'log'
    cod_log = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_pc_id = db.Column(db.Integer)
    log_pc_nc = db.Column(db.String(50))
    log_pc_st = db.Column(db.String(50))
    log_date = db.Column(db.DateTime)
    log_state = db.Column(db.String(12))
    log_archivo = db.Column(db.String(200))
    log_cod_user_id = db.Column(db.Integer)


    



