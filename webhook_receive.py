from flask import Flask
from flask import request
import gzip, io
import json
from time import sleep

from sense_hat import SenseHat


application = Flask(__name__)

def action_triggered:
    sense = SenseHat()
    sense.clear()

    # colours
    b = (50,50,50)  # Black
    w = (255, 255, 255)  # White
    o = (251, 192, 45)  # Orange
    g = (20, 166, 91)  # Green

    cl_matrix  = [
        b, b, b, b, b, b, b, o,
        b, b, b, w, w, b, o, o,
        b, b, b, w, w, o, o, o,
        b, w, w, b, b, o, o, o,
        b, w, w, g, g, o, o, o,
        g, g, g, w, w, g, w, w,
        g, g, g, w, w, g, w, w,
        g, g, g, g, g, g, g, o
    ]

    sense.set_pixels(cl_matrix)
    sleep(1)
    sense.clear()



@application.route('/trigger', methods=['POST'])
def webhook_handler():
    # print(request.is_json)
    print(request.headers)
    # print(request.get_json(force=True))
    #

    # print(type(request.get_data()))
    # compressed_data = io.BytesIO(request.get_data())
    # # # # print(compressed_data.getvalue().hex())
    compressed_data = io.BytesIO(request.data)
    text_data = gzip.GzipFile(fileobj=compressed_data, mode='r')
    json_bytes = text_data.read()
    json_str = json_bytes.decode('utf-8')
    print(json_str)
    # # print(json.loads(text_data.read()))
    #
    action_triggered()
    return "{'ContentType': 'application/json'}"



if __name__ == '__main__':
    sense.clear()
    application.run(host='0.0.0.0', port=8888, debug=True)
