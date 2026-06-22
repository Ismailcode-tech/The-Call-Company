# from . import membership_bp
# from flask import jsonify, request



# @membership_bp.route('/activate', methods=['POST'])
# def activate_membership():
#     data = request.get_json()
#     if not data or 'planId' not in data:
#         return jsonify({"error": "Invalid request data"}), 400
#     # Process activation logic here
#     return jsonify({"message": "Membership activated"}), 200

# @membership_bp.route('/cancel', methods=['POST'])
# def cancel_membership():
#     # Process cancellation logic here
#     return jsonify({"message": "Membership cancelled"}), 200

# @membership_bp.route('/history', methods=['GET'])
# def membership_history():
#     # Process history retrieval logic here
#     # Return an empty list to match HistoryEntry[] in the frontend
#     return jsonify([]), 200

# @membership_bp.route('', methods=['GET'])
# def getMembership():
#     # Process membership retrieval logic here
#     # Return None (which becomes JSON null) to indicate no active membership
#     return jsonify(None), 200













"""
from . import membership_bp
from flask import jsonify, request



@membership_bp.route('/activate', methods=['POST'])
def activate_membership():
    data = request.get_json()
    if not data or 'planId' not in data:
        return jsonify({"error": "Invalid request data"}), 400
    # Process activation logic here
    return jsonify({"message": "Membership activated"}), 200

@membership_bp.route('/cancel', methods=['POST'])
def cancel_membership():
    # Process cancellation logic here
    return jsonify({"message": "Membership cancelled"}), 200

@membership_bp.route('/history', methods=['GET'])
def membership_history():
    # Process history retrieval logic here
    # Return an empty list to match HistoryEntry[] in the frontend
    return jsonify([]), 200

@membership_bp.route('', methods=['GET'])
def getMembership():
    # Process membership retrieval logic here
    # Return None (which becomes JSON null) to indicate no active membership
    return jsonify(None), 200
 
"""

from flask import jsonify, request
from flask_login import login_required,current_user
from . import membership_bp
from .services import activate_membership, get_current_membership,get_membership_history



@membership_bp.route("/activate", methods=["POST"])
@login_required
def activate():

    data = request.get_json()
    if not data:
        return jsonify({
            "error": "Request body required"
        }), 400

    plan_id = data.get("planId")

    if not plan_id:
        return jsonify({
            "error": "planId is required"
        }), 400

    

    success, result = activate_membership(
        member_id=current_user.id,
        plan_id=plan_id
    )

    if not success:
        return jsonify({
            "error": result
        }), 400

    return jsonify(result), 200


@membership_bp.route("/", methods=["GET"])
@login_required
def get_membership():

    member_id = current_user.id

    membership = get_current_membership(member_id)
    print(membership)
    

    return jsonify(membership), 200
    
    # returns null automatically if membership is None





@membership_bp.route("/history", methods=["GET"])
@login_required
def history():

    member_id = current_user.id

    history_data = get_membership_history(member_id)

    return jsonify(history_data), 200