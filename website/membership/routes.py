from . import membership_bp
from flask import request



@membership_bp.route('/activate', methods=['POST'])
def activate_membership():
    data = request.get_json()
    if not data or 'planId' not in data:
        return "Invalid request data", 400
    # Process activation logic here
    return "Membership activated", 200

@membership_bp.route('/cancel', methods=['POST'])
def cancel_membership():
    data = request.get_json()
    if not data or 'membershipId' not in data:
        return "Invalid request data", 400
    # Process cancellation logic here
    return "Membership cancelled", 200


    

@membership_bp.route('/history', methods=['GET'])
def membership_history():
    # Process history retrieval logic here
    return "Membership history", 200


@membership_bp.route('', methods=['POST'])
def getMembership():
    data = request.get_json()
    if not data or 'planId' not in data:
        return "Invalid request data", 400
    # Process membership creation logic here
    return "Membership created", 201
