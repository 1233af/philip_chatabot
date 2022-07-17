import requests
from flask import Flask, request, jsonify
import json
import pprint
from notion_add_members import *


application = Flask(__name__)


@application.route("/add_members",methods=['POST'])
def add_members():
    req = request.get_json()
    n = json.loads(req['action']['detailParams']['number_of_members']['value'])['amount']
    
    # notion_add_members(n)
    # async_notion_add_members.delay(n)
    adv_notion_add_members(n)
    
    answer = str(n) + '명의 멤버를 추가합니다.'
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": answer
                    }
                }
            ]
        }
    }
    return jsonify(res)


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True)