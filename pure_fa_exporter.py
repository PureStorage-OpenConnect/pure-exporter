#!/usr/bin/env python

from flask import Flask, request, abort, make_response
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from flasharray_collector import FlasharrayCollector

import logging


app = Flask(__name__)
app.logger.setLevel(logging.INFO)


@app.route('/')
def route_index():
    """Display an overview of the exporters capabilities."""
    return '''
    <h1>Pure Storage Prometeus Exporter</h1>
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
                <td>FlashArray hosts</td>
                <td><a href="/metrics/flasharray/hosts?endpoint=host&apitoken=0">/metrics/flasharray</a></td>
                <td>endpoint, apitoken</td>
                <td>Retrieves only host related metrics</td>
            </tr>
            <tr>
                <td>FlashArray volumes</td>
                <td><a href="/metrics/flasharray/volumes?endpoint=host&apitoken=0">/metrics/flasharray</a></td>
                <td>endpoint, apitoken</td>
                <td>Retrieves only volume related metrics</td>
            </tr>
            <tr>
                <td>FlashArray pods</td>
                <td><a href="/metrics/flasharray/pods?endpoint=host&apitoken=0">/metrics/flasharray</a></td>
                <td>endpoint, apitoken</td>
                <td>Retrieves only pod related metrics</td>
            </tr>
        </tbody>
    </table>
    '''

@app.route('/metrics/<m_type>', methods=['GET'])
def route_flasharray(m_type: str):
    """Produce FlashArray metrics."""
    if not m_type in ['array', 'volumes', 'hosts', 'pods']:
        m_type = 'all'
    collector = FlasharrayCollector
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


@app.route('/metrics', methods=['GET'])
def route_flasharray_all():
    return route_flasharray('all')

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
