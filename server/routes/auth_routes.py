from flask import Blueprint, request, jsonify
from utils.auth import hash_password, check_password, generate_token, verify_token
import pymongo
import os
from dotenv import load_dotenv

# Define a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')  # Add url_prefix here

# Load MongoDB URI from environment (fall back to hardcoded if not set)
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI") or "mongodb+srv://prateeknarain001_db_user:narain9812461880@cluster0.vewvizi.mongodb.net/"
client = pymongo.MongoClient(MONGO_URI)
db = client["Eloquence"]
users_collection = db["users"]


# ROUTE 1 :create a user using POST : auth/create  , doesnt require auth
@auth_bp.route('/create', methods=['POST'])  # Change to /create
def create_user():
    try:
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']

        # Hash the password
        hashed_password = hash_password(password)

        # Check if user already exists
        if users_collection.find_one({'email': email}):
            return jsonify({"error": "User with this email already exists"}), 400

        # Insert the new user
        result = users_collection.insert_one({'username': username, 'password': hashed_password, 'email': email})

        # Generate JWT token (use email as identity)
        token = generate_token(email)

        # Return token and basic user info so the frontend can store username and userId
        return jsonify({"message": "User created", "token": token, "username": username, "userId": email}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/update', methods=['POST'])
def update_user():
    """Update a user's public profile fields. Expects JSON: { userId: <email>, username: <new name> }"""
    try:
        data = request.get_json() or {}
        user_id = data.get('userId')
        new_username = data.get('username')

        if not user_id or not new_username:
            return jsonify({"error": "userId and username are required"}), 400

        result = users_collection.update_one({'email': user_id}, {'$set': {'username': new_username}})
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User updated", "username": new_username}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# ROUTE 2 :authenticate a user using POST : auth/login   , no login required
@auth_bp.route('/login', methods=['POST']) 
def login_user():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        user = users_collection.find_one({'email': email})
        if not user:
            return jsonify({"error": "User not found"}), 404

        if not check_password(user['password'], password):
            return jsonify({"error": "Invalid password"}), 401

        # Generate JWT token
        token = generate_token(email)

        # Provide username and userId to the client so it can persist them in localStorage
        username = user.get('username') or email
        return jsonify({"message": "Login successful", "token": token, "username": username, "userId": email}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Protected Route Example
# ROUTE 3 : get loggedIn user details using POST : auth/protected , login reuqired
@auth_bp.route('/protected', methods=['POST'])
def protected():
   # get token from the body as its a post method 
    token = request.json.get("token", None)
    


    if not token:
        return jsonify({"error": "Token missing"}), 401

    # Remove 'Bearer ' from the token string if it's present
    token = token.replace("Bearer ", "")
    username = verify_token(token)  # Verify the token

    if not username:
        return jsonify({"error": "Invalid or expired token"}), 401

    return jsonify({"message": f"Hello, {username}! This is a protected route."})
