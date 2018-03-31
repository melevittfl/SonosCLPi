from flask import Flask
from flask import request
import gzip, io
import json
import sense_hat



application = Flask(__name__)


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
    return "{'ContentType': 'application/json'}"


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8888, debug=True)
