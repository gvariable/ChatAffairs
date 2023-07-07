from flask import Flask, jsonify, request, make_response, send_file
import requests
from flask_cors import CORS
import argparse
import requests
import json
import logging

app = Flask(__name__)
CORS(app)
logger = app.logger
logger.setLevel(logging.DEBUG)


def get_token():
    token = json.loads(
        requests.post(
            "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=VZjTnhUdpVkC6SBqAWnIYMhZ&client_secret=SGrt56yaDRdIhWYjRXSeHGv3uZMcXWPA"
        ).text
    )["access_token"]
    return token


@app.route("/api/voice", methods=["POST"])
def voice():
    request.json["token"] = get_token()

    baidu_result = json.loads(
        requests.post(url="https://vop.baidu.com/pro_api", json=request.json).text
    )
    print(baidu_result)

    return jsonify(baidu_result), 200


@app.route("/api/text2speech", methods=["GET"])
def text2speech():
    param = request.args.to_dict()
    param["tok"] = get_token()
    baidu_result = requests.post(url="http://tsn.baidu.com/text2audio", params=param)

    audio = make_response(baidu_result.content)
    audio.content_type = baidu_result.headers["Content-Type"]

    return audio


@app.route("/api/text2luospeech", methods=["GET"])
def text2luospeech():
    param = request.args.to_dict()
    param["tok"] = get_token()
    baidu_result = requests.post(url="http://tsn.baidu.com/text2audio", params=param)

    ac_result = requests.post(
        f"http://localhost:11111/api/ac",
        data=baidu_result.content,
        headers=baidu_result.headers,
    )

    audio = make_response(ac_result.content)
    audio.content_type = ac_result.headers["Content-Type"]

    return audio


@app.route("/api/ac", methods=["POST"])
def ac_api():
    response = requests.post(
        "http://127.0.0.1:11111/api/ac", data=request.data, headers=request.headers
    )
    audio = make_response(response.content)
    audio.content_type = response.headers["Content-Type"]

    return audio


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backend server")
    parser.add_argument("--port", "-p", type=int, help="port", default=10001)
    args = parser.parse_args()
    app.config["host"] = "0.0.0.0"
    app.config["port"] = args.port
    app.run(threaded=True, host="0.0.0.0", port=args.port)
