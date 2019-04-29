import urllib3
import six
from purity_fb import PurityFb

# import third party modules
from prometheus_client.core import GaugeMetricFamily

# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FlashbladeCollector:
    """ Instantiates the collector's methods and properties to retrieve metrics
    from Puretorage FlasBlade.
    Provides also a 'collect' method to allow Prometheus client registry
    to work

    :param target: IP address or domain name of the target array's management
                   interface.
    :type target: str
    :param api_token: API token of the user with which to log in.
    :type api_token: str
    """

    def __init__(self, target, api_token):
        # self.fb = PurityFb(endpoint, conn_timeo=ctimeo, read_timeo=rtimeo, retries=retries)
        self.fb = PurityFb(host=target, api_token=api_token)
        self.fb.disable_verify_ssl()

    def array_hw(self):
        """ Create a metric of gauge type for components status,
        with the hardware component name as label.
        Metrics values can be iterated over.
        """

        fb_hw = self.fb.hardware.list_hardware().items
        labels = ['hw_id']
        status = GaugeMetricFamily('pure_fb_hw_status',
                                   'Hardware components status',
                                   labels=labels)
        for h in fb_hw:
            state = h.status
            name = h.name
            labels_v = [name]
            if state == 'unused' or state == 'not_installed':
                status.add_metric(labels_v, -1)
            elif state == 'healty':
                status.add_metric(labels_v, 1)
            else:
                status.add_metric(labels_v, 0)
        yield status

    def array_events(self):
        """ Create a metric of gauge type for the number of open alerts:
        critical, warning and info, with the severity as label.
        Metrics values can be iterated over.
        """
        fb_events = self.fb.alerts.list_alerts(filter="state='open'").items
        labels = ['severity']
        events = GaugeMetricFamily('pure_fb_open_events_total',
                                   'FlashBlade number of open events',
                                   labels=labels)
        ccounter = 0
        wcounter = 0
        icounter = 0
        for msg in fb_events:
            severity = msg.severity
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
        """ Create metrics of gauge type for array space indicators.
        Metrics values can be iterated over.
        """
        fb_space = self.fb.arrays.list_arrays_space().items[0]
        capacity_tot = GaugeMetricFamily('pure_fb_space_tot_capacity_bytes',
                                         'FlashBlade total space capacity',
                                         labels=[])
        data_reduction = GaugeMetricFamily('pure_fb_space_data_reduction',
                                           'FlashBlade overall data reduction',
                                           labels=[])
        tot_physical = GaugeMetricFamily('pure_fb_space_tot_physical_bytes',
                                         'FlashBlade overall occupied space',
                                         labels=[])
        tot_snapshots = GaugeMetricFamily('pure_fb_space_tot_snapshot_bytes',
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
        """ Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        Metrics values can be iterated over.
        """
        fb_buckets = self.fb.buckets.list_buckets()
        labels = ['account', 'name']
        data_reduct = GaugeMetricFamily('pure_fb_buckets_data_reduction',
                                        'FlashBlade buckets data reduction',
                                        labels=labels)
        obj_cnt = GaugeMetricFamily('pure_fb_buckets_object_count',
                                    'FlashBlade buckets objects counter',
                                    labels=labels)
        space_snap = GaugeMetricFamily('pure_fb_buckets_snapshots_bytes',
                                       'FlashBlade buckets occupied snapshots space',
                                       labels=labels)
        tot_phy = GaugeMetricFamily('pure_fb_buckets_total_bytes',
                                    'FlashBlade buckets total physical space',
                                    labels=labels)
        virt_space = GaugeMetricFamily('pure_fb_buckets_virtual_bytes',
                                       'FlashBlade buckets virtual space',
                                       labels=labels)
        uniq_space = GaugeMetricFamily('pure_fb_buckets_unique_bytes',
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
        """ Create metrics of gauge type for filesystems space indicators,
        with filesystem name as label.
        Metrics values can be iterated over.
        """
        fb_filesystems = self.fb.file_systems.list_file_systems()
        labels = ['name']
        data_reduct = GaugeMetricFamily('pure_fb_filesystems_data_reduction',
                                        'FlashBlade filesystems data reduction',
                                        labels=labels)
        space_snap = GaugeMetricFamily('pure_fb_filesystems_snapshots_bytes',
                                       'FlashBlade filesystems occupied snapshots space',
                                       labels=labels)
        tot_phy = GaugeMetricFamily('pure_fb_filesystems_total_bytes',
                                    'FlashBlade filesystems total physical space',
                                    labels=labels)
        virt_space = GaugeMetricFamily('pure_fb_filesystems_virtual_bytes',
                                       'FlashBlade filesystems virtual space',
                                       labels=labels)
        uniq_space = GaugeMetricFamily('pure_fb_filesystems_unique_bytes',
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


    def _array_perf(self, proto):
        """ Create array performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        def _fb_perf(fb, proto):
            protocols = ['http', 'nfs', 's3', 'smb']
            if (proto is not None) and isinstance(proto, six.string_types) and \
                (proto in protocols) :
                return fb.arrays.list_arrays_performance(protocol=proto).items[0]
            return fb.arrays.list_arrays_performance().items[0]

        fb_perf = _fb_perf(self.fb, proto)
        if proto is None:
            proto = ''
            l_sep = ''
            d_sep = ''
        else:
            l_sep = '_'
            d_sep = ' '
        _b_op = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}bytes_per_op',
                                  f'FlashBlade {proto}{d_sep}average bytes per operation',
                                  labels=[])
        _b_rd = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}bytes_per_read',
                                  f'FlashBlade {proto}{d_sep}average bytes per read',
                                  labels=[])
        _b_wr = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}bytes_per_write',
                                  f'FlashBlade {proto}{d_sep}average bytes per write',
                                  labels=[])
        _rd_lat = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}rd_latency_usec',
                                    f'FlashBlade {proto}{d_sep}read latency',
                                    labels=[])
        _wr_lat = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}wr_latency_usec',
                                    f'FlashBlade {proto}{d_sep}write latency',
                                    labels=[])
        _others_lat = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}others_latency_usec',
                                        f'FlashBlade {proto}{d_sep}other operations latency',
                                        labels=[])
        _rd_iops = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}rd_ops',
                                     f'FlashBlade {proto}{d_sep}read IOPS',
                                     labels=[])
        _others_iops = GaugeMetricFamily(f'pure_fb_perf{proto}{l_sep}others_ops',
                                     f'FlashBlade {proto}{d_sep}others IOPS',
                                     labels=[])
        _in_iops = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}output_ops',
                                     f'FlashBlade {proto}{d_sep}input IOPS',
                                     labels=[])
        _out_iops = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}output_ops',
                                      f'FlashBlade {proto}{d_sep}output IOPS',
                                      labels=[])
        _wr_iops = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}wr_ops',
                                     f'FlashBlade {proto}{d_sep}write IOPS',
                                     labels=[])
        _rd_bw = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}rd_bps',
                                   f'FlashBlade {proto}{d_sep}read bandwidth',
                                   labels=[])
        _wr_bw = GaugeMetricFamily(f'pure_fb_perf_{proto}{l_sep}wr_bps',
                                   f'FlashArray {proto}{d_sep}write bandwidth',
                                   labels=[])
        _b_op.add_metric([], fb_perf.bytes_per_op)
        _b_rd.add_metric([], fb_perf.bytes_per_read)
        _b_wr.add_metric([], fb_perf.bytes_per_read)
        _rd_lat.add_metric([], fb_perf.usec_per_read_op)
        _wr_lat.add_metric([], fb_perf.usec_per_write_op)
        _others_lat.add_metric([], fb_perf.usec_per_other_op)
        _rd_iops.add_metric([], fb_perf.reads_per_sec)
        _others_iops.add_metric([], fb_perf.others_per_sec)
        _in_iops.add_metric([], fb_perf.input_per_sec)
        _out_iops.add_metric([], fb_perf.output_per_sec)
        _wr_iops.add_metric([], fb_perf.writes_per_sec)
        _rd_bw.add_metric([], fb_perf.read_bytes_per_sec)
        _wr_bw.add_metric([], fb_perf.write_bytes_per_sec)
        metrics = [_b_op, _b_rd, _b_wr, _rd_lat, _wr_lat, _others_lat, _rd_iops, \
                _others_iops, _in_iops, _out_iops, _wr_iops, _rd_bw, _wr_bw]
        for m in metrics:
            yield m

    def array_perf(self):
        yield from self._array_perf(proto=None)

    def array_perf_http(self):
        yield from self._array_perf(proto='http')
        
    def array_perf_nfs(self):
        yield from self._array_perf(proto='nfs')

    def array_perf_smb(self):
        yield from self._array_perf(proto='smb')

    def array_perf_s3(self):
        yield from self._array_perf(proto='s3')

    def collect(self):
        """Global collector method for all the collected metrics."""
        yield from self.array_hw()
        yield from self.array_events()
        yield from self.array_space()
        yield from self.buckets_space()
        yield from self.filesystems_space()
        yield from self.array_perf()
        yield from self.array_perf_http()
        yield from self.array_perf_nfs()
        yield from self.array_perf_smb()
        yield from self.array_perf_s3()
