from prometheus_client.core import GaugeMetricFamily


class VolumeSpaceMetrics():
    """
    Base class for FlashArray Prometheus volume space metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = GaugeMetricFamily('purefa_volume_space_datareduction_ratio',
                                                'FlashArray volumes data reduction ratio',
                                                labels=['pod', 'naaid'],
                                                unit='ratio')
        self.size = GaugeMetricFamily('purefa_volume_space_size_bytes',
                                      'FlashArray volumes size',
                                      labels=['pod', 'naaid'])
        self.allocated = GaugeMetricFamily('purefa_volume_space_bytes',
                                           'FlashArray allocated space',
                                           labels=['pod', 'naaid', 'dimension'])

    def _data_reduction(self):
        """
        Create metrics of gauge type for volume data reduction
        Metrics values can be iterated over.
        """
        for v in self.fa.get_volumes():
            self.data_reduction.add_metric([v['name'], v['naaid']], v['data_reduction'] if v['data_reduction'] is not None else 0)


    def _size(self):
        for v in self.fa.get_volumes():
            self.size.add_metric([v['name'], v['naaid']], v['size'] if v['size'] is not None else 0)

    def _allocated(self):
        for v in self.fa.get_volumes():
            self.allocated.add_metric([v['name'], v['naaid'], 'volumes'], v['volumes'] if v['volumes'] is not None else 0)
            self.allocated.add_metric([v['name'], v['naaid'], 'snapshots'], v['snapshots'] if v['snapshots'] is not None else 0)
            self.allocated.add_metric([v['name'], v['naaid'], 'total'], v['total'] if v['total'] is not None else 0)

    def get_metrics(self):
        self._data_reduction()
        self._size()
        self._allocated()
        yield self.data_reduction
        yield self.size
        yield self.allocated
