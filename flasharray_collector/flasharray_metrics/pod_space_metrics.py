from prometheus_client.core import GaugeMetricFamily


class PodSpaceMetrics():
    """
    Base class for FlashArray Prometheus pod space metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = GaugeMetricFamily('purefa_pod_space_datareduction_ratio',
                                                'FlashArray pod data reduction ratio',
                                                labels=['pod'],
                                                unit='ratio')
        self.size = GaugeMetricFamily('purefa_pod_space_size_bytes',
                                      'FlashArray pod size',
                                      labels=['pod'])
        self.allocated = GaugeMetricFamily('purefa_pod_space_bytes',
                                           'FlashArray pod allocated space',
                                           labels=['pod', 'dimension'])

    def _data_reduction(self):
        """
        Create metrics of gauge type for pod data reduction
        Metrics values can be iterated over.
        """
        for p in self.fa.get_pods():
            self.data_reduction.add_metric([p['name']], p['data_reduction'] if p['data_reduction'] is not None else 0)

    def _size(self):
        """
        Create metrics of gauge type for pod size.
        Metrics values can be iterated over.
        """
        for p in self.fa.get_pods():
            self.size.add_metric([p['name']], p['size'] if p['size'] is not None else 0)

    def _allocated(self):
        for p in self.fa.get_pods():
            self.allocated.add_metric([p['name'], 'volumes'], p['volumes'] if p['volumes'] is not None else 0)
            self.allocated.add_metric([p['name'], 'snapshots'], p['snapshots'] if p['snapshots'] is not None else 0)
            self.allocated.add_metric([p['name'], 'total'], p['total'] if p['total'] is not None else 0)

    def get_metrics(self):
        self._data_reduction()
        self._size()
        self._allocated()
        yield self.data_reduction
        yield self.size
        yield self.allocated
