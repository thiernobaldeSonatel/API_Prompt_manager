from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import get_db_connection, create_tables

bp = Blueprint('routes', __name__)


@bp.before_app_request
def initialize_database():
    create_tables()


# Registration endpoint
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    password_hash = generate_password_hash(data['password'])

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO users (username, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    ''', (data['username'], data['email'], password_hash, 'user'))
    user_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User registered successfully", "user_id": user_id}), 201


# Login endpoint
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = %s;', (data['email'],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user['password_hash'], data['password']):
        access_token = create_access_token(identity=user['id'])
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


# Create a prompt
@bp.route('/prompts', methods=['POST'])
@jwt_required()
def create_prompt():
    data = request.get_json()
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO prompts (content, user_id)
        VALUES (%s, %s)
        RETURNING id;
    ''', (data['content'], user_id))
    prompt_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Prompt created successfully", "prompt_id": prompt_id}), 201


# Get all prompts
@bp.route('/prompts', methods=['GET'])
def get_prompts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM prompts;')
    prompts = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(prompts), 200


# Get a specific prompt
@bp.route('/prompts/<int:id>', methods=['GET'])
def get_prompt(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM prompts WHERE id = %s;', (id,))
    prompt = cur.fetchone()
    cur.close()
    conn.close()
    if prompt:
        return jsonify(prompt), 200
    else:
        return jsonify({"message": "Prompt not found"}), 404


# Update a prompt
@bp.route('/prompts/<int:id>', methods=['PUT'])
@jwt_required()
def update_prompt(id):
    data = request.get_json()
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM prompts WHERE id = %s;', (id,))
    prompt = cur.fetchone()

    if not prompt:
        cur.close()
        conn.close()
        return jsonify({"message": "Prompt not found"}), 404

    if prompt['status'] in ['Activer', 'Supprimer']:
        cur.close()
        conn.close()
        return jsonify({"message": "Cannot update a validated or deleted prompt"}), 400

    if prompt['user_id'] != user_id:
        cur.close()
        conn.close()
        return jsonify({"message": "Unauthorized"}), 403

    cur.execute('''
        UPDATE prompts
        SET content = %s, status = 'À revoir', updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    ''', (data['content'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Prompt updated successfully"}), 200


# Delete a prompt
@bp.route('/prompts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_prompt(id):
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM prompts WHERE id = %s;', (id,))
    prompt = cur.fetchone()

    if not prompt:
        cur.close()
        conn.close()
        return jsonify({"message": "Prompt not found"}), 404

    cur.execute('SELECT * FROM users WHERE id = %s;', (user_id,))
    user = cur.fetchone()

    if user['role'] != 'admin' and prompt['user_id'] != user_id:
        cur.close()
        conn.close()
        return jsonify({"message": "Unauthorized"}), 403

    cur.execute('''
        UPDATE prompts
        SET status = 'À supprimer', updated_at = CURRENT_TIMESTAMP
        WHERE id = %s;
    ''', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Prompt marked for deletion"}), 200


def init_app(app):
    app.register_blueprint(bp)
