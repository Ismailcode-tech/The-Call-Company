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
