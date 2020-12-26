from prometheus_client.core import GaugeMetricFamily
from . import array_specific_performance_mapping

class ArraySpecificPerformanceMetrics():
    """
    Base class for FlashBlade Prometheus array specific performance metrics
    """

    def __init__(self, fb):
        self.fb = fb
        self.latency = GaugeMetricFamily(
                              'purefb_array_specific_performance_latency_usec',
                              'FlashBlade array specific latency',
                              labels=['protocol', 'dimension'])
        self.iops = GaugeMetricFamily('purefb_array_specific_performance_iops',
                                      'FlashBlade array specific IOPS',
                                      labels=['protocol', 'dimension'])



    def _latency(self):
        """
        Create array specific latency performance metrics of gauge type.
        """
        def _add_metric(proto, metric):
            if proto == 'nfs':
                mapping = array_specific_performance_mapping.nfs_array_specific_latency
            elif proto == 'http':
                mapping = array_specific_performance_mapping.http_array_specific_latency
            elif proto == 's3':
                mapping = array_specific_performance_mapping.s3_array_specific_latency

            m = self.fb.get_array_specific_performance(proto)
            if m is not None:
                for _k in getattr(m, '__dict__'):
                    k = _k[1:]
                    if k in mapping.keys() and getattr(m, _k) is not None :
                        metric.add_metric([proto, mapping[k]], getattr(m, _k))

        _add_metric('nfs', self.latency)
        _add_metric('http', self.latency)
        _add_metric('s3', self.latency)

    def _iops(self):
        """
        Create array specific iops performance metrics of gauge type.
        """
        def _add_metric(proto, metric):
            if proto == 'nfs':
                mapping = array_specific_performance_mapping.nfs_array_specific_iops
            elif proto == 'http':
                mapping = array_specific_performance_mapping.http_array_specific_iops
            elif proto == 's3':
                mapping = array_specific_performance_mapping.s3_array_specific_iops

            m = self.fb.get_array_specific_performance(proto)
            if m is not None:
                for _k in getattr(m, '__dict__'):
                    k = _k[1:]
                    if k in mapping.keys() and getattr(m, _k) is not None :
                        metric.add_metric([proto, mapping[k]], getattr(m, _k))

        _add_metric('nfs', self.iops)
        _add_metric('http', self.iops)
        _add_metric('s3', self.iops)

    def get_metrics(self):
        self._latency()
        self._iops()
        yield self.latency
        yield self.iops
