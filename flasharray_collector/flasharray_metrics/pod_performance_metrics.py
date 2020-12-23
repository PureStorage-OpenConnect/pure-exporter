from prometheus_client.core import GaugeMetricFamily
from . import mappings


class PodPerformanceMetrics():
    """
    Base class for FlashArray Prometheus pod performance metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.latency = GaugeMetricFamily('purefa_pod_performance_latency_usec',
                                         'FlashArray pod IO latency',
                                         labels=['pod', 'dimension'])
        self.bandwidth = GaugeMetricFamily('purefa_pod_performance_bandwidth_bytes',
                                           'FlashArray pod bandwidth',
                                           labels=['pod', 'dimension'])
        self.iops = GaugeMetricFamily('purefa_pod_performance_iops',
                                      'FlashArray pod IOPS',
                                      labels=['pod', 'dimension'])

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
        Create pods latency metrics of gauge type, with pod name and
        dimension as label.
        """
        self._mk_metric(self.latency,
                        self.fa.get_pods(),
                        mappings.pod_latency_mapping)

    def _bandwidth(self):
        """
        Create pods bandwidth metrics of gauge type, with pod name and
        dimension as label.
        """
        self._mk_metric(self.bandwidth,
                        self.fa.get_pods(),
                        mappings.pod_bandwidth_mapping)


    def _iops(self):
        """
        Create IOPS bandwidth metrics of gauge type, with pod name and
        dimension as label.
        """
        self._mk_metric(self.iops,
                        self.fa.get_pods(),
                        mappings.pod_iops_mapping)

    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        yield self.latency
        yield self.bandwidth
        yield self.iops
