from prometheus_client.core import GaugeMetricFamily


class ClientsPerformanceMetrics():
    """
    Base class for FlashBlade Prometheus clients performance metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.latency = None
        self.iops = None
        self.ops_size = None
        self.throughput = None

    def _latency(self):
        """
        Create metrics of gauge type for client latency metrics.
        """
        self.latency = GaugeMetricFamily(
                                      'purefb_client_performance_latency_usec',
                                      'FlashBlade latency',
                                      labels=['name', 'port', 'dimension'])

        for cperf in self.fb.get_clients_performance():
            client, port = cperf.name.split(':')
            self.latency.add_metric([client, port, 'read'],
                                    cperf.usec_per_read_op)
            self.latency.add_metric([client, port, 'write'],
                                    cperf.usec_per_write_op)
            self.latency.add_metric([client, port, 'other'],
                                    cperf.usec_per_other_op)

    def _iops(self):
        """
        Create metrics of gauge type for client iops metrics.
        """
        self.iops = GaugeMetricFamily('purefb_client_performance_iops',
                                      'FlashBlade IOPS',
                                      labels=['name', 'port', 'dimension'])

        for cperf in self.fb.get_clients_performance():
            client, port = cperf.name.split(':')
            self.iops.add_metric([client, port, 'read'],
                                 cperf.reads_per_sec)
            self.iops.add_metric([client, port, 'write'],
                                 cperf.writes_per_sec)
            self.iops.add_metric([client, port, 'other'],
                                 cperf.others_per_sec)

    def _ops_size(self):
        """
        Create metrics of gauge type for client operations size  metrics.
        """
        self.ops_size = GaugeMetricFamily(
                              'purefb_client_performance_opns_bytes',
                              'FlashBlade client average bytes per operations',
                              labels=['name', 'port', 'dimension'])
        for cperf in self.fb.get_clients_performance():
            client, port = cperf.name.split(':')
            self.ops_size.add_metric([client, port, 'per_op'],
                                     cperf.bytes_per_op)
            self.ops_size.add_metric([client, port, 'read'],
                                     cperf.bytes_per_read)
            self.ops_size.add_metric([client, port, 'write'],
                                     cperf.bytes_per_write)

    def _throughput(self):
        """
        Create metrics of gauge type for client throughput metrics.
        """
        self.throughput = GaugeMetricFamily(
                                  'purefb_client_performance_throughput_bytes',
                                  'FlashBlade client_throughput',
                                  labels=['name', 'port', 'dimension'])

        for cperf in self.fb.get_clients_performance():
            client, port = cperf.name.split(':')
            self.throughput.add_metric([client, port, 'read'],
                                       cperf.read_bytes_per_sec)
            self.throughput.add_metric([client, port, 'write'],
                                       cperf.write_bytes_per_sec)

    def get_metrics(self):
        self._latency()
        self._iops()
        self._ops_size()
        self._throughput()
        yield self.latency
        yield self.iops
        yield self.ops_size
        yield self.throughput
