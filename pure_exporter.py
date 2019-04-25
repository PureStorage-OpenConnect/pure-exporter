#!/usr/bin/env python

from flask import Flask, request, abort, make_response
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
from collectors import FlasharrayCollector
from collectors import FlashbladeCollector

import logging


app = Flask(__name__)
app.logger.setLevel(logging.INFO)


@app.route('/')
def route_index():
    """
    Display an overview of the exporters capabilities.
    """
    return '''
    <h1>PureStorage Exporter</h1>
    <table>
        <thead>
            <tr>
                <td>Type</td>
                <td>Endpoint</td>
                <td>Required GET parameters</td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>FlashArray</td>
                <td><a href="/metrics/flasharray?endpoint=host&apitoken=0">/metrics/flasharray</a></td>
                <td>endpoint, apitoken</td>
            </tr>
            <tr>
                <td>FlashBlade</td>
                <td><a href="/metrics/flashblade?endpoint=host&apitoken=0">/metrics/flashblade</a></td>
                <td>endpoint, apitoken</td>
            </tr>
        </tbody>
    </table>
    '''


@app.route('/metrics/flasharray', methods=['GET'])
@app.route('/metrics/flashblade', methods=['GET'])
def route_metrics_flasharray():
    """
    Produce FlashArray metrics.
    """
    endp = request.args.get('endpoint', None)
    atok = request.args.get('apitoken', None)
    path = request.path

    if (path == '/metrics/flasharray'):
        collector = 'FlasharrayCollector'
    elif (path == '/metrics/flashblade'):
        collector = 'FlashbladeCollector'
    else:
        abort(400)

    if (endp is None or atok is None):
        abort(400)

    _reg = CollectorRegistry()
    try:
        if (collector == 'FlasharrayCollector'):
            _reg.register(FlasharrayCollector(endp, atok))
        else:
            _reg.register(FlashbladeCollector(endp, atok))

    except Exception as e:
        app.logger.warn('%s: %s', collector, str(e))
        abort(500)

    resp = make_response(generate_latest(_reg), 200)
    resp.headers['Content-type'] = CONTENT_TYPE_LATEST
    return resp


@app.errorhandler(400)
def route_error_400(error):
    """
    Handle invalid request errors
    """
    return 'Invalid request parameters', 400


@app.errorhandler(404)
def route_error_404(error):
    """
    Handle 404 (HTTP Not Found) errors
    """
    return 'Not found', 404


@app.errorhandler(500)
def route_error_500(error):
    """
    Handle server-side errors
    """
    return 'Internal server error', 500


# Run in debug mode when not called by WSGI
if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('running in debug mode...')
    app.run(host="0.0.0.0", port=8080, debug=True)
