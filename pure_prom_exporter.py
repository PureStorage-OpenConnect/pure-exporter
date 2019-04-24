#!/usr/bin/env python
# Copyright (c) 2019 Pure Storage, Inc.
#

from flask import Flask, request, abort, make_response
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST  
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
from pure_fa_collector import PurestorageFACollector
from pure_fb_collector import PurestorageFBCollector

import logging


app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.route('/metrics/flasharray', methods=['GET'])
def get_fa_metrics():

    endp = request.args.get('endpoint','')
    atok = request.args.get('api-token','')
    if ( endp == '' or atok == ''):
        abort(404)

    _reg = CollectorRegistry()
    try:
        _reg.register(PurestorageFACollector(endp, atok))
    except Exception as e:
        app.logger.info('PurestorageFACollector: %s', str(e))
        abort(404)
    resp = make_response(generate_latest(_reg), 200)
    resp.headers['Content-type'] = CONTENT_TYPE_LATEST
    return resp

@app.route('/metrics/flashblade', methods=['GET'])
def get_fb_metrics():

    endp = request.args.get('endpoint','')
    atok = request.args.get('api-token','')
    if ( endp == '' or atok == ''):
        abort(404)

    _reg = CollectorRegistry()
    try:
        _reg.register(PurestorageFBCollector(endp, atok))
    except Exception as e:
        app.logger.info('PurestorageFBCollector: %s', str(e))
        abort(404)
    resp = make_response(generate_latest(_reg), 200)
    resp.headers['Content-type'] = CONTENT_TYPE_LATEST
    return resp

@app.errorhandler(404)
def not_found(error):
    return 'Not found', 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9091)
