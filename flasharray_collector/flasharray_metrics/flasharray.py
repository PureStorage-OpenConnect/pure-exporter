import re
import urllib3
import purestorage


# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PURE_NAA = 'naa.624a9370'

base_kpi_params = [{'action': 'monitor'},
                   {'action': 'monitor', 'mirrored': True},
                   {'action': 'monitor', 'latency': True},
                   {'action': 'monitor', 'latency': True, 'mirrored': True},
                   {'action': 'monitor', 'size': True},
                   {'action': 'monitor', 'size': True, 'mirrored': True}]

comm_kpi_params = base_kpi_params + [{'space': True, 'pending': True}]

host_kpi_params = base_kpi_params + [{'space': True}]


class FlashArray:
    """
    Base class for FlashArray Prometheus array info
    """
    def __init__(self, endpoint, api_token):
        self.flasharray = None
        try:
            self.flasharray =  purestorage.FlashArray(
                endpoint,
                api_token=api_token,
                user_agent='Purity_FA_Prometheus_exporter/1.0')
        except purestorage.PureError:
            pass

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

        for params in comm_kpi_params:
            try:
                a = self.flasharray.get(**params)[0]
                self.array.update(a)
            except purestorage.PureError:
                pass
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
        for v in self.flasharray.list_volumes(pending='true'):
            v['naaid'] = PURE_NAA + v['serial']
            vdict[v['name']] = v
        try:
            for v in self.flasharray.list_volumes(protocol_endpoint=True):
                # PE do not have these metrics, so it is necessasy to poulate with fake values
                v['naaid'] = PURE_NAA + v['serial']
                v['size'] = 0
                v['volumes'] = 0
                v['snapshots'] = 0
                v['total'] = 0
                v['data_reduction'] = 0
                vdict[v['name']] = v
        except purestorage.PureError:
            pass

        for params in comm_kpi_params:
            try:
                for v in self.flasharray.list_volumes(**params):
                    vdict[v['name']].update(v)
            except purestorage.PureError:
                pass
        # vdict = {key:val for key, val in vdict.items() if val['time_remaining'] is None}
        self.volumes = list(vdict.values())
        return self.volumes

    def get_hosts(self):    
        if self.hosts is not None:
            return self.hosts
        hdict = {}
        try:
            for h in self.flasharray.list_hosts():
                hdict[h['name']] = h
        except purestorage.PureError:
            pass

        for params in host_kpi_params:
            try:
                for h in self.flasharray.list_hosts(**params):
                    hdict[h['name']].update(h)
            except purestorage.PureError:
                pass
        self.hosts = list(hdict.values())
        return self.hosts

    def get_pods(self):
        if self.pods is not None:
            return self.pods
        pdict = {}
        try:
            for p in self.flasharray.list_pods(pending='true'):
                pdict[p['name']] = p
        except purestorage.PureError:
            pass

        for params in comm_kpi_params:
            try:
                for p in self.flasharray.list_pods(**params):
                    pdict[p['name']].update(p)
            except purestorage.PureError:
                pass
        # pdict = {key:val for key, val in pdict.items() if val['time_remaining'] is None}
        self.pods = list(pdict.values())
        return self.pods
