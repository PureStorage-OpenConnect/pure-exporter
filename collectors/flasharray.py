import urllib3
import purestorage

# import third party modules
from prometheus_client.core import GaugeMetricFamily

# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FlasharrayCollector:
    """ Instantiates the collector's methods and properties to retrieve metrics
    from Puretorage Flasharray.
    Provides also a 'collect' method to allow Prometheus client registry
    to work

    :param target: IP address or domain name of the target array's management
                   interface.
    :type target: str
    :param api_token: API token of the user with which to log in.
    :type api_token: str
    """
    def __init__(self, target, api_token):
        self.fa = purestorage.FlashArray(target, api_token=api_token)
        conn = self.fa.list_array_connections()
        self.active_cluster = False
        for c in conn:
            if c['type'] == 'sync-replication':
                self.active_cluster = True
                break

    def array_hw(self):
        """ Create metrics of gauge type for temperature, power and components
        status, with hardware component name as label.
        Metrics values can be iterated over.
        """

        def _get_desc(cid):
            """ Utility function to create human readable labels for
            hardware components
            """
            desc = ''
            hw_comp = cid['name'].split('.')
            for hw in hw_comp:
                if (hw.find('CH', 0, 2) >= 0):
                    c = hw.split('CH')
                    desc = desc + f' Chassis {c[1]}'
                elif (hw.find('BAY', 0, 3) >= 0):
                    m = hw.split('BAY')
                    desc = desc + f' Flash module {m[1]}'
                elif (hw.find('SH', 0, 2) >= 0):
                    m = hw.split('SH')
                    desc = desc + f'Shelf {m[1]}'
                elif (hw.find('NVB', 0, 3) >= 0):
                    m = hw.split('NVB')
                    desc = desc + f' NVRAM module {m[1]}'
                elif (hw.find('TMP', 0, 3) >= 0):
                    m = hw.split('TMP')
                    desc = desc + f' Temperature sensor {m[1]}'
                elif (hw.find('FAN', 0, 3) >= 0):
                    m = hw.split('FAN')
                    desc = desc + f' Fan {m[1]}'
                elif (hw.find('PWR', 0, 3) >= 0):
                    m = hw.split('PWR')
                    desc = desc + f' Power Supply {m[1]}'
                elif (hw.find('CT', 0, 2) >= 0):
                    c = hw.split('CT')
                    desc = desc + f' Controller {c[1]}'
                elif (hw.find('FC', 0, 2) >= 0):
                    m = hw.split('FC')
                    desc = desc + f' Fibre Channel port {m[1]}'
                elif (hw.find('ETH', 0, 3) >= 0):
                    m = hw.split('ETH')
                    desc = desc + f' Ethernet Port {m[1]}'
                elif (hw.find('SAS', 0, 3) >= 0):
                    m = hw.split('SAS')
                    desc = desc + f' SAS Port {m[1]}'
                elif (hw.find('TMP', 0, 3) >= 0):
                    m = hw.split('TMP')
                    desc = desc + f' Temperature sensor {m[1]}'
                elif (hw.find('FAN', 0, 3) >= 0):
                    m = hw.split('FAN')
                    desc = desc + f' Fan {m[1]}'

            return desc.strip()

        fa_hw = self.fa.list_hardware()
        labels = ['hw_id', 'hw_desc']
        temp = GaugeMetricFamily('pure_fa_temp_celsius',
                                 'Hardware components temperature',
                                 labels=labels)
        power = GaugeMetricFamily('pure_fa_power_watts',
                                  'Hardware components Power consumption',
                                  labels=labels)
        status = GaugeMetricFamily('pure_fa_hw_status',
                                   'Hardware components status',
                                   labels=labels)
        for h in fa_hw:
            state = h['status']
            name = h['name']
            labels_v = [name, _get_desc(h)]
            if 'TMP' in name and h['temperature']:
                temp.add_metric(labels_v, h['temperature'])
            if 'PWR' in h['name'] and h['voltage']:
                power.add_metric(labels_v, h['voltage'])
            if state == 'ok' or state == 'not_installed':
                status.add_metric(labels_v, 1)
            else:
                status.add_metric(labels_v, 0)
        yield temp
        yield power
        yield status

    def array_events(self):
        """ Create a metric of gauge type for the number of open alerts:
        critical, warning and info, with the severity as label.
        Metrics values can be iterated over.
        """
        fa_events = self.fa.list_messages(open=True)
        labels = ['severity']
        events = GaugeMetricFamily('pure_fa_open_events_total',
                                   'Number of open events',
                                   labels=labels)
        ccounter = 0
        wcounter = 0
        icounter = 0
        for msg in fa_events:
            severity = msg['current_severity']
            if severity == 'critical':
                ccounter += 1
            if severity == 'warning':
                wcounter += 1
            if severity == 'info':
                icounter += 1
        events.add_metric(['critical'], ccounter)
        events.add_metric(['warning'], wcounter)
        events.add_metric(['info'], icounter)
        yield events

    def array_space(self):
        """ Create array space metrics of gauge type.
        Metrics values can be iterated over.
        """
        fa_space = self.fa.get(space=True)
        array_capacity = GaugeMetricFamily('pure_fa_space_capacity_bytes',
                                           'FlashArray overall space capacity',
                                           labels=[])
        array_reduction = GaugeMetricFamily('pure_fa_space_data_reduction',
                                            'FlashArray overall data reduction',
                                            labels=[])
        array_provisioned = GaugeMetricFamily('pure_fa_space_provisioned_bytes',
                                              'FlashArray overall provisioned space',
                                              labels=[])
        array_shared = GaugeMetricFamily('pure_fa_space_shared_bytes',
                                         'FlashArray overall shared space',
                                         labels=[])
        array_system = GaugeMetricFamily('pure_fa_space_system_bytes',
                                         'FlashArray overall system space',
                                         labels=[])
        array_volumes = GaugeMetricFamily('pure_fa_space_volumes_bytes',
                                          'FlashArray overall volumes space',
                                          labels=[])
        array_capacity.add_metric([], fa_space[0]['capacity'])
        array_reduction.add_metric([], fa_space[0]['data_reduction'])
        array_provisioned.add_metric([], fa_space[0]['provisioned'])
        array_shared.add_metric([], fa_space[0]['shared_space'])
        array_system.add_metric([], fa_space[0]['system'])
        array_volumes.add_metric([], fa_space[0]['volumes'])
        yield array_capacity
        yield array_reduction
        yield array_provisioned
        yield array_shared
        yield array_system
        yield array_volumes

    def array_perf(self):
        """ Create array performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        fa_perf = self.fa.get(action='monitor', mirrored='True')
        array_rd_lat = GaugeMetricFamily('pure_fa_perf_rd_latency_usec',
                                         'FlashArray read latency',
                                         labels=[])
        array_wr_lat = GaugeMetricFamily('pure_fa_perf_wr_latency_usec',
                                         'FlashArray write latency',
                                         labels=[])
        array_queue = GaugeMetricFamily('pure_fa_perf_qlen_usec',
                                        'FlashArray queue time',
                                        labels=[])
        array_rd_iops = GaugeMetricFamily('pure_fa_perf_rd_ops',
                                          'FlashArray read IOPS',
                                          labels=[])
        array_wr_iops = GaugeMetricFamily('pure_fa_perf_wr_ops',
                                          'FlashArray write IOPS',
                                          labels=[])
        array_rd_bw = GaugeMetricFamily('pure_fa_perf_rd_bps',
                                        'FlashArray read bandwidth',
                                        labels=[])
        array_wr_bw = GaugeMetricFamily('pure_fa_perf_wr_bps',
                                        'FlashArray write bandwidth',
                                        labels=[])
        if self.active_cluster:
            array_mwr_lat = GaugeMetricFamily('pure_fa_perf_mirrored_wr_latency_usec',
                                              'FlashArray mirrored write latency',
                                              labels=[])
            array_mwr_iops = GaugeMetricFamily('pure_fa_perf_mirrored_wr_ops',
                                               'FlashArray mirrored write IOPS',
                                               labels=[])
            array_mwr_bw = GaugeMetricFamily('pure_fa_perf_mirrored_wr_bps',
                                             'FlashArray mirrored write bandwidth',
                                             labels=[])
        array_rd_lat.add_metric([], fa_perf[0]['usec_per_read_op'])
        array_wr_lat.add_metric([], fa_perf[0]['usec_per_write_op'])
        # array_queue.add_metric([], fa_perf[0]['local_queue_usec_per_op'])
        array_rd_iops.add_metric([], fa_perf[0]['reads_per_sec'])
        array_wr_iops.add_metric([], fa_perf[0]['writes_per_sec'])
        array_rd_bw.add_metric([], fa_perf[0]['output_per_sec'])
        array_wr_bw.add_metric([], fa_perf[0]['input_per_sec'])
        if self.active_cluster:
            array_mwr_lat.add_metric([], fa_perf[0]['usec_per_mirrored_write_op'])
            array_mwr_iops.add_metric([], fa_perf[0]['mirrored_writes_per_sec'])
            array_mwr_bw.add_metric([], fa_perf[0]['mirrored_input_per_sec'])
        yield array_rd_lat
        yield array_wr_lat
        yield array_queue
        yield array_rd_iops
        yield array_wr_iops
        yield array_rd_bw
        yield array_wr_bw
        if self.active_cluster:
            yield array_mwr_lat
            yield array_mwr_iops
            yield array_mwr_bw

    def vol_space(self):
        """ Create volumes space metrics of gauge type, with the volume name
        as a label.
        Metrics values can be iterated over.
        """
        v_space = self.fa.list_volumes(space='true')
        labels = ['volume']
        vol_dr = GaugeMetricFamily('pure_fa_vol_data_reduction',
                                   'FlashArray volume data reduction ratio',
                                   labels=labels)
        vol_size = GaugeMetricFamily('pure_fa_vol_size_bytes',
                                     'FlashArray volume size',
                                     labels=labels)
        vol_snap = GaugeMetricFamily('pure_fa_vol_snapshots_bytes',
                                     'FlashArray volume snapshots space',
                                     labels=labels)
        vol_tot = GaugeMetricFamily('pure_fa_vol_total_bytes',
                                    'FlashArray volume total allocated size',
                                    labels=labels)
        vol_vols = GaugeMetricFamily('pure_fa_vol_volumes_space_bytes',
                                     'FlashArray volume volumes space',
                                     labels=labels)
        # Temporarily left out
        #      'system' value always None
        #      'shared_space'  value always None
        #      'thin_provisioning'
        #      'total_reduction'
        for v in v_space:
            vol_dr.add_metric([v['name']], v['data_reduction'])
            vol_size.add_metric([v['name']], v['size'])
            vol_snap.add_metric([v['name']], v['snapshots'])
            vol_tot.add_metric([v['name']], v['total'])
            vol_vols.add_metric([v['name']], v['volumes'])
            yield vol_dr
            yield vol_size
            yield vol_snap
            yield vol_tot
            yield vol_vols

    def vol_perf(self):
        """ Create volumes performance metrics of gauge type, with
        volume name as label.
        Metrics values can be iterated over.
        """
        v_perf = self.fa.list_volumes(action='monitor')
        labels = ['volume']
        vol_rd_lat = GaugeMetricFamily('pure_fa_vol_rd_latency_usec',
                                       'FlashArray volume read latency',
                                       labels=labels)
        vol_wr_lat = GaugeMetricFamily('pure_fa_vol_wr_latency_usec',
                                       'FlashArray volume write latency',
                                       labels=labels)
        vol_rd_bw = GaugeMetricFamily('pure_fa_vol_rd_bw_bps',
                                      'FlashArray volume read bandwidth',
                                      labels=labels)
        vol_wr_bw = GaugeMetricFamily('pure_fa_vol_wr_bw_bps',
                                      'FlashArray volume write bandwidth',
                                      labels=labels)
        vol_rd_iops = GaugeMetricFamily('pure_fa_vol_rd_ops',
                                        'FlashArray volume read IOPS',
                                        labels=labels)
        vol_wr_iops = GaugeMetricFamily('pure_fa_vol_wr_ops',
                                        'FlashArray volume write IOPS',
                                        labels=labels)
        for v in v_perf:
            vol_rd_lat.add_metric([v['name']], v['usec_per_read_op'])
            vol_wr_lat.add_metric([v['name']], v['usec_per_write_op'])
            vol_rd_bw.add_metric([v['name']], v['input_per_sec'])
            vol_wr_bw.add_metric([v['name']], v['output_per_sec'])
            vol_rd_iops.add_metric([v['name']], v['reads_per_sec'])
            vol_wr_iops.add_metric([v['name']], v['writes_per_sec'])
            yield vol_rd_lat
            yield vol_wr_lat
            yield vol_rd_bw
            yield vol_wr_bw
            yield vol_rd_iops
            yield vol_wr_iops

    def collect(self):
        """ Global collector method for all the collected metrics.
        """
        yield from self.array_hw()
        yield from self.array_events()
        yield from self.array_space()
        yield from self.array_perf()
        yield from self.vol_space()
        yield from self.vol_perf()
