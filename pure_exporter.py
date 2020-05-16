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
    """Display an overview of the exporters capabilities."""
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
                <td><a href="/metrics/flashblade/array?endpoint=host&apitoken=0">/metrics/flashblade</a></td>
                <td>endpoint, apitoken</td>
            </tr>
        </tbody>
    </table>
    '''

def route_array(array_type, m_type):
    """Produce FlashArray metrics."""
    collector = None
    if array_type == 'flasharray':
        if not m_type in ['array', 'volumes', 'hosts', 'pods']:
            m_type = 'all'
        collector = FlasharrayCollector
    elif array_type == 'flashblade':
        if not m_type in ['array', 'hosts']:
            m_type = 'all'
        collector = FlashbladeCollector
    else:
        abort(404)

    registry = CollectorRegistry()
    try:
        endpoint = request.args.get('endpoint', None)
        token = request.args.get('apitoken', None)
        registry.register(collector(endpoint, token, m_type))
    except Exception as e:
        app.logger.warn('%s: %s', collector.__name__, str(e))
        abort(500)

    resp = make_response(generate_latest(registry), 200)
    resp.headers['Content-type'] = CONTENT_TYPE_LATEST
    return resp

@app.route('/metrics/flasharray/<m_type>', methods=['GET'])
def route_flasharray(m_type: str):
    return route_array('flasharray', m_type)

@app.route('/metrics/flasharray', methods=['GET'])
def route_flasharray_all():
    return route_flasharray('all')

@app.route('/metrics/flashblade/<m_type>', methods=['GET'])
def route_flashblade(m_type: str):
    return route_array('flashblade', m_type)

@app.route('/metrics/flashblade', methods=['GET'])
def route_flashblade_all():
    return route_flashblade('all')

@app.errorhandler(400)
def route_error_400(error):
    """Handle invalid request errors."""
    return 'Invalid request parameters', 400

@app.errorhandler(404)
def route_error_404(error):
    """ Handle 404 (HTTP Not Found) errors."""
    return 'Not found', 404

@app.errorhandler(500)
def route_error_500(error):
    """Handle server-side errors."""
    return 'Internal server error', 500

# Run in debug mode when not called by WSGI
if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('running in debug mode...')
    app.run(host="0.0.0.0", port=8080, debug=True)
