from flask import Flask, jsonify, request, render_template
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, register_user, check_user_credentials, play_game, update_score, get_user_score

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secrets.token_urlsafe(32)'

db.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "Username already exists. Please choose a different username."}), 400

        # If username is not taken, proceed with registration
        register_user(username, password)
        return jsonify({"msg": "User created successfully"}), 201

    except ValueError as e:
        return jsonify({"msg": str(e)}), 400
    
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if check_user_credentials(username, password):
        access_token = create_access_token(identity=username)
        return jsonify({"msg": "Login successful", "access_token": access_token}), 200
    else:
        # Check if the username exists in the database
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({"msg": "Incorrect password"}), 401
        else:
            return jsonify({"msg": "User not found"}), 401
    
@app.route('/play', methods=['POST'])
@jwt_required()
def play():
    player_choice = request.json.get('choice', None)
    result = play_game(player_choice)
    update_score(get_jwt_identity(), result)
    return jsonify(result=result), 200

@app.route('/score', methods=['GET'])
@jwt_required()
def score():
    username = get_jwt_identity()
    score = get_user_score(username)
    return jsonify(score=score)

if __name__=='__main__':
    app.run(debug=True)
