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

array_kpi_params = base_kpi_params + [{'space': True}]
host_kpi_params = array_kpi_params

volume_kpi_params = base_kpi_params + [{'space': True, 'pending': True}]
pod_kpi_params = volume_kpi_params

nic_kpi_params = base_kpi_params + [{'error': True}]


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
        self.vgroups = None
        self.pods = None
        self.host_volumes = None
        self.network_interfaces = None

    def __del__(self):
        if self.flasharray:
            self.flasharray.invalidate_cookie()

    def get_array(self):
        if self.array is not None:
            return self.array
        self.array = self.flasharray.get()

        for params in array_kpi_params:
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
            return list(self.volumes.values())
        vdict = {}
        if self.vgroups is None:
            self.vgroups = self.flasharray.list_vgroups()
        for v in self.flasharray.list_volumes(pending='true'):
            v['naaid'] = PURE_NAA + v['serial']
            v['vgroup'] = ''
            for vg in self.vgroups:
                if v['name'] in vg['volumes']:
                    v['vgroup'] = vg['name']
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
                v['thin_provision'] = 0
                v['vgroup'] = ''
                vdict[v['name']] = v
        except purestorage.PureError:
            pass

        for params in volume_kpi_params:
            try:
                for v in self.flasharray.list_volumes(**params):
                    vdict[v['name']].update(v)
            except purestorage.PureError:
                pass
        # vdict = {key:val for key, val in vdict.items() if val['time_remaining'] is None}
        self.volumes = vdict
        return list(self.volumes.values())

    def get_hosts(self):
        if self.hosts is not None:
            return list(self.hosts.values())
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
        self.hosts = hdict
        return list(self.hosts.values())

    def get_host_volumes(self):
        if self.host_volumes is not None:
            return list(self.host_volumes.values())
        hvdict = {}

        try:
            for h in self.get_hosts():
                for c in self.flasharray.list_host_connections(h['name']):
                    hvdict[h['name']] = {'host': h['name'], 'naaid': self.volumes[c['vol']]['naaid']}
        except purestorage.PureError:
            pass

        self.host_volumes = hvdict
        return list(self.host_volumes.values())

    def get_pods(self):
        if self.pods is not None:
            return list(self.pods.values())
        pdict = {}
        try:
            for p in self.flasharray.list_pods(pending='true'):
                pdict[p['name']] = p
        except purestorage.PureError:
            pass

        for params in pod_kpi_params:
            try:
                for p in self.flasharray.list_pods(**params):
                    pdict[p['name']].update(p)
            except purestorage.PureError:
                pass
        # pdict = {key:val for key, val in pdict.items() if val['time_remaining'] is None}
        self.pods = pdict
        return list(self.pods.values())

    def get_network_interfaces(self):
        if self.network_interfaces is not None:
            return list(self.network_interfaces.values())
        nicdict = {}
        try:
            for n in self.flasharray.list_network_interfaces():
                nicdict[n['name']] = n
        except purestorage.PureError:
            pass

        for params in nic_kpi_params:
            try:
                for n in self.flasharray.list_network_interfaces(**params):
                    nicdict[n['name']].update(n)
            except purestorage.PureError:
                pass
        self.network_interfaces = nicdict
        return list(self.network_interfaces.values())