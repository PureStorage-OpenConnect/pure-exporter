#!/usr/bin/env python

from flask import Flask, request, abort, make_response
from flask_httpauth import HTTPTokenAuth
from urllib.parse import parse_qs
import re
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from flasharray_collector import FlasharrayCollector

import logging

class InterceptRequestMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        d = parse_qs(environ['QUERY_STRING'])
        api_token = d.get('apitoken', [''])[0] # Returns the first api-token value
        if 'HTTP_AUTHORIZATION' not in environ:
            environ['HTTP_AUTHORIZATION'] = 'Bearer ' + api_token
        return self.wsgi_app(environ, start_response)

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.wsgi_app = InterceptRequestMiddleware(app.wsgi_app)
auth = HTTPTokenAuth(scheme='Bearer')

@auth.verify_token
def verify_token(token):
    pattern_str = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    regx = re.compile(pattern_str)
    match = regx.search(token)
    return token if match is not None else False


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
                <td>GET parameters</td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Full metrics</td>
                <td><a href="/metrics?endpoint=host&apitoken=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx">/metrics</a></td>
                <td>endpoint, apitoken (optional, required only if authentication tokem is not provided)</td>
            </tr>
            <tr>
                <td>Volume metrics</td>
                <td><a href="/metrics/volumes?endpoint=host&apitoken=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx">/metrics/volumes</a></td>
                <td>endpoint, apitoken (optional, required only if authentication tokem is not provided)</td>
                <td>Retrieves only volume related metrics</td>
            </tr>
            <tr>
                <td>Host metrics</td>
                <td><a href="/metrics/hosts?endpoint=host&apitoken=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx">/metrics/hosts</a></td>
                <td>endpoint, apitoken (optional, required only if authentication tokem is not provided)</td>
                <td>Retrieves only host related metrics</td>
            </tr>
            <tr>
                <td>Pod metrics</td>
                <td><a href="/metrics/pods?endpoint=host&apitoken=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx">/metrics/pods</a></td>
                <td>endpoint, apitoken (optional, required only if authentication tokem is not provided)</td>
                <td>Retrieves only pod related metrics</td>
            </tr>
        </tbody>
    </table>
    '''

@app.route('/metrics/<m_type>', methods=['GET'])
@auth.login_required
def route_flasharray(m_type: str):
    """Produce FlashArray metrics."""
    if not m_type in ['array', 'volumes', 'hosts', 'pods']:
        m_type = 'all'
    collector = FlasharrayCollector
    registry = CollectorRegistry()
    try:
        endpoint = request.args.get('endpoint', None)
        token = auth.current_user()
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
