from prometheus_client.core import GaugeMetricFamily


class BucketsSpaceMetrics():
    """
    Base class for FlashBlade Prometheus buckets space metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.datareduction = None
        self.objcount = None
        self.space = None

    def _data_reduction(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        """
        self.data_reduction = GaugeMetricFamily(
                                          'purefb_buckets_data_reduction',
                                          'FlashBlade buckets data reduction',
                                          labels=['account', 'name'])
        for b in self.fb.get_buckets():
            if b.space.data_reduction is None:
                b.space.data_reduction = 0
            self.data_reduction.add_metric([b.account.name, b.name],
                                           b.space.data_reduction)

    def _objects(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        """
        self.objects = GaugeMetricFamily('purefb_buckets_object_count',
                                         'FlashBlade buckets objects counter',
                                         labels=['account', 'name'])
        for b in self.fb.get_buckets():
            self.objects.add_metric([b.account.name, b.name], b.object_count)

    def _space(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        """
        self.space = GaugeMetricFamily('purefb_buckets_space_bytes',
                                       'FlashBlade buckets space',
                                       labels=['account', 'name', 'dimension'])
        for b in self.fb.get_buckets():
            self.space.add_metric([b.account.name, b.name, 'snapshots'],
                                  b.space.snapshots)
            self.space.add_metric([b.account.name, b.name, 'total_physical'],
                                  b.space.total_physical)
            self.space.add_metric([b.account.name, b.name, 'virtual'],
                                  b.space.virtual)
            self.space.add_metric([b.account.name, b.name, 'unique'],
                                  b.space.unique)

    def get_metrics(self):
        self._data_reduction()
        self._objects()
        self._space()
        yield self.data_reduction
        yield self.objects
        yield self.space
