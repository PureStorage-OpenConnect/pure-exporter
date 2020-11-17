from prometheus_client.core import GaugeMetricFamily


class HostSpaceMetrics():
    """
    Base class for FlashArray Prometheus host space metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = None
        self.size = None
        self.allocated = None

    def _data_reduction(self):
        self.data_reduction = GaugeMetricFamily(
                                'purefa_host_space_datareduction_ratio',
                                'FlashArray host volumes data reduction ratio',
                                labels=['host'],
                                unit='ratio')
        for h in self.fa.get_hosts():
            self.data_reduction.add_metric([h['name']], h['data_reduction'])


    def _size(self):
        self.size = GaugeMetricFamily('purefa_host_space_size_bytes',
                                      'FlashArray host volumes size',
                                      labels=['host'])
        for h in self.fa.get_hosts():
            self.size.add_metric([h['name']], h['size'])

    def _allocated(self):
        self.allocated = GaugeMetricFamily('purefa_host_space_bytes',
                                     'FlashArray host volumes allocated space',
                                     labels=['host', 'dimension'])
        for h in self.fa.get_hosts():
            self.allocated.add_metric([h['name'], 'volumes'], h['volumes'])
            self.allocated.add_metric([h['name'], 'snapshots'], h['snapshots'])
            self.allocated.add_metric([h['name'], 'total'], h['total'])

    def get_metrics(self):
        self._data_reduction()
        self._size()
        self._allocated()
        yield self.data_reduction
        yield self.size
        yield self.allocated
