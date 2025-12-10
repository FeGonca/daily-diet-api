from flask_login import LoginManager, login_user, logout_user, login_required
from models.user import User
from flask import Flask, request, jsonify
from database import db
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




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)