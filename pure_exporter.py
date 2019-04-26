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


@app.route('/metrics/<c_type>', methods=['GET'])
def route_metrics(c_type: str):
    """
    Produce FlashArray metrics.
    """
    # map collector_type string to a collector class
    registry = CollectorRegistry()
    c_map = {
        'flasharray': FlasharrayCollector,
        'flashblade': FlashbladeCollector
    }
    collector = c_map[c_type] if c_type in c_map else None

    try:
        if collector is FlasharrayCollector:
            # FlashArray
            endpoint = request.args.get('endpoint', None)
            token = request.args.get('apitoken', None)
            registry.register(collector(endpoint, token))
        elif collector is FlashbladeCollector:
            # FlashBlade
            endpoint = request.args.get('endpoint', None)
            token = request.args.get('apitoken', None)
            registry.register(collector(endpoint, token))
        else:
            # collector type not found
            abort(404)
    except Exception as e:
        app.logger.warn('%s: %s', collector.__name__, str(e))
        abort(500)

    resp = make_response(generate_latest(registry), 200)
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
