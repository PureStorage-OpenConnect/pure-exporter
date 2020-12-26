from prometheus_client.core import GaugeMetricFamily


class BucketsSpaceMetrics():
    """
    Base class for FlashBlade Prometheus buckets space metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.data_reduction = GaugeMetricFamily('purefb_buckets_data_reduction',
                                                'FlashBlade buckets data reduction',
                                                labels=['account', 'name'])
        self.objects = GaugeMetricFamily('purefb_buckets_object_count',
                                         'FlashBlade buckets objects counter',
                                         labels=['account', 'name'])
        self.space = GaugeMetricFamily('purefb_buckets_space_bytes',
                                       'FlashBlade buckets space',
                                       labels=['account', 'name', 'dimension'])
        self.buckets = fb.get_buckets()

    def _data_reduction(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        """
        for b in self.buckets:
            self.data_reduction.add_metric([b.account.name, b.name],
                                           b.space.data_reduction if b.space.data_reduction is not None else 0)

    def _objects(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        """
        for b in self.buckets:
            self.objects.add_metric([b.account.name, b.name], b.object_count)

    def _space(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        """
        for b in self.buckets:
            self.space.add_metric([b.account.name, b.name, 'snapshots'], b.space.snapshots)
            self.space.add_metric([b.account.name, b.name, 'total_physical'], b.space.total_physical)
            self.space.add_metric([b.account.name, b.name, 'virtual'], b.space.virtual)
            self.space.add_metric([b.account.name, b.name, 'unique'], b.space.unique)

    def get_metrics(self):
        self._data_reduction()
        self._objects()
        self._space()
        yield self.data_reduction
        yield self.objects
        yield self.space
