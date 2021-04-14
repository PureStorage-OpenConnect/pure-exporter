from prometheus_client.core import GaugeMetricFamily
from . import mappings
import re


class VolumePerformanceMetrics():
    """
    Base class for FlashArray Prometheus volume performance metrics
    """

    def __init__(self, volumes):
        self.volumes = volumes
        self.latency = GaugeMetricFamily('purefa_volume_performance_latency_usec',
                                         'FlashArray volume IO latency',
                                         labels = ['volume', 'naaid', 'pod', 'vgroup' ,'dimension'])
        self.bandwidth = GaugeMetricFamily('purefa_volume_performance_throughput_bytes',
                                           'FlashArray volume throughput',
                                           labels = ['volume', 'naaid', 'pod', 'vgroup' ,'dimension'])
        self.iops = GaugeMetricFamily('purefa_volume_performance_iops',
                                      'FlashArray volume IOPS',
                                      labels = ['volume', 'naaid', 'pod', 'vgroup', 'dimension'])

    def _mk_metric(self, metric, entity_list, mapping):
        """
        Create metrics of gauge type, with volume name, naaid and
        dimension as label.
        Metrics values can be iterated over.
        """
        p = re.compile(r'::')
        for e in entity_list:
            for k in mapping:
                if k in e:
                    e_name = p.split(e['name'])
                    if len(e_name) == 1:
                        e_name = ['/'] + e_name
                    if 'vgroup' not in e.keys():
                        e['vgroup'] = ''
                    metric.add_metric([e_name[1], e['naaid'], e_name[0], e['vgroup'], mapping[k]], e[k])

    def _latency(self):
        """
        Create volumes latency metrics of gauge type.
        """
        self._mk_metric(self.latency,
                        self.volumes,
                        mappings.volume_latency_mapping)

    def _bandwidth(self):
        """
        Create volumes bandwidth metrics of gauge type.
        """
        self._mk_metric(self.bandwidth,
                        self.volumes,
                        mappings.volume_bandwidth_mapping)

    def _iops(self):
        """
        Create IOPS bandwidth metrics of gauge type.
        """
        self._mk_metric(self.iops,
                        self.volumes,
                        mappings.volume_iops_mapping)

    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        yield self.latency
        yield self.bandwidth
        yield self.iops
