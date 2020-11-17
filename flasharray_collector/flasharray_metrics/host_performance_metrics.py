from prometheus_client.core import GaugeMetricFamily


class HostPerformanceMetrics():
    """
    Base class for FlashArray Prometheus host performance metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.latency = None
        self.bandwidth = None
        self.iops = None

    def _latency(self):
        """
        Create hosts latency metrics of gauge type, with host name and
        dimension as label.
        Metrics values can be iterated over.
        """

        self.latency = GaugeMetricFamily(
                                        'purefa_host_performance_latency_usec',
                                        'FlashArray host IO latency',
                                        labels=['host', 'dimension'])
        for h in self.fa.get_hosts():
            self.latency.add_metric([h['name'], 'read'], h['usec_per_read_op'])
            self.latency.add_metric([h['name'], 'write'], h['usec_per_write_op'])
            self.latency.add_metric([h['name'], 'mirrored_write'], h['usec_per_mirrored_write_op'])
            self.latency.add_metric([h['name'], 'san_read'], h['san_usec_per_read_op'])
            self.latency.add_metric([h['name'], 'san_write'], h['san_usec_per_write_op'])
            self.latency.add_metric([h['name'], 'san_mirrored_write'], h['san_usec_per_mirrored_write_op'])
            self.latency.add_metric([h['name'], 'queue_read'], h['queue_usec_per_read_op'])
            self.latency.add_metric([h['name'], 'queue_write'], h['queue_usec_per_write_op'])
            self.latency.add_metric([h['name'], 'queue_mirrored_write'], h['queue_usec_per_mirrored_write_op'])
            self.latency.add_metric([h['name'], 'qos_read'], h['qos_rate_limit_usec_per_read_op'])
            self.latency.add_metric([h['name'], 'qos_write'], h['qos_rate_limit_usec_per_write_op'])
            self.latency.add_metric([h['name'], 'qos_mirrored'], h['qos_rate_limit_usec_per_mirrored_write_op'])

    def _bandwidth(self):
        """
        Create hosts bandwidth metrics of gauge type, with host name and
        dimension as label.
        Metrics values can be iterated over.
        """
        self.bandwidth = GaugeMetricFamily(
                                    'purefa_host_performance_bandwidth_bytes',
                                    'FlashArray host bandwidth',
                                    labels=['host', 'dimension'])
        for h in self.fa.get_hosts():
            self.bandwidth.add_metric([h['name'], 'read'], h['output_per_sec'])
            self.bandwidth.add_metric([h['name'], 'write'], h['input_per_sec'])
            self.bandwidth.add_metric([h['name'], 'mirrored_write'], h['mirrored_input_per_sec'])

    def _iops(self):
        """
        Create hosts IOPS metrics of gauge type, with host name and
        dimension as label.
        Metrics values can be iterated over.
        """
        self.iops = GaugeMetricFamily('purefa_host_performance_iops',
                                      'FlashArray host IOPS',
                                      labels=['host', 'dimension'])
        for h in self.fa.get_hosts():
            self.iops.add_metric([h['name'], 'read'], h['reads_per_sec'])
            self.iops.add_metric([h['name'], 'write'], h['writes_per_sec'])
            self.iops.add_metric([h['name'], 'mirrored_write'], h['mirrored_writes_per_sec'])

    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        yield self.latency
        yield self.bandwidth
        yield self.iops
