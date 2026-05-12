from flask import  jsonify



def login_user():
    return jsonify({"message": "Login successful"})

