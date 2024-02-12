from flask import Flask, request, jsonify

app = Flask(__name__)
logs = {}


@app.route('/log', methods=['POST'])
def log_message():
    data = request.json
    logs[data['id']] = data['msg']
    print(f"Logged message: {data['msg']}")
    return jsonify({'status': 'success'}), 200


@app.route('/log', methods=['GET'])
def get_logs():
    return jsonify(list(logs.values())), 200


if __name__ == '__main__':
    app.run(port=8081, debug=True)
