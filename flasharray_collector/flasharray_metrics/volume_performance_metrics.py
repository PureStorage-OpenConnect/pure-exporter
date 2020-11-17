from prometheus_client.core import GaugeMetricFamily


class VolumePerformanceMetrics():
    """
    Base class for FlashArray Prometheus volume performance metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.latency = None
        self.bandwidth = None
        self.iops = None

    def _latency(self):
        """
        Create volumes latency metrics of gauge type, with volume name, naaid and
        dimension as label.
        Metrics values can be iterated over.
        """

        self.latency = GaugeMetricFamily(
                                        'purefa_volume_performance_latency_usec',
                                        'FlashArray volume IO latency',
                                        labels = ['volume', 'naaid', 'dimension'])
        for v in self.fa.get_volumes():
            self.latency.add_metric([v['name'], v['naaid'], 'read'], v['usec_per_read_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'write'], v['usec_per_write_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'mirrored_write'], v['usec_per_mirrored_write_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'san_read'], v['san_usec_per_read_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'san_write'], v['san_usec_per_write_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'san_mirrored_write'], v['san_usec_per_mirrored_write_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'queue_read'], v['queue_usec_per_read_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'queue_write'], v['queue_usec_per_write_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'queue_mirrored_write'], v['queue_usec_per_mirrored_write_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'qos_read'], v['qos_rate_limit_usec_per_read_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'qos_write'], v['qos_rate_limit_usec_per_write_op'])
            self.latency.add_metric([v['name'], v['naaid'], 'qos_mirrored'], v['qos_rate_limit_usec_per_mirrored_write_op'])

    def _bandwidth(self):
        """
        Create pods bandwidth metrics of gauge type, with host name, naaid and
        dimension as label.
        Metrics values can be iterated over.
        """
        self.bandwidth = GaugeMetricFamily('purefa_volume_performance_throughput_bytes',
                                           'FlashArray volume throughput',
                                           labels = ['volume', 'naaid', 'dimension'])
        for v in self.fa.get_volumes():
            self.bandwidth.add_metric([v['name'], v['naaid'], 'read'], v['output_per_sec'])
            self.bandwidth.add_metric([v['name'], v['naaid'], 'write'], v['input_per_sec'])
            self.bandwidth.add_metric([v['name'], v['naaid'], 'mirrored_write'], v['mirrored_input_per_sec'])

    def _iops(self):
        """
        Create IOPS bandwidth metrics of gauge type, with volume name, naaid and
        dimension as label.
        Metrics values can be iterated over.
        """
        self.iops = GaugeMetricFamily('purefa_volume_performance_iops',
                                      'FlashArray volume IOPS',
                                      labels = ['volume', 'naaid', 'dimension'])
        for v in self.fa.get_volumes():
            self.iops.add_metric([v['name'], v['naaid'], 'read'], v['reads_per_sec'])
            self.iops.add_metric([v['name'], v['naaid'], 'write'], v['writes_per_sec'])
            self.iops.add_metric([v['name'], v['naaid'], 'mirrored_write'], v['mirrored_writes_per_sec'])

    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        yield self.latency
        yield self.bandwidth
        yield self.iops
