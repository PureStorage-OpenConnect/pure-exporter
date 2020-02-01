#!/usr/bin/env python

from flask import Flask, request, abort, make_response, jsonify
import urllib3
import purestorage


import logging


app = Flask(__name__)
app.logger.setLevel(logging.INFO)


@app.route('/')
def route_index():
    """Display an overview of the helper capabilities."""
    return '''
    <h1>PureStorage Grafana helper</h1>
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
                <td>volume-hosts</td>
                <td><a href="/flasharray/volume/vol01/host?endpoint=host&apitoken=0">/flasharray/volume/{volume}/host</a></td>
                <td>endpoint</td>
            </tr>
            <tr>
                <td>host-volumes</td>
                <td><a href="/flasharray/host/host01/volume?endpoint=host&apitoken=0">/flasharray/host/{host}/volume</a></td>
host/:host/volume
                <td>endpoint</td>
            </tr>
        </tbody>
    </table>
    '''


@app.route('/flasharray/volume/<volume>/host', methods=['GET'])
def route_volume(volume):
    """Produce a list of information for the volume."""

    try:
        endpoint = request.args.get('endpoint', None)
        token = request.args.get('apitoken', None)
        resp = jsonify(list_volume_connections(endpoint, token, volume))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        app.logger.warn('%s: %s', 'pure_helper', str(e))
        abort(500)
        
@app.route('/flasharray/volume/<vgroup>/<volume>/host', methods=['GET'])
def route_vgvolume(vgroup, volume):
    """Produce a list of information for the volume of the given volume group ."""
    vol = vgroup + '/' + volume
    return(route_volume(vol))

@app.route('/flasharray/host/<host>/volume', methods=['GET'])
def route_host(host):
    """Produce a list of information for the host."""

    try:
        endpoint = request.args.get('endpoint', None)
        token = request.args.get('apitoken', None)
        resp = jsonify(list_host_connections(endpoint, token, host))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp
    except Exception as e:
        app.logger.warn('%s: %s', 'pure_helper', str(e))
        abort(500)

@app.errorhandler(400)
def route_error_400(error):
    """Handle invalid request errors."""
    resp = jsonify(error = 'Invalid request parameters')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp, 400


@app.errorhandler(404)
def route_error_404(error):
    """ Handle 404 (HTTP Not Found) errors."""
    resp = jsonify(error = 'Not found')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp, 404


@app.errorhandler(500)
def route_error_500(error):
    """Handle server-side errors."""
    resp = jsonify(error = 'Internal server error')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp, 500


def list_volume_connections(target, api_token, volume):
    # disable ceritificate warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    conn = purestorage.FlashArray(
            target,
            api_token=api_token,
            user_agent='Purity_FA_Prometheus_exporter/1.0')
    p_hosts = conn.list_volume_private_connections(volume)
    s_hosts = conn.list_volume_shared_connections(volume)
    v_info = conn.get_volume(volume)

    hosts = []
    for h in s_hosts:
        hosts.append({'host': h['host'], 'lun': h['lun'], 'hgroup': h['hgroup']})
    for h in p_hosts:
        hosts.append({'host': h['host'], 'lun': h['lun'], 'hgroup': ''})

    vol = {}
    vol['serial'] = v_info['serial']
    vol['hosts'] = hosts
    return vol

def list_host_connections(target, api_token, host):
    # disable ceritificate warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    conn = purestorage.FlashArray(
            target,
            api_token=api_token,
            user_agent='Purity_FA_Prometheus_exporter/1.0')
    v_list = conn.list_host_connections(host)
    vols = []
    for v in v_list:
        v_info = conn.get_volume(v['vol'])
        if not v_info:
            serial = ''
        else:
            serial = v_info['serial']
        vols.append({'volume': v['vol'], 'lun': v['lun'], 'serial': serial})
    h_info = conn.get_host(host)
    h_info['volumes'] = vols
    return h_info


# Run in debug mode when not called by WSGI
if __name__ == "__main__":
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('running in debug mode...')
    app.run(host="0.0.0.0", port=9000, debug=True)
