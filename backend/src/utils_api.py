from flask import Flask, jsonify, request
from flask_cors import CORS
import argparse
import requests
import json

app = Flask(__name__)
CORS(app)

@app.route("/voice_api", methods=["POST"])
def voice_api():
    
    token = json.loads(requests.post("https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=VZjTnhUdpVkC6SBqAWnIYMhZ&client_secret=SGrt56yaDRdIhWYjRXSeHGv3uZMcXWPA").text)['access_token']
    
    request.json["token"] = token
    
    baidu_result = json.loads(requests.post(
                            url="https://vop.baidu.com/pro_api", 
                            json=request.json
                        ).text)

    print(baidu_result)

    return jsonify(baidu_result) ,200
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backend server")
    parser.add_argument("--port", "-p", type=int, help="port", default=10001)
    args = parser.parse_args()
    app.run(threaded=True, host="0.0.0.0", port=args.port)