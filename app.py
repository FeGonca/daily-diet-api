from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.user import User, Meal
from flask import Flask, request, jsonify
from database import db
import datetime
import bcrypt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'desafio'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/daily-diet-api'

login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Index
@app.route('/', methods=['GET'])
def index():
    return '<h1>Hello World</h1>'

# Create User
@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Verificando se o usuário já existe
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Usuário já cadastrado'}), 400
    
    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'Usuário cadastrado com sucesso'})
    
    return jsonify({'message': 'Dados Inválidos'}), 400

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
        login_user(user)

        return jsonify({'message': 'Login realizado com sucesso!'})
    
    return jsonify({'message': 'Usuário ou senha inválidos'})

# Logout
@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Lougout realizado com sucesso!'})

# Create Meal
@app.route('/meal', methods=['POST'])
@login_required
def create_meal():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    diet_flag = data.get('diet_flag')
    date_created = data.get('date_created')

    if name and description and date_created and (diet_flag is not None):
        meal = Meal(
            name=name,
            description=description,
            diet_flag=diet_flag,
            date_created=date_created,
            user_id=current_user.id,
            updated_at=date_created
        )
        db.session.add(meal)
        db.session.commit()

        return jsonify({'message': 'Refeição criada com sucesso!'})
    
    return jsonify({'message': 'Dados Inválidos'}), 400

# Read Meal
@app.route('/meal', methods=['GET'])
@login_required
def read_meal():
    meal = Meal.query.filter_by(user_id = current_user.id)

    if meal.count() > 0:
        return jsonify({'meals': [{
            'id': m.id,
            'name': m.name,
            'description': m.description,
            'diet_flag': m.diet_flag,
            'date_created': m.date_created
        } for m in meal]})
    
    return jsonify({'message': 'Usuário não possui refeições cadastradas'}), 404

@app.route('/meal/<int:id>', methods=['GET'])
@login_required
def show_meal(id):
    meal = Meal.query.filter_by(user_id = current_user.id, id=id)

    if meal.count() > 0:
        return jsonify({'meal': [{
            'id': m.id,
            'name': m.name,
            'description': m.description,
            'diet_flag': m.diet_flag,
            'date_created': m.date_created
        } for m in meal]})
    
    return jsonify({'message': 'Refeição não encontrada'}), 404


# Update Meal
@app.route('/meal/<int:id_meal>', methods=['PUT'])
@login_required
def update_meal(id_meal):
    data = request.json
    meal = Meal.query.get(id_meal)

    print(f'Teste: {meal.user_id}')

    if meal.user_id != current_user.id:
        return jsonify({'message': 'Operação não permitida'})
    
    if meal:
        meal.name = data.get('name')
        meal.description = data.get('description')
        meal.diet_flag = data.get('diet_flag')
        meal.updated_at = datetime.datetime.now()

        db.session.commit()

        return jsonify({'message': f'A refeição {id_meal} atualizada com sucesso'})

    return jsonify({'message': 'Refeição não encontrado'}), 404

# Delete Meal
@app.route('/meal/<int:id_meal>', methods=['DELETE'])
@login_required
def delete(id_meal):
    # data = request.json
    meal = Meal.query.get(id_meal)

    if meal.user_id != current_user.id:
        return jsonify({'message': 'Operação não permitida'})
    
    if meal:
        db.session.delete(meal)
        db.session.commit()

        return jsonify({'message': f'Refeição {id_meal} deletada com sucesso'})
    
    return jsonify({'message': 'Refeição não encontrada'})



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)