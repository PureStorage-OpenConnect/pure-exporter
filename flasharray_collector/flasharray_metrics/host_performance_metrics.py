from prometheus_client.core import GaugeMetricFamily
from . import mappings


class HostPerformanceMetrics():
    """
    Base class for FlashArray Prometheus host performance metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.latency = GaugeMetricFamily('purefa_host_performance_latency_usec',
                                         'FlashArray host IO latency',
                                         labels=['host', 'dimension'])
        self.bandwidth = GaugeMetricFamily('purefa_host_performance_bandwidth_bytes',
                                           'FlashArray host bandwidth',
                                           labels=['host', 'dimension'])
        self.iops = GaugeMetricFamily('purefa_host_performance_iops',
                                      'FlashArray host IOPS',
                                      labels=['host', 'dimension'])

    def _mk_metric(self, metric, entity_list, mapping):
        """
        Create metrics of gauge type, with given name 'name' and
        dimension as label.
        Metrics values can be iterated over.
        """
        for e in entity_list:
            for k in mapping:
                if k in e:
                    metric.add_metric([e['name'], mapping[k]], e[k])

    def _latency(self):
        """
        Create hosts latency metrics of gauge type.
        """
        self._mk_metric(self.latency,
                        self.fa.get_hosts(),
                        mappings.host_latency_mapping)

    def _bandwidth(self):
        """
        Create hosts bandwidth metrics of gauge type.
        """
        self._mk_metric(self.bandwidth,
                        self.fa.get_hosts(),
                        mappings.host_bandwidth_mapping)

    def _iops(self):
        """
        Create hosts IOPS metrics of gauge type.
        """
        self._mk_metric(self.iops,
                        self.fa.get_hosts(),
                        mappings.host_iops_mapping)

    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        yield self.latency
        yield self.bandwidth
        yield self.iops
