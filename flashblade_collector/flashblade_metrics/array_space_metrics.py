from prometheus_client.core import GaugeMetricFamily


class ArraySpaceMetrics():
    """
    Base class for FlashBlade Prometheus array space metrics
    """
    def __init__(self, fb):
        self.fb = fb
        space = None
        reduction = None

    def _space(self):
        """
        Create metrics of gauge type for array space indicators.
        """
        fbspace = self.fb.get_array_space()
        self.space = GaugeMetricFamily('purefb_array_space_bytes',
                                       'FlashBlade total space capacity',
                                       labels=['dimension'])
        self.space.add_metric(['capacity'], fbspace.capacity)
        self.space.add_metric(['total_physical'], fbspace.space.total_physical)
        self.space.add_metric(['snapshots'], fbspace.space.snapshots)

    def _reduction(self):
        """
        Create metrics of gauge type for array data redution indicator.
        """
        fbspace = self.fb.get_array_space()
        self.reduction = GaugeMetricFamily('purefb_array_space_data_reduction',
                                           'FlashBlade overall data reduction',
                                           labels=[])
        self.reduction.add_metric([], fbspace.space.data_reduction)

    def get_metrics(self):
        self._space()
        self._reduction()
        yield self.space
        yield self.reduction
