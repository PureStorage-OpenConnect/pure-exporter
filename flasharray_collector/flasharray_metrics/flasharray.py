import re
import urllib3
import purestorage


# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PURE_NAA = 'naa.624a9370'


class FlashArray:
    """
    Base class for FlashArray Prometheus array info
    """
    def __init__(self, endpoint, api_token):
        self.flasharray =  purestorage.FlashArray(
            endpoint,
            api_token=api_token,
            user_agent='Purity_FA_Prometheus_exporter/1.0')

        self.array = None
        self.hosts = None
        self.volumes = None
        self.pods = None

    def __del__(self):
        if self.flasharray:
            self.flasharray.invalidate_cookie()

    def get_array(self):
        if self.array is not None:
            return self.array
        self.array = self.flasharray.get()
        a = self.flasharray.get(action='monitor')[0]
        self.array.update(a)
        a = self.flasharray.get(action='monitor', mirrored=True)[0]
        self.array.update(a)
        a = self.flasharray.get(action='monitor', latency=True)[0]
        self.array.update(a)
        a = self.flasharray.get(action='monitor', latency=True, mirrored=True)[0]
        self.array.update(a)
        a = self.flasharray.get(action='monitor', size=True)[0]
        self.array.update(a)
        a = self.flasharray.get(action='monitor', size=True, mirrored=True)[0]
        self.array.update(a)
        a = self.flasharray.get(space=True)[0]
        self.array.update(a)
        return self.array

    def get_array_elem(self, elem):
        array = self.get_array()
        if elem not in array:
            return None
        return array[elem]

    def get_open_alerts(self):
        return self.flasharray.list_messages(open=True)

    def get_hardware_status(self):
        return self.flasharray.list_hardware()

    def get_volumes(self):
        if self.volumes is not None:
            return self.volumes
        vdict = {}
        for v in self.flasharray.list_volumes():
            v['naaid'] = PURE_NAA + v['serial']
            vdict[v['name']] = v
        for v in self.flasharray.list_volumes(protocol_endpoint=True):
            # PE do not have these metrics, so it is necessasy to poulate with fake values
            v['naaid'] = PURE_NAA + v['serial']
            v['size'] = 0
            v['volumes'] = 0
            v['snapshots'] = 0
            v['total'] = 0
            v['data_reduction'] = 0
            vdict[v['name']] = v
        for v in self.flasharray.list_volumes(action='monitor'):
            vdict[v['name']].update(v)
        for v in self.flasharray.list_volumes(action='monitor', mirrored='true'):
            vdict[v['name']].update(v)
        for v in self.flasharray.list_volumes(action='monitor', latency='true'):
            vdict[v['name']].update(v)
        for v in self.flasharray.list_volumes(action='monitor', latency='true', mirrored='true'):
            vdict[v['name']].update(v)
        for v in self.flasharray.list_volumes(action='monitor', size='true'):
            vdict[v['name']].update(v)
        for v in self.flasharray.list_volumes(action='monitor', size='true', mirrored='true'):
            vdict[v['name']].update(v)
        for v in self.flasharray.list_volumes(space='true'):
            vdict[v['name']].update(v)
        self.volumes = list(vdict.values())
        return self.volumes

    def get_hosts(self):    
        if self.hosts is not None:
            return self.hosts
        hdict = {}
        for h in self.flasharray.list_hosts():
            hdict[h['name']] = h
        for h in self.flasharray.list_hosts(action='monitor'):
            hdict[h['name']].update(h)
        for h in self.flasharray.list_hosts(action='monitor', mirrored='true'):
            hdict[h['name']].update(h)
        for h in self.flasharray.list_hosts(action='monitor', latency='true'):
            hdict[h['name']].update(h)
        for h in self.flasharray.list_hosts(action='monitor', latency='true', mirrored='true'):
            hdict[h['name']].update(h)
        for h in self.flasharray.list_hosts(action='monitor', size='true'):
            hdict[h['name']].update(h)
        for h in self.flasharray.list_hosts(action='monitor', size='true', mirrored='true'):
            hdict[h['name']].update(h)
        for h in self.flasharray.list_hosts(space='true'):
            hdict[h['name']].update(h)
        self.hosts = list(hdict.values())
        return self.hosts

    def get_pods(self):
        if self.pods is not None:
            return self.pods
        pdict = {}
        for p in self.flasharray.list_pods():
            pdict[p['name']] = p
        for p in self.flasharray.list_pods(action='monitor'):
            pdict[p['name']].update(p)
        for p in self.flasharray.list_pods(action='monitor', mirrored='true'):
            pdict[p['name']].update(p)
        for p in self.flasharray.list_pods(action='monitor', latency='true'):
            pdict[p['name']].update(p)
        for p in self.flasharray.list_pods(action='monitor', latency='true', mirrored='true'):
            pdict[p['name']].update(p)
        for p in self.flasharray.list_pods(action='monitor', size='true'):
            pdict[p['name']].update(p)
        for p in self.flasharray.list_pods(action='monitor', size='true', mirrored='true'):
            pdict[p['name']].update(p)
        for p in self.flasharray.list_pods(space='true'):
            pdict[p['name']].update(p)
        self.pods = list(pdict.values())
        return self.pods
