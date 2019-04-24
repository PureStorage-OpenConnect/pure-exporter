import urllib3
from purity_fb import PurityFb

# import third party modules
from prometheus_client.core import GaugeMetricFamily

# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PurestorageFBCollector:
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
        #self.fb = PurityFb(endpoint, conn_timeo=ctimeo, read_timeo=rtimeo, retries=retries)
        self.fb = PurityFb(host=target, api_token=api_token)
        self.fb.disable_verify_ssl()
        self._name = None

    @property
    def name(self):
        """ Return the FlashBlade name

        :returns: The FlashBlade name.
        :rtype: str

        """
        if self._name is None:
            fbinfo = self.fb.arrays.list_arrays()
            self._name = fbinfo.items[0].name
        return self._name

    def array_hw(self):
        """ Creates metrics for: temperature, power and components status of
        gauge type with array name and the hw component name as labels.
        Metrics values can be iterated over.
        """

        fb_hw = self.fb.hardware.list_hardware().items
        labels=['array','hw_id']
        status = GaugeMetricFamily('pure_fb_hw_status',
                                   'Hardware components status', labels=labels)
        for h in fb_hw:
            state = h.status
            name = h.name
            labels_v = [self.name, name]
            if state == 'unused' or state == 'not_installed':
                status.add_metric(labels_v, -1)
            elif state == 'healty':
                status.add_metric(labels_v, 1)
            else:
                status.add_metric(labels_v, 0)
        yield status

    def array_events(self):
        """
        Create a metric for the number of open alerts: critical, warning and
        info of gauge type, with array name and the severity as labels.
        Metrics values can be iterated over.
        """
        fb_events = self.fb.alerts.list_alerts(filter="state='open'").items
        labels=['array','severity']
        events = GaugeMetricFamily('pure_fb_open_events_total',
                                   'FlashBlade number of open events', labels=labels)
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
        events.add_metric([self.name, 'critical'], ccounter)
        events.add_metric([self.name, 'warning'], wcounter)
        events.add_metric([self.name, 'info'], icounter)
        yield events

    def array_space(self):
        """
        Create array space metrics of type gauge with array name as label.
        Metrics values can be iterated over.
        """
        fb_space = self.fb.arrays.list_arrays_space().items[0]
        labels = ['array']
        capacity_tot = GaugeMetricFamily('pure_fb_space_tot_capacity_bytes',
                                         'FlashBlade total space capacity',
                                         labels=labels)
        data_reduction = GaugeMetricFamily('pure_fb_space_data_reduction',
                                           'FlashBlade overall data reduction',
                                        labels=labels)
        tot_physical = GaugeMetricFamily('pure_fb_space_tot_physical_bytes',
                                        'FlashBlade overall occupied space',
                                        labels=labels)
        tot_snapshots = GaugeMetricFamily('pure_fb_space_tot_snapshot_bytes',
                                          'FlashBlade occupied space for snapshots',
                                          labels=labels)
        capacity_tot.add_metric([self.name], fb_space.capacity)
        data_reduction.add_metric([self.name], fb_space.space.data_reduction)
        tot_physical.add_metric([self.name], fb_space.space.total_physical)
        tot_snapshots.add_metric([self.name], fb_space.space.snapshots)
        yield capacity_tot
        yield data_reduction
        yield tot_physical
        yield tot_snapshots

    def buckets_space(self):
        """
        Create buckets space metrics of type gauge with array name as label.
        Metrics values can be iterated over.
        """
        fb_buckets = self.fb.buckets.list_buckets()
        labels = ['array','account','name']
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
            data_reduct.add_metric([self.name, b.account.name, b.name], b.space.data_reduction)
            obj_cnt.add_metric([self.name, b.account.name, b.name], b.object_count)
            space_snap.add_metric([self.name, b.account.name, b.name], b.space.snapshots)
            tot_phy.add_metric([self.name, b.account.name, b.name], b.space.total_physical)
            virt_space.add_metric([self.name, b.account.name, b.name], b.space.virtual)
            uniq_space.add_metric([self.name, b.account.name, b.name], b.space.unique)
            yield data_reduct
            yield obj_cnt
            yield space_snap
            yield tot_phy
            yield virt_space
            yield uniq_space

    def collect(self):
        """
        Overall collector method for all the collected metrics.
        """
        yield from self.array_hw()
        yield from self.array_events()
        yield from self.array_space()
        yield from self.buckets_space()
