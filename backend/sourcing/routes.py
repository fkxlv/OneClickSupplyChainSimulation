from flask import Flask, request, jsonify
from flask_cors import CORS
#from sourcing. import run_sourcing

app = Flask(__name__)
CORS(app)

@app.route("/source", methods=["POST"])
def source():
    data = request.get_json()
    result = run_sourcing(data)
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(port=5001, debug=True)
