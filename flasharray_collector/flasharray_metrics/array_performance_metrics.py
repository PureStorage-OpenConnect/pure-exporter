from prometheus_client.core import GaugeMetricFamily
from . import mappings


class ArrayPerformanceMetrics():
    """
    Base class for FlashArray Prometheus array performance metrics
    """

    def __init__(self, fa):
        self.fa = fa

        self.latency = GaugeMetricFamily('purefa_array_performance_latency_usec',
                                         'FlashArray latency',
                                         labels=['dimension'])
        self.bandwidth = GaugeMetricFamily('purefa_array_performance_bandwidth_bytes',
                                           'FlashArray bandwidth',
                                           labels=['dimension'])
        self.iops = GaugeMetricFamily('purefa_array_performance_iops',
                                      'FlashArray IOPS',
                                      labels=['dimension'])
        self.avg_bsz = GaugeMetricFamily('purefa_array_performance_avg_block_bytes',
                                         'FlashArray avg block size',
                                         labels=['dimension'])
        self.qdepth = GaugeMetricFamily('purefa_array_performance_qdepth',
                                        'FlashArray queue depth',
                                        labels=['dimension'])

    def _mk_metric(self, metric, entity_list, mapping):
        """
        Create metrics of gauge type, with dimension as label.
        Metrics values can be iterated over.
        """
        for k in mapping:
            if k in entity_list:
                metric.add_metric([mapping[k]], entity_list[k] if entity_list[k] is not None else 0)

    def _latency(self):
        """
        Create array latency performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        self._mk_metric(self.latency,
                        self.fa.get_array(), 
                        mappings.array_latency_mapping)

    def _bandwidth(self):
        """
        Create array bandwidth performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        self._mk_metric(self.bandwidth,
                        self.fa.get_array(), 
                        mappings.array_bandwidth_mapping)

    def _iops(self):
        """
        Create array iops performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        self._mk_metric(self.iops,
                        self.fa.get_array(), 
                        mappings.array_iops_mapping)

    def _avg_block_size(self):
        """
        Create array average block size performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        self._mk_metric(self.avg_bsz,
                        self.fa.get_array(), 
                        mappings.array_bsize_mapping)

    def _qdepth(self):
        """
        Create array queue depth performance metric of gauge type.
        Metrics values can be iterated over.
        """
        self._mk_metric(self.qdepth,
                        self.fa.get_array(), 
                        mappings.array_qdepth_mapping)

    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        self._avg_block_size()
        self._qdepth()
        yield self.latency
        yield self.bandwidth
        yield self.iops
        yield self.avg_bsz
        yield self.qdepth
