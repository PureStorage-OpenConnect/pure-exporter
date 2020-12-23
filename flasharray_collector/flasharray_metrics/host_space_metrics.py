from prometheus_client.core import GaugeMetricFamily


class HostSpaceMetrics():
    """
    Base class for FlashArray Prometheus host space metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = GaugeMetricFamily('purefa_host_space_datareduction_ratio',
                                                'FlashArray host volumes data reduction ratio',
                                                labels=['host'],
                                                unit='ratio')
        self.size = GaugeMetricFamily('purefa_host_space_size_bytes',
                                      'FlashArray host volumes size',
                                      labels=['host'])
        self.allocated = GaugeMetricFamily('purefa_host_space_bytes',
                                           'FlashArray host volumes allocated space',
                                           labels=['host', 'dimension'])

    def _data_reduction(self):
        for h in self.fa.get_hosts():
            self.data_reduction.add_metric([h['name']], h['data_reduction'] if h['data_reduction'] is not None else 0)


    def _size(self):
        for h in self.fa.get_hosts():
            self.size.add_metric([h['name']], h['size'] if h['size'] is not None else 0)

    def _allocated(self):
        for h in self.fa.get_hosts():
            self.allocated.add_metric([h['name'], 'volumes'], h['volumes'] if h['volumes'] is not None else 0)
            self.allocated.add_metric([h['name'], 'snapshots'], h['snapshots'] if h['snapshots'] is not None else 0)
            self.allocated.add_metric([h['name'], 'total'], h['total'] if h['total'] is not None else 0)

    def get_metrics(self):
        self._data_reduction()
        self._size()
        self._allocated()
        yield self.data_reduction
        yield self.size
        yield self.allocated
