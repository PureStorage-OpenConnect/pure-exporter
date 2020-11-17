from prometheus_client.core import GaugeMetricFamily


class PodPerformanceMetrics():
    """
    Base class for FlashArray Prometheus pod performance metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.latency = None
        self.bandwidth = None
        self.iops = None

    def _latency(self):
        """
        Create pods latency metrics of gauge type, with pod name and
        dimension as label.
        Metrics values can be iterated over.
        """

        self.latency = GaugeMetricFamily(
                                        'purefa_pod_performance_latency_usec',
                                        'FlashArray pod IO latency',
                                        labels=['pod', 'dimension'])
        for p in self.fa.get_pods():
            self.latency.add_metric([p['name'], 'read'], p['usec_per_read_op'])
            self.latency.add_metric([p['name'], 'write'], p['usec_per_write_op'])
            self.latency.add_metric([p['name'], 'mirrored_write'], p['usec_per_mirrored_write_op'])
            self.latency.add_metric([p['name'], 'san_read'], p['san_usec_per_read_op'])
            self.latency.add_metric([p['name'], 'san_write'], p['san_usec_per_write_op'])
            self.latency.add_metric([p['name'], 'san_mirrored_write'], p['san_usec_per_mirrored_write_op'])
            self.latency.add_metric([p['name'], 'queue_read'], p['queue_usec_per_read_op'])
            self.latency.add_metric([p['name'], 'queue_write'], p['queue_usec_per_write_op'])
            self.latency.add_metric([p['name'], 'queue_mirrored_write'], p['queue_usec_per_mirrored_write_op'])
            self.latency.add_metric([p['name'], 'qos_read'], p['qos_rate_limit_usec_per_read_op'])
            self.latency.add_metric([p['name'], 'qos_write'], p['qos_rate_limit_usec_per_write_op'])
            self.latency.add_metric([p['name'], 'qos_mirrored'], p['qos_rate_limit_usec_per_mirrored_write_op'])

    def _bandwidth(self):
        """
        Create pods bandwidth metrics of gauge type, with pod name and
        dimension as label.
        Metrics values can be iterated over.
        """
        self.bandwidth = GaugeMetricFamily(
                                    'purefa_pod_performance_bandwidth_bytes',
                                    'FlashArray pod bandwidth',
                                    labels=['pod', 'dimension'])
        for p in self.fa.get_pods():
            self.bandwidth.add_metric([p['name'], 'read'], p['output_per_sec'])
            self.bandwidth.add_metric([p['name'], 'write'], p['input_per_sec'])
            self.bandwidth.add_metric([p['name'], 'mirrored_write'], p['mirrored_input_per_sec'])

    def _iops(self):
        """
        Create IOPS bandwidth metrics of gauge type, with pod name and
        dimension as label.
        Metrics values can be iterated over.
        """
        self.iops = GaugeMetricFamily('purefa_pod_performance_iops',
                                      'FlashArray pod IOPS',
                                      labels=['pod', 'dimension'])
        for p in self.fa.get_pods():
            self.iops.add_metric([p['name'], 'read'], p['reads_per_sec'])
            self.iops.add_metric([p['name'], 'write'], p['writes_per_sec'])
            self.iops.add_metric([p['name'], 'mirrored_write'], p['mirrored_writes_per_sec'])

    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        yield self.latency
        yield self.bandwidth
        yield self.iops
