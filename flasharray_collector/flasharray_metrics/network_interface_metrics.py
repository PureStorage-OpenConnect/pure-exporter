from prometheus_client.core import GaugeMetricFamily
from . import mappings
import re

class NetworkInterfacePerformanceMetrics():
    """
    Base class for FlashArray Prometheus network interface performance metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.performance = GaugeMetricFamily('purefa_network_interface_performance',
                                         'FlashArray network interface performance',
                                         labels = ['interface','dimension'])

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

    def _performance(self):
        """
        Create array network interface metrics of gauge type.
        """
        self._mk_metric(self.performance,
                        self.fa.get_network_interfaces(),
                        mappings.array_network_interface_mapping)

    def get_metrics(self):
        self._performance()
        yield self.performance
