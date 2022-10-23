import main
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from xml.dom import minidom
import base64
import re
import json

app = Flask(__name__)

app.config["DEBUG"] = True
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type, Access-Control-Allow-Origin'


@app.route("/parse_code", methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'])
def hello():

    if request.method != "POST":
        return jsonify({
            'status': 405,
            'message': f'Este metodo no esta permitido para este endpoint'
        })

    print("here")
    print(request)
    a = request.values["code"]
    print(a)

    r = main.parse_code(a)
    if "optimization" not in r.keys():
        print("OPT TABLE NOT POPULATED")
        r["optimization"] = [["a<->b<->c"]]

    return jsonify({"result": r})
    # return "a"

app.run()