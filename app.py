from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
import os, uuid
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, Users, Profiles, Users_profiles, Type, Model, Brand, Pc_users, State, Pc, State_pc

app = Flask(__name__)

# Configuración base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/afn'

#folder pdf
app.config['UPLOAD_FOLDER'] = './pdf_afn'

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = '9123'
jwt = JWTManager(app)

bcrypt = Bcrypt(app)
#supports_credentials permite el envio de cookies
CORS(app, supports_credentials=True)
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(nick_name=username).first()

        if user and bcrypt.check_password_hash(user.u_password, password):
            # Crear un token de acceso
            access_token = create_access_token(identity=user.cod_users)
            response = make_response(jsonify(access_token=access_token), 200)
            response.set_cookie('access_token_cookie', value=access_token, httponly=True, samesite='None',secure=True)

            return response

    return jsonify({'error': 'Credenciales inválidas'}), 401

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Desconectado'}), 200

@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existe_user = Users.query.filter_by(nick_name=username).first()
        if existe_user:
            return jsonify({'message': 'El nombre de usuario ya está en uso. Elige otro.'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Users(nick_name=username, u_password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201

    return jsonify({'message': 'Registro fallido'}), 400

@app.route('/check-token', methods=['GET'])
@jwt_required()
def check_auth():
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)

    user_profile = Users_profiles.query.filter_by(cod_users_id=current_user.cod_users).first()

    user_profile_details = {
        'cod_users' : user_profile.cod_users_id,
        'profile' : user_profile.cod_profile_id
    }

    print(user_profile.cod_profile_id)
    return jsonify({'authenticated': True, 'user_profile': user_profile_details})

#carga pdf ¿donde?
@app.route('/upload_pdf', methods=['POST'])
def uploader():
    if request.method == 'POST':
        pdf = request.files['archivo']
        if pdf:
            filename = secure_filename(pdf.filename)
            unique_filename = str(uuid.uuid4()) +'_'+ filename
            pdf.save(os.path.join(app.config['UPLOAD_FOLDER'], f'_id_{unique_filename}'))
            return jsonify({'message': 'Archivo guardado exitosamente'})
        else:
            return jsonify({'error': 'No se ha enviado un archivo válido'}), 400
    else:
        return jsonify({'error': 'No se encontró el archivo en la solicitud'}), 400


@app.route('/add_user_pc', methods= ['POST'])
@jwt_required()
def add_user_pc():
    if request.method == 'POST':
        lastname_user = request.form['lastname_user']
        create_date = request.form['create_date']
        rut_user = request.form['rut_user']
        
        existe_rut = Pc_users.query.filter_by(rut_user=rut_user).first()
        if  existe_rut:
            return jsonify({"estado":"El rut ya existe."}),400

        new_user_pc = Pc_users(lastname_user=lastname_user,create_date=create_date,rut_user=rut_user)
        db.session.add(new_user_pc)

        estado = State.query.filter_by(name_state='no asignado').first()
        new_statu_user = State_pc(cod_pusers_id=new_user_pc.cod_pusers,cod_state_id=estado.cod_state)
        db.session.add(new_statu_user)

        db.session.commit()
        return jsonify({"estado":"usuario creado"})
    return jsonify({"estado":"Error al agregar"})

@app.route('/add_pc', methods = ['POST'])
@jwt_required()
def create():
    if request.method == 'POST':
        name_computer = request.form['namecomputer']
        serial_name = request.form['nameserial']
        date_received = request.form['datereceived']
        cod_model_id = request.form['namemodel']
        cod_brand_id = request.form['namebrand']
        cod_type_id = request.form['nametype']
        #usuario login
        current_user_id = get_jwt_identity()
        current_user = Users.query.get(current_user_id)

        existe_serial_number = Pc.query.filter_by(serial_number=serial_name).first()
        existe_name_computer = Pc.query.filter_by(name_computer=name_computer).first()
        if existe_serial_number and existe_name_computer:
            return jsonify({'message': 'El nombre de numero de serial y nombre computador ya está en uso.'}), 400
        elif existe_name_computer:
            return jsonify({'message': 'El nombre de computador ya está en uso.'}), 401
        elif existe_serial_number:
            return  jsonify({'message': 'El numero de serial ya está en uso.'}), 402

        new_pc = Pc(name_computer=name_computer,serial_number=serial_name,date_received=date_received,cod_model_id=cod_model_id,cod_brand_id=cod_brand_id,cod_type_id=cod_type_id,cod_users_id=current_user.cod_users)
        db.session.add(new_pc)

        estado = State.query.filter_by(name_state='no asignado').first()
        new_statu_pc = State_pc(cod_pc_id=new_pc.cod_pc,cod_state_id=estado.cod_state)
        db.session.add(new_statu_pc)
        db.session.commit()

        return jsonify({'pc':'Creado'})
        
    return jsonify({'pc':'Error ingreso'})

@app.route('/datos', methods = ['GET'])
def datos():

    models = Model.query.all()
    types = Type.query.all()
    brands = Brand.query.all()
    
    models_json = [model.obtener() for model in models]
    types_json = [tipo.obtener() for tipo in types]
    brand_json = [brand.obtener() for brand in brands]
    datos = {
        'model':models_json,
        'type':types_json,
        'brand': brand_json
    }
    return jsonify(datos)    

@app.route('/get_pc_users', methods = ['GET'])
def get_pc_users():

    resultado = db.session.query(State_pc,Pc_users.rut_user,Pc_users.lastname_user,State.name_state,Pc_users.create_date)\
                .join(Pc_users, State_pc.cod_pusers_id == Pc_users.cod_pusers,isouter=True)\
                .join(State, State_pc.cod_state_id == State.cod_state)\
                .filter(State_pc.cod_pusers_id.isnot(None))\
                .group_by(State_pc.cod_pusers_id)\
                .order_by(Pc_users.create_date.desc())\
                .all()

    data = []
    for user in resultado:
        data.append(
            {
                "lastname_user": user.lastname_user,
                "create_date" : user.create_date,
                "rut_user" : user.rut_user,
                "state_name" : user.name_state
            }
        )
    return jsonify(data)

@app.route('/get_pc', methods = ['GET','POST'])
def get_pc():

    resultado = db.session.query(State_pc,Pc.cod_pc,Pc.name_computer,Pc.serial_number,State.name_state,Pc.date_received,Model.name.label('model_name'),Brand.name.label('brand_name'),Type.name.label('type_name'))\
                .join(Pc, State_pc.cod_pc_id == Pc.cod_pc, isouter=True)\
                .join(Brand, Brand.cod_brand == Pc.cod_brand_id, isouter=True)\
                .join(Model, Model.cod_model == Pc.cod_model_id, isouter=True)\
                .join(Type, Type.cod_type == Pc.cod_type_id, isouter=True)\
                .join(State, State_pc.cod_state_id == State.cod_state)\
                .filter(State_pc.cod_pc_id.isnot(None))\
                .group_by(State_pc.cod_pc_id)\
                .order_by(Pc.date_received.desc())\
                .all()
    
    db.session.commit()

    data = []

    for computer in resultado:
        data.append({
            'cod_pc': computer.cod_pc,
            'name_computer': computer.name_computer,
            'serial_number': computer.serial_number,
            'name_state': computer.name_state,
            'date_received': computer.date_received,
            'name_model': computer.model_name,
            'name_brand': computer.brand_name,
            'name_type': computer.type_name,
            
        })       

    return jsonify(data)

@app.route('/listado', methods = ['GET','POST'])
@jwt_required()
def listado():
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)
    return f'Hello, {current_user.nick_name}!'




@app.route('/datos_prueba')
def addu():

    new_type = Type(name='Notebook')
    new_type2 = Type(name='Netbook')
    new_profile = Profiles(name='Administrador')
    new_profile2 = Profiles(name='Usuario')
    new_brand = Brand(name='Dell')
    new_brand2 = Brand(name='Lenovo')
    new_brand3 = Brand(name='HP')
    new_model = Model(name='modelo1')
    new_model2 = Model(name='modelo2')
    new_model3 = Model(name='modelo3')
    new_state2 = State(name_state='Asignado')
    new_state3 = State(name_state='No asignado')
    new_state4 = State(name_state='Mal estado')
    new_user = Users(nick_name='javier', u_password='$2b$12$9q6oTe2dQoV/YdPIfrVAZeFA4P3fZYdHfQzHmZkeatX2dJto/eiRW')
    db.session.add(new_user)
    db.session.add(new_type)
    db.session.add(new_type2)
    db.session.add(new_profile)
    db.session.add(new_profile2)
    db.session.add(new_brand)
    db.session.add(new_brand2)
    db.session.add(new_brand3)
    db.session.add(new_model)
    db.session.add(new_model2)
    db.session.add(new_model3)
    db.session.add(new_state2)
    db.session.add(new_state3)
    db.session.add(new_state4)
    db.session.commit()

    return jsonify({'datos':'Cargados'})

with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=True)