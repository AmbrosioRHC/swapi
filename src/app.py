import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException
from admin import setup_admin
from models import db, User, Person, Planet, Favorite

# Inicialización de la aplicación Flask
app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de la base de datos SQLite
base_dir = os.path.abspath(os.path.dirname(__file__))
db_file = os.path.join(base_dir, '..', 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)

# Configuración de CORS para permitir todas las rutas desde http://localhost:5173
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Función para agregar datos de ejemplo
def add_example_data():
    # Verificar y crear usuarios solo si no existen
    existing_user = User.query.filter_by(username='johndoe').first()
    if existing_user is None:
        user1 = User(username='johndoe', email='john.doe@example.com')
        db.session.add(user1)

    existing_user = User.query.filter_by(username='janedoe').first()
    if existing_user is None:
        user2 = User(username='janedoe', email='jane.doe@example.com')
        db.session.add(user2)

    # Crear personas
    person1 = Person(name='Luke Skywalker', homeworld='Tatooine')
    person2 = Person(name='Darth Vader', homeworld='Tatooine')
    db.session.add(person1)
    db.session.add(person2)

    # Crear planetas
    planet1 = Planet(name='Tatooine', climate='Arid', population='200000')
    planet2 = Planet(name='Coruscant', climate='Temperate', population='1 billion')
    db.session.add(planet1)
    db.session.add(planet2)

    # Commit para guardar los cambios en la base de datos
    db.session.commit()

# Función para crear la base de datos y añadir datos de ejemplo
def setup_database():
    with app.app_context():
        db.create_all()
        add_example_data()

# Manejo de errores como objetos JSON
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Rutas de la API

@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()
    return jsonify([person.serialize() for person in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Person.query.get(people_id)
    if person is None:
        raise APIException('Person not found', 404)
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', 404)
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    if user_id is None:
        raise APIException('User ID is required', 400)

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        raise APIException('User ID is required', 400)

    favorite = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite planet added successfully"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        raise APIException('User ID is required', 400)

    favorite = Favorite(user_id=user_id, person_id=people_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite person added successfully"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        raise APIException('User ID is required', 400)

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if favorite is None:
        raise APIException('Favorite not found', 404)

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite planet deleted successfully"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        raise APIException('User ID is required', 400)

    favorite = Favorite.query.filter_by(user_id=user_id, person_id=people_id).first()
    if favorite is None:
        raise APIException('Favorite not found', 404)

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite person deleted successfully"}), 200

# Ejecutar la configuración inicial de la base de datos al iniciar la aplicación
if __name__ == '__main__':
    with app.app_context():
        setup_database()

    app.run(host='0.0.0.0', port=3000, debug=True)
