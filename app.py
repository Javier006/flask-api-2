from flask import Flask, jsonify, request, make_response, send_from_directory
from flask_cors import CORS
import os, uuid, datetime
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, Users, Profiles, Users_profiles, Type, Model, Brand, State, Pc, Employes, Employes_state, Log

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
            access_token = create_access_token(identity=user.cod_user)
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
        profile = request.form['profile']
        existe_user = Users.query.filter_by(nick_name=username).first()
        if existe_user:
            return jsonify({'message': 'El nombre de usuario ya está en uso. Elige otro.'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Users(nick_name=username, u_password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        add_profile = Users_profiles(cod_user_id=new_user.cod_user,cod_profile_id=profile)
        db.session.add(add_profile)
        db.session.commit()

        return jsonify({'message': 'Usuario registrado exitosamente'}), 201

    return jsonify({'message': 'Registro fallido'}), 400

@app.route('/check-token', methods=['GET'])
@jwt_required()
def check_auth():
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)

    user_profile = Users_profiles.query.filter_by(cod_user_id=current_user.cod_user).first()

    user_profile_details = {
        'cod_user' : user_profile.cod_user_id,
        'profile' : user_profile.cod_profile_id
    }
    return jsonify({'authenticated': True, 'user_profile': user_profile_details})

@app.route('/add_employes', methods= ['POST'])
@jwt_required()
def add_user_pc():

    if request.method == 'POST':
        lastname_user = request.form['lastname_user']
        create_date = request.form['create_date']
        gps = request.form['rut_user']
        
        current_user_id = get_jwt_identity()
        current_user = Users.query.get(current_user_id)
        
        existe_rut = Employes.query.filter_by(gps_id=gps).first()
        if  existe_rut:
            return jsonify({"estado":"El GPS id ya esta en uso."}), 400
    
        if gps:
            #agregar empleado
            new_user_pc = Employes(lastname_user=lastname_user, create_date=create_date, gps_id=gps,cod_employe_id=1)
            db.session.add(new_user_pc)
            db.session.commit()
            #registrar Log
            return jsonify({"mensaje":"usuario creado"}), 200
        else:
            return jsonify({"mensaje":"gps faltante"}, 401)

       
    return jsonify({"estado":"Error al agregar"})

@app.route('/edit_employes' , methods=['POST'])
@jwt_required()
def edit_employe():

    if request.method == 'POST':

        gps = request.form['gps_id']
        service_tag = request.form['service_tag']
        archivo = request.files['pdf_file']
        date_delivery = request.form['datedelivery']
        act_estado = request.form['estado']

        current_user_id = get_jwt_identity()
        current_user = Users.query.get(current_user_id)

        data_pc = Pc.query.filter_by(service_tag=service_tag).first()
        data_employes = Employes.query.filter_by(gps_id=gps).first()

        if archivo:
            # tomar archivo y poner otro nombre
            filename = secure_filename(archivo.filename)
            unique_filename = str(uuid.uuid4())+'_'+filename
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'],unique_filename))
                
            #editar estado de pc. 1 = asignado
            data_pc.cod_state_id = 1
            db.session.commit()
            #asignar pc a empleado
            data_employes.cod_pc_id = data_pc.cod_pc    
            db.session.commit()
            #añadir nombre de archivo 
            data_employes.archivo = unique_filename
            db.session.commit()
            #añadir fecha de entrega
            data_employes.date_delivery = date_delivery
            db.session.commit()

            #Registrar LOG - asignar pc
            new_log_asignar = Log(cod_pc_id=data_pc.cod_pc, cod_employe_id=data_employes.cod_employes, cod_user_id=current_user.cod_user, data_log=date_delivery,state_log='asignado',archivo_log=unique_filename)
            db.session.add(new_log_asignar)
            db.session.commit()
            return jsonify({'message': 'Editado exitosamente'})
        else:
            ##unique_filename = None
            #editar estado de pc. 1 = asignado
            data_pc.cod_state_id = 1
            db.session.commit()
            #asignar pc a empleado
            data_employes.cod_pc_id = data_pc.cod_pc    
            db.session.commit()
            #añadir nombre de archivo 
            ##data_employes.archivo = unique_filename
            ##db.session.commit()
            #añadir fecha de entrega
            data_employes.date_delivery = date_delivery
            db.session.commit()

            #Registrar LOG - asignar pc
            new_log_asignar = Log(cod_pc_id=data_pc.cod_pc, cod_employe_id=data_employes.cod_employes, cod_user_id=current_user.cod_user, data_log=date_delivery,state_log='asignado')
            db.session.add(new_log_asignar)
            db.session.commit()
            return jsonify({"mensaje":"asigando sin pdf"})
    return jsonify({"estado":"error al editar"})

@app.route('/quitar_pc' , methods= ['POST'])
@jwt_required()
def quitar_pc():
    if request.method == 'POST':
        st = request.form['service_tag']
        state_pc = request.form['state']

        st_existe = Pc.query.filter_by(service_tag=st).first()
        
        if st_existe:
            st_existe_e = Employes.query.filter_by(cod_pc_id=st_existe.cod_pc).first()
            if st_existe_e:
                # Cambiar estado a pc
                st_existe.cod_state_id = state_pc 
                db.session.commit()

                # quitar pc a empleado
                st_existe_e.cod_pc_id = None
                db.session.commit()
        
            return({"mensaje":"computado quitado"})
            
        return({"mensaje":"error al quitar pc"})

    return({"mensaje":"error al quitar pc"})

@app.route('/reasignar_pc', methods = ['POST'])
def reasigar():
    if request.method == 'POST':

        st = request.form['service_tag']
        state = request.form['state']
        new_st = request.form['new_st']

        existe_st = Pc.query.filter_by(service_tag=st).first()
        
        existe_new_st = Pc.query.filter_by(service_tag=new_st).first()

        if existe_st and existe_new_st:
            
            buscar_id_employe = Employes.query.filter_by(cod_pc_id = existe_st.cod_pc).first()

            if buscar_id_employe:
                # Cambiar estado a pc actual
                existe_st.cod_state_id = state
                db.session.commit()

                # Cambiar estado a pc nuevo
                existe_new_st.cod_state_id = 1
                db.session.commit()

                # Asignar pc nuevo
                buscar_id_employe.cod_pc_id = existe_new_st.cod_pc
                db.session.commit()

                return jsonify({"mensaje":"computador reasignado"})
    return jsonify({"mensaje":"error al reasignar"})


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

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
        if name_computer and serial_name and date_received and cod_brand_id and cod_model_id and cod_type_id:
            current_user_id = get_jwt_identity()
            current_user = Users.query.get(current_user_id)

            existe_service_tag = Pc.query.filter_by(service_tag=serial_name).first()
            existe_name_computer = Pc.query.filter_by(name_computer=name_computer).first()
            if existe_service_tag and existe_name_computer:
                return jsonify({'message': 'El nombre de numero de serial y nombre computador ya está en uso.'}), 400
            elif existe_name_computer:
                return jsonify({'message': 'El nombre de computador ya está en uso.'}), 401
            elif existe_service_tag:
                return  jsonify({'message': 'El numero de serial ya está en uso.'}), 402
            

            new_pc = Pc(name_computer=name_computer,service_tag=serial_name,date_received=date_received,cod_model_id=cod_model_id,cod_brand_id=cod_brand_id,cod_type_id=cod_type_id,cod_user_id=current_user.cod_user,cod_state_id=2)
            db.session.add(new_pc)
            db.session.commit()

            hora_actual = datetime.datetime.now()
            new_log = Log(cod_pc_id=new_pc.cod_pc,cod_user_id=current_user.cod_user,date_log=hora_actual,state_log='no asignado')

            db.session.add(new_log)
            db.session.commit()
            return jsonify({'pc':'Creado'})
    return jsonify({'pc':'Error ingreso'})

@app.route('/add_brand', methods = ['POST'])
def add_brand():

    if request.method == 'POST':
        marca = request.form['marca']
        if marca != 'undefined':
            new_marca = Brand(name_brand = marca)
            db.session.add(new_marca)
            db.session.commit()
            return jsonify({"mensaje":"marca añadida"})
        return jsonify({"mensaje":"debe ingresar nombre de marca"}),401
    return jsonify({"mensaje":"error al añadir marca"})

@app.route('/delete_brand', methods = ['POST'])
def delete_brand():
    if request.method== 'POST':
        cod = request.form['cod_brand']
        existe_brand = Brand.query.filter_by(cod_brand=cod).first()
        if cod != 0:
            if existe_brand:   
                db.session.delete(existe_brand)
                db.session.commit()
                return jsonify({"mensaje":"marca eliminada"})
        return jsonify({"mensaje":"Debe seleccionar una marca para eliminar"}), 401
    return  jsonify({"mensaje":"error al eliminar"})

@app.route('/add_model', methods = ['POST'])
def add_modelo():

    if request.method == 'POST':
        modelo = request.form['modelo']
        if modelo != 'undefined':
            new_modelo = Model(name_model = modelo)
            db.session.add(new_modelo)
            db.session.commit()
            return jsonify({"mensaje":"modelo añadida"})
        return jsonify({"mensaje":"debe ingresar nombre de modelo"}),401
    return jsonify({"mensaje":"error al añadir modelo"})

@app.route('/delete_model', methods = ['POST'])
def delete_modelo():
    if request.method== 'POST':
        cod = request.form['cod_model']
        existe_modelo = Model.query.filter_by(cod_model=cod).first()
        if cod != 0:
            if existe_modelo:   
                db.session.delete(existe_modelo)
                db.session.commit()
                return jsonify({"mensaje":"modelo eliminada"})
        return jsonify({"mensaje":"Debe seleccionar una modelo para eliminar"}), 401
    return  jsonify({"mensaje":"error al eliminar"})

@app.route('/add_type', methods = ['POST'])
def add_tipo():

    if request.method == 'POST':
        tipo = request.form['tipo']
        if tipo != 'undefined':
            new_type = Type(name_type = tipo)
            db.session.add(new_type)
            db.session.commit()
            return jsonify({"mensaje":"tipo añadida"})
        return jsonify({"mensaje":"debe ingresar nombre de tipo"}),401
    return jsonify({"mensaje":"error al añadir tipo"})

@app.route('/delete_type', methods = ['POST'])
def delete_tipo():
    if request.method== 'POST':
        cod = request.form['cod_type']
        existe_tipo = Type.query.filter_by(cod_type=cod).first()
        if cod != 0:
            if existe_tipo:   
                db.session.delete(existe_tipo)
                db.session.commit()
                return jsonify({"mensaje":"tipo eliminada"})
        return jsonify({"mensaje":"Debe seleccionar un tipo para eliminar"}), 401
    return  jsonify({"mensaje":"error al eliminar"})

@app.route('/datos', methods = ['GET'])
def datos():

    models = Model.query.all()
    types = Type.query.all()
    brands = Brand.query.all()
    profiles =  Profiles.query.all()
    states = State.query.all()
    
    models_json = [model.obtener() for model in models]
    types_json = [tipo.obtener() for tipo in types]
    brand_json = [brand.obtener() for brand in brands]
    profiles_json = [profile.obtener() for profile in profiles]
    states_json = [state.obtener() for state in states]
    datos = {
        'model':models_json,
        'type':types_json,
        'brand': brand_json,
        'profile': profiles_json,
        'state': states_json
    }
    return jsonify(datos)    

@app.route('/estado', methods = ['GET'])
def estado():

    states = State.query.all()

    states_json = [state.obtener() for state in states]

    datos = {
        'state': states_json 
    }

    return jsonify(datos)

@app.route('/get_pc_users', methods = ['GET'])
def get_pc_users():

    resultado = db.session.query(Employes,Employes.cod_employes,Pc.service_tag,Employes.archivo,Employes.date_delivery, Employes.gps_id,Employes.lastname_user,Employes.create_date,Employes_state.state_employe)\
                .join(Employes_state, Employes.cod_employe_id == Employes_state.cod_employe_state)\
                .join(Pc, Employes.cod_pc_id == Pc.cod_pc, isouter=True)\
                .order_by((Pc.service_tag == None).desc())\
                .order_by(Employes.create_date.desc())\
                .all()

    data = []
    for user in resultado:
        data.append(
            {
                "cod_pusers" : user.cod_employes,
                "lastname_user": user.lastname_user,
                "create_date" : user.create_date,
                "gps_id" : user.gps_id,
                "service_tag" : user.service_tag,
                "archivo" : user.archivo,
                "date_delivery" : user.date_delivery
            }
        )

    return jsonify(data)

@app.route('/get_pc', methods = ['GET','POST'])
def get_pc():

    resultado = db.session.query(Pc,Pc.cod_pc,Pc.name_computer,Pc.service_tag,Pc.date_received,Employes.lastname_user,Brand.name_brand,Model.name_model,Type.name_type,State.name_state)\
                .join(Brand, Pc.cod_brand_id == Brand.cod_brand)\
                .join(Model, Pc.cod_model_id == Model.cod_model)\
                .join(Type, Pc.cod_type_id == Type.cod_type)\
                .join(State, Pc.cod_state_id == State.cod_state)\
                .join(Employes, Pc.cod_pc == Employes.cod_pc_id, isouter=True)\
                .order_by((Pc.cod_state_id == 2).desc())\
                .order_by((Pc.cod_state_id == 3).desc())\
                .order_by((Pc.cod_state_id == 1).desc())\
                .order_by((Pc.cod_state_id == 4).desc())\
                .order_by((Pc.cod_state_id == 5).desc())\
                .order_by(Pc.date_received.desc())\
                .all()


    data = []

    for computer in resultado:
        data.append({
            'cod_pc': computer.cod_pc,
            'name_computer': computer.name_computer,
            'service_tag': computer.service_tag,
            'name_state': computer.name_state,
            'date_received': computer.date_received,
            'name_model': computer.name_model,
            'name_brand': computer.name_brand,
            'name_type': computer.name_type,
            'name_user': computer.lastname_user
            
        })       

    return jsonify(data)

@app.route('/listado', methods = ['GET','POST'])
@jwt_required()
def listado():
    current_user_id = get_jwt_identity()
    current_user = Users.query.get(current_user_id)
    return f'Hello, {current_user.nick_name}!'

@app.route('/get_noasignado',  methods = ['GET'])
def get_noasignado():

    resultado = db.session.query(Pc, Pc.service_tag,State.cod_state)\
                .join(State, Pc.cod_state_id == State.cod_state)\
                .filter(State.cod_state == 2)\
                .all()
    data = []
    for d in resultado:
        data.append({ 
                    'state' : d.cod_state,
                    'service_tag' : d.service_tag   
                    })
    return jsonify(data)


@app.route('/datos_prueba')
def addu():

    new_type = Type(name='notebook')
    new_profile = Profiles(name='administrador')
    new_profile2 = Profiles(name='usuario')
    new_brand = Brand(name='dell')
    new_model = Model(name='modelo1')
    new_model2 = Model(name='modelo2')
    new_model3 = Model(name='modelo3')
    new_state2 = State(name_state='asignado')
    new_state3 = State(name_state='no asignado')
    new_state4 = State(name_state='mal estado')
    new_user = Users(nick_name='javier', u_password='$2b$12$9q6oTe2dQoV/YdPIfrVAZeFA4P3fZYdHfQzHmZkeatX2dJto/eiRW')
    db.session.add(new_user)
    db.session.add(new_type)
    db.session.add(new_profile)
    db.session.add(new_profile2)
    db.session.add(new_brand)
    db.session.add(new_model)
    db.session.add(new_model2)
    db.session.add(new_model3)
    db.session.add(new_state2)
    db.session.add(new_state3)
    db.session.add(new_state4)
    db.session.commit()

    return jsonify({'datos':'Cargados'})


@app.route('/ps')
def ps():

    name_estado = State.query.filter_by(cod_state='1').first()

    print(name_estado.name_state)

    return jsonify({"mesaje":"si"})

with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=True)