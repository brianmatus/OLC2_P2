import main
from flask import Flask, Response, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from xml.dom import minidom
import base64
import re
import json
import global_config

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
    from elements.c_env import Environment
    global_config.main_environment = Environment(None)

    global_config.lexic_error_list = []
    global_config.syntactic_error_list = []
    global_config.semantic_error_list = []
    global_config.tmp_symbol_table = []
    global_config.function_list = {}
    # func list
    global_config.console_output = ""
    global_config.function_3ac_code = []

    r = main.parse_code(a)
    if "optimization" not in r.keys():
        print("OPT TABLE NOT POPULATED")
        r["optimization"] = ["a<->b<->c<->d"]

    return jsonify({"result": r})
    # return "a"

app.run()