from prometheus_client.core import GaugeMetricFamily


class ArraySpaceMetrics():
    """
    Base class for FlashBlade Prometheus array space metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.space = GaugeMetricFamily('purefb_array_space_bytes',
                                       'FlashBlade total space capacity',
                                       labels=['dimension'])
        self.reduction = GaugeMetricFamily('purefb_array_space_data_reduction',
                                           'FlashBlade overall data reduction',
                                           labels=[])
        self.array_space = fb.get_array_space()

    def _space(self):
        """
        Create metrics of gauge type for array space indicators.
        """
        if self.array_space is  None:
            return
        self.space.add_metric(['unique'], self.array_space.space.unique)
        self.space.add_metric(['virtual'], self.array_space.space.virtual)
        self.space.add_metric(['total_physical'], self.array_space.space.total_physical)
        self.space.add_metric(['snapshots'], self.array_space.space.snapshots)
        self.space.add_metric(['capacity'], self.array_space.capacity)

    def _reduction(self):
        """
        Create metrics of gauge type for array data redution indicator.
        """
        if self.array_space is  None:
            return
        self.reduction.add_metric([], self.array_space.space.data_reduction)

    def get_metrics(self):
        self._space()
        self._reduction()
        yield self.space
        yield self.reduction
