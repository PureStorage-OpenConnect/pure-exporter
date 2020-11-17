from prometheus_client.core import GaugeMetricFamily


class PodSpaceMetrics():
    """
    Base class for FlashArray Prometheus pod space metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = None
        self.size = None
        self.allocated = None

    def _data_reduction(self):
        """
        Create metrics of gauge type for pod data reduction
        Metrics values can be iterated over.
        """

        self.data_reduction = GaugeMetricFamily(
                                'purefa_pod_space_datareduction_ratio',
                                'FlashArray pod data reduction ratio',
                                labels=['pod'],
                                unit='ratio')
        for p in self.fa.get_pods():
            self.data_reduction.add_metric([p['name']], p['data_reduction'])


    def _size(self):
        self.size = GaugeMetricFamily('purefa_pod_space_size_bytes',
                                      'FlashArray pod size',
                                      labels=['pod'])
        for p in self.fa.get_pods():
            self.size.add_metric([p['name']], p['size'])

    def _allocated(self):
        self.allocated = GaugeMetricFamily('purefa_pod_space_bytes',
                                     'FlashArray pod allocated space',
                                     labels=['pod', 'dimension'])
        for p in self.fa.get_pods():
            self.allocated.add_metric([p['name'], 'volumes'], p['volumes'])
            self.allocated.add_metric([p['name'], 'snapshots'], p['snapshots'])
            self.allocated.add_metric([p['name'], 'total'], p['total'])

    def get_metrics(self):
        self._data_reduction()
        self._size()
        self._allocated()
        yield self.data_reduction
        yield self.size
        yield self.allocated
