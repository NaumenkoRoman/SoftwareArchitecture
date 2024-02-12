from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)


@app.route('/message', methods=['POST'])
def handle_post():
    msg = request.json.get('msg')
    unique_id = str(uuid.uuid4())
    requests.post('http://localhost:8081/log', json={'id': unique_id, 'msg': msg})
    return jsonify({'id': unique_id, 'message': 'Logged'}), 200


@app.route('/message', methods=['GET'])
def handle_get():
    logging_response = requests.get('http://localhost:8081/log').text
    message_response = requests.get('http://localhost:8082/message').text
    return jsonify({'logging_service': logging_response, 'messages_service': message_response}), 200


if __name__ == '__main__':
    app.run(port=8080, debug=True)
