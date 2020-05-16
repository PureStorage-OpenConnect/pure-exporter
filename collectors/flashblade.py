import urllib3
import six
from purity_fb import PurityFb

# import third party modules
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FlashbladeCollector():
    """
    Instantiates the collector's methods and properties to retrieve status,
    space occupancy and performance metrics from Puretorage FlasBlade.
    Provides also a 'collect' method to allow Prometheus client registry
    to work properly.
    :param target: IP address or domain name of the target array's management
                   interface.
    :type target: str
    :param api_token: API token of the user with which to log in.
    :type api_token: str
    """
    def __init__(self, target, api_token, request = 'all'):
        # self.fb = PurityFb(endpoint, conn_timeo=ctimeo, read_timeo=rtimeo, retries=retries)
        self.fb = PurityFb(host=target, api_token=api_token)
        self.fb.disable_verify_ssl()
        self.fb._api_client.user_agent = 'Purity_FB_Prometheus_exporter/1.0'
        self.request = request

    def __del__(self):
        if self.fb:
            self.fb.logout()

    def array_info(self):
        """Assemble a simple information metric defining the scraped system."""
        data = self.fb.arrays.list_arrays().items[0]

        yield InfoMetricFamily(
            'purefb',
            'FlashBlade system information',
            value={
                'array_name': data.name,
                'system_id': data.id,
                'os': data.os,
                'version': data.version
            })

    def array_hw(self):
        """
        Create a metric of gauge type for components status,
        with the hardware component name as label.
        Metrics values can be iterated over.
        """

        fb_hw = self.fb.hardware.list_hardware().items
        labels = ['hw_id']
        status = GaugeMetricFamily('purefb_hw_status',
                                   'Hardware components status',
                                   labels=labels)
        for h in fb_hw:
            state = h.status
            name = h.name
            labels_v = [name]
            if state == 'unused' or state == 'not_installed':
                continue
            elif state == 'healthy':
                status.add_metric(labels_v, 1)
            else:
                status.add_metric(labels_v, 0)
        yield status


    def array_events(self):
        """
        Create a metric of gauge type for the number of open alerts:
        critical, warning and info, with the severity as label.
        Metrics values can be iterated over.
        """
        fb_events = self.fb.alerts.list_alerts(filter="state='open'").items
        labels = ['severity']
        events = GaugeMetricFamily('purefb_open_events_total',
                                   'FlashBlade number of open events',
                                   labels=labels)

        # Inrement each counter for each type of event
        c_crit, c_warn, c_info = 0, 0, 0
        for msg in fb_events:
            if msg.severity == 'critical':
                c_crit += 1
            if msg.severity == 'warning':
                c_warn += 1
            if msg.severity == 'info':
                c_info += 1
        events.add_metric(['critical'], c_crit)
        events.add_metric(['warning'], c_warn)
        events.add_metric(['info'], c_info)
        yield events


    def array_space(self):
        """
        Create metrics of gauge type for array space indicators.
        Metrics values can be iterated over.
        """
        fb_space = self.fb.arrays.list_arrays_space().items[0]
        capacity_tot = GaugeMetricFamily('purefb_space_tot_capacity_bytes',
                                         'FlashBlade total space capacity',
                                         labels=[])
        data_reduction = GaugeMetricFamily('purefb_space_data_reduction',
                                           'FlashBlade overall data reduction',
                                           labels=[])
        tot_physical = GaugeMetricFamily('purefb_space_tot_physical_bytes',
                                         'FlashBlade overall occupied space',
                                         labels=[])
        tot_snapshots = GaugeMetricFamily('purefb_space_tot_snapshot_bytes',
                                          'FlashBlade occupied space for snapshots',
                                          labels=[])
        capacity_tot.add_metric([], fb_space.capacity)
        data_reduction.add_metric([], fb_space.space.data_reduction)
        tot_physical.add_metric([], fb_space.space.total_physical)
        tot_snapshots.add_metric([], fb_space.space.snapshots)
        yield capacity_tot
        yield data_reduction
        yield tot_physical
        yield tot_snapshots


    def buckets_space(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        Metrics values can be iterated over.
        """
        fb_buckets = self.fb.buckets.list_buckets()
        labels = ['account', 'name']
        data_reduct = GaugeMetricFamily('purefb_buckets_data_reduction',
                                        'FlashBlade buckets data reduction',
                                        labels=labels)
        obj_cnt = GaugeMetricFamily('purefb_buckets_object_count',
                                    'FlashBlade buckets objects counter',
                                    labels=labels)
        space_snap = GaugeMetricFamily('purefb_buckets_snapshots_bytes',
                                       'FlashBlade buckets occupied snapshots space',
                                       labels=labels)
        tot_phy = GaugeMetricFamily('purefb_buckets_total_bytes',
                                    'FlashBlade buckets total physical space',
                                    labels=labels)
        virt_space = GaugeMetricFamily('purefb_buckets_virtual_bytes',
                                       'FlashBlade buckets virtual space',
                                       labels=labels)
        uniq_space = GaugeMetricFamily('purefb_buckets_unique_bytes',
                                       'FlashBlade buckets unique space',
                                       labels=labels)
        for b in fb_buckets.items:
            if b.space.data_reduction is None:
                b.space.data_reduction = 0
            data_reduct.add_metric([b.account.name, b.name],
                                   b.space.data_reduction)
            obj_cnt.add_metric([b.account.name, b.name], b.object_count)
            space_snap.add_metric([b.account.name, b.name], b.space.snapshots)
            tot_phy.add_metric([b.account.name, b.name],
                               b.space.total_physical)
            virt_space.add_metric([b.account.name, b.name], b.space.virtual)
            uniq_space.add_metric([b.account.name, b.name], b.space.unique)
        yield data_reduct
        yield obj_cnt
        yield space_snap
        yield tot_phy
        yield virt_space
        yield uniq_space

    def filesystems_space(self):
        """
        Create metrics of gauge type for filesystems space indicators,
        with filesystem name as label.
        Metrics values can be iterated over.
        """
        fb_filesystems = self.fb.file_systems.list_file_systems()
        labels = ['name']
        data_reduct = GaugeMetricFamily('purefb_filesystems_data_reduction',
                                        'FlashBlade filesystems data reduction',
                                        labels=labels)
        space_snap = GaugeMetricFamily('purefb_filesystems_snapshots_bytes',
                                       'FlashBlade filesystems occupied snapshots space',
                                       labels=labels)
        tot_phy = GaugeMetricFamily('purefb_filesystems_total_bytes',
                                    'FlashBlade filesystems total physical space',
                                    labels=labels)
        virt_space = GaugeMetricFamily('purefb_filesystems_virtual_bytes',
                                       'FlashBlade filesystems virtual space',
                                       labels=labels)
        uniq_space = GaugeMetricFamily('purefb_filesystems_unique_bytes',
                                       'FlashBlade filesystems unique space',
                                       labels=labels)
        for f in fb_filesystems.items:
            if f.space.data_reduction is None:
                f.space.data_reduction = 0
            data_reduct.add_metric([f.name], f.space.data_reduction)
            space_snap.add_metric([f.name], f.space.snapshots)
            tot_phy.add_metric([f.name], f.space.total_physical)
            virt_space.add_metric([f.name], f.space.virtual)
            uniq_space.add_metric([f.name], f.space.unique)
        yield data_reduct
        yield space_snap
        yield tot_phy
        yield virt_space
        yield uniq_space

    def array_perf(self):
        """
        Create array performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        protocols = ['all', 'http', 'nfs', 's3', 'smb']

        for proto in protocols:
            if proto == 'all':
                fb_perf = self.fb.arrays.list_arrays_performance().items[0]
            else:
                fb_perf = self.fb.arrays.list_arrays_performance(protocol=proto).items[0]

            labels = ['protocol', 'dimension']
            bpops = GaugeMetricFamily('purefb_array_performance_opns_bytes',
                                      'FlashBlade array average bytes per operations',
                                      labels=labels)
            latency = GaugeMetricFamily('purefb_array_performance_latency_usec',
                                        'FlashBlade array latency',
                                        labels=labels)
            iops = GaugeMetricFamily('purefb_array_performance_iops',
                                     'FlashBlade array IOPS',
                                     labels=labels)
            throughput = GaugeMetricFamily('purefb_array_performance_throughput_bytes',
                                          'FlashBlade array throughput',
                                          labels=labels)
            bpops.add_metric([proto, 'opn'], fb_perf.bytes_per_op)
            bpops.add_metric([proto, 'rd'], fb_perf.bytes_per_read)
            bpops.add_metric([proto, 'wr'], fb_perf.bytes_per_write)
            latency.add_metric([proto, 'rd'], fb_perf.usec_per_read_op)
            latency.add_metric([proto, 'wr'], fb_perf.usec_per_write_op)
            latency.add_metric([proto, 'other'], fb_perf.usec_per_other_op)
            iops.add_metric([proto, 'rd'], fb_perf.reads_per_sec)
            iops.add_metric([proto, 'wr'], fb_perf.writes_per_sec)
            iops.add_metric([proto, 'other'], fb_perf.others_per_sec)
            #iops.add_metric([proto, 'in'], fb_perf.input_per_sec)
            #iops.add_metric([proto, 'out'], fb_perf.output_per_sec)
            throughput.add_metric([proto, 'rd'], fb_perf.read_bytes_per_sec)
            throughput.add_metric([proto, 'wr'], fb_perf.write_bytes_per_sec)
        yield bpops
        yield latency
        yield iops
        yield throughput


    def array_clientperf(self):
        """
        Create metrics of gauge type for client performance metrics.
        Metrics values can be iterated over.
        """
        fb_clientperf = self.fb.arrays.list_clients_performance()
        labels = ['name', 'dimension']
        bpops = GaugeMetricFamily('purefb_client_performance_opns_bytes',
                                  'FlashBlade client average bytes per operations',
                                  labels=labels)
        latency = GaugeMetricFamily('purefb_client_performance_latency_usec',
                                    'FlashBlade latency',
                                    labels=labels)
        iops = GaugeMetricFamily('purefb_client_performance_iops',
                                 'FlashBlade IOPS',
                                 labels=labels)
        throughput = GaugeMetricFamily('purefb_client_performance_throughput_bytes',
                                       'FlashBlade client_throughput',
                                       labels=labels)

        for cperf in fb_clientperf.items:
            bpops.add_metric([cperf.name, 'opn'], cperf.bytes_per_op)
            bpops.add_metric([cperf.name, 'rd'], cperf.bytes_per_read)
            bpops.add_metric([cperf.name, 'wr'], cperf.bytes_per_write)
            iops.add_metric([cperf.name, 'rd'], cperf.reads_per_sec)
            iops.add_metric([cperf.name, 'wr'], cperf.writes_per_sec)
            iops.add_metric([cperf.name, 'other'], cperf.others_per_sec)
            latency.add_metric([cperf.name, 'rd'], cperf.usec_per_read_op)
            latency.add_metric([cperf.name, 'wr'], cperf.usec_per_write_op)
            latency.add_metric([cperf.name, 'other'], cperf.usec_per_other_op)
            throughput.add_metric([cperf.name, 'rd'], cperf.read_bytes_per_sec)
            throughput.add_metric([cperf.name, 'wr'], cperf.write_bytes_per_sec)

        yield bpops
        yield latency
        yield iops
        yield throughput

    def collect(self):
        """Global collector method for all the collected array metrics."""
        if (self.request == 'all' or self.request == 'array'):
            yield from self.array_info()
            yield from self.array_hw()
            yield from self.array_events()
            yield from self.array_perf()
            yield from self.array_space()
            yield from self.filesystems_space()
            yield from self.buckets_space()
        if (self.request == 'all' or self.request == 'clients'):
            yield from self.array_clientperf()
