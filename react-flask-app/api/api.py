import time
from flask import Flask, jsonify, request
import requests
app = Flask(__name__)

@app.route('/api/time', methods=['GET'])
def get_current_time():
    return {'time': time.time()}


@app.route('/api/send-message', methods=['POST'])
def send_message():
    data = request.get_json()  # Get the JSON data sent from the frontend
    message = data.get('name', '')  # Extract the message field
    #response_message = f"Server received: {message}"  # Formulate a response
    return jsonify({'responseMessage': f"Hello {message}"})