from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/message', methods=['GET'])
def get_message():
    return jsonify({'message': 'not implemented yet'}), 200


if __name__ == '__main__':
    app.run(port=8082, debug=True)
