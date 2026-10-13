#!/usr/bin/env python3

from flask import Flask, request, Response
import jsonpickle
from PIL import Image
import io
import argparse
import base64
import binascii

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)


@app.route('/api/add/<int:a>/<int:b>', methods=['GET', 'POST'])
def add(a, b):
    response = {'sum': str(a + b)}
    return Response(response=jsonpickle.encode(response), status=200,
                    mimetype='application/json')


@app.route('/api/rawimage', methods=['POST'])
def rawimage():
    try:
        img = Image.open(io.BytesIO(request.data))
        response = {'width': img.size[0], 'height': img.size[1]}
    except Exception:
        response = {'width': 0, 'height': 0}
    return Response(response=jsonpickle.encode(response), status=200,
                    mimetype='application/json')


@app.route('/api/dotproduct', methods=['POST'])
def dotproduct():
    data = request.get_json()
    a = data['a']
    b = data['b']
    if len(a) != len(b):
        return {'error': 'Vectors must have the same length'}, 400
    result = sum(x * y for x, y in zip(a, b))
    response = {'dotproduct': result}
    return Response(response=jsonpickle.encode(response), status=200,
                    mimetype='application/json')


@app.route('/api/jsonimage', methods=['POST'])
def jsonimage():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('image'), str):
        return {'error': 'Expected JSON with an image string'}, 400
    try:
        image_bytes = base64.b64decode(data['image'], validate=True)
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
    except (ValueError, binascii.Error, OSError):
        return {'error': 'Invalid base64 image'}, 400
    response = {'width': width, 'height': height}
    return Response(response=jsonpickle.encode(response), status=200,
                    mimetype='application/json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flask REST server')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='Port on which to run the server (default: 5000)')
    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port)
