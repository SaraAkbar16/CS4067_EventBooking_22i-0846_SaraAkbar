from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.notification_db
notifications = db.notifications

@app.route("/send_notification", methods=["POST"])
def send_notification():
    data = request.json
    recipient = data.get("recipient")
    notif_type = data.get("type")  # "email" or "sms"
    message = data.get("message")

    if not recipient or not notif_type or not message:
        return jsonify({"error": "Missing required fields"}), 400

    notification_data = {
        "recipient": recipient,
        "type": notif_type,
        "message": message,
        "status": "pending",
        "timestamp": datetime.utcnow()
    }

    # Insert into MongoDB
    result = notifications.insert_one(notification_data)
    return jsonify({"message": "Notification scheduled", "id": str(result.inserted_id)})

@app.route("/notifications", methods=["GET"])
def get_notifications():
    all_notifications = list(notifications.find({}, {"_id": 0}))  
    return jsonify(all_notifications)

if __name__ == "__main__":
    app.run(debug=True)
