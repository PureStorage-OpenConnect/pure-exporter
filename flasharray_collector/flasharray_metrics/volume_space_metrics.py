from prometheus_client.core import GaugeMetricFamily


class VolumeSpaceMetrics():
    """
    Base class for FlashArray Prometheus volume space metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = None
        self.size = None
        self.allocated = None

    def _data_reduction(self):
        """
        Create metrics of gauge type for volume data reduction
        Metrics values can be iterated over.
        """

        self.data_reduction = GaugeMetricFamily(
                                'purefa_volume_space_datareduction_ratio',
                                'FlashArray volumes data reduction ratio',
                                labels=['pod', 'naaid'],
                                unit='ratio')
        for v in self.fa.get_volumes():
            self.data_reduction.add_metric([v['name'], v['naaid']], v['data_reduction'])


    def _size(self):
        self.size = GaugeMetricFamily('purefa_volume_space_size_bytes',
                                      'FlashArray volumes size',
                                      labels=['pod', 'naaid'])
        for v in self.fa.get_volumes():
            self.size.add_metric([v['name'], v['naaid']], v['size'])

    def _allocated(self):
        self.allocated = GaugeMetricFamily('purefa_volume_space_bytes',
                                     'FlashArray allocated space',
                                     labels=['pod', 'naaid', 'dimension'])
        for v in self.fa.get_volumes():
            self.allocated.add_metric([v['name'], v['naaid'], 'volumes'], v['volumes'])
            self.allocated.add_metric([v['name'], v['naaid'], 'snapshots'], v['snapshots'])
            self.allocated.add_metric([v['name'], v['naaid'], 'total'], v['total'])

    def get_metrics(self):
        self._data_reduction()
        self._size()
        self._allocated()
        yield self.data_reduction
        yield self.size
        yield self.allocated
