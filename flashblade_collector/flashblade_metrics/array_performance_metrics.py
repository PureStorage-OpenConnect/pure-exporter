from prometheus_client.core import GaugeMetricFamily


class ArrayPerformanceMetrics():
    """
    Base class for FlashBlade Prometheus array performance metrics
    """

    def __init__(self, fb):
        self.fb = fb
        self.protocols = ['http', 'nfs', 's3', 'smb']
        self.latency = GaugeMetricFamily('purefb_array_performance_latency_usec',
                                         'FlashBlade array latency',
                                         labels=['protocol', 'dimension'])
        self.iops = GaugeMetricFamily('purefb_array_performance_iops',
                                      'FlashBlade array IOPS',
                                      labels=['protocol', 'dimension'])
        self.ops_size = GaugeMetricFamily('purefb_array_performance_opns_bytes',
                                          'FlashBlade array average bytes per operations',
                                          labels=['protocol', 'dimension'])
        self.throughput = GaugeMetricFamily('purefb_array_performance_throughput_bytes',
                                            'FlashBlade array throughput',
                                            labels=['protocol', 'dimension'])

    def _latency(self):
        """
        Create array latency performance metrics of gauge type.
        """
        for p in self.protocols:
            m = self.fb.get_array_performance(p)
            if m is None:
                continue
            self.latency.add_metric([p, 'read'], m.usec_per_read_op)
            self.latency.add_metric([p, 'write'], m.usec_per_write_op)
            self.latency.add_metric([p, 'other'], m.usec_per_other_op)

    def _iops(self):
        """
        Create array iops performance metrics of gauge type.
        """
        for p in self.protocols:
            m = self.fb.get_array_performance(p)
            if m is None:
                continue
            self.iops.add_metric([p, 'read'], m.reads_per_sec)
            self.iops.add_metric([p, 'write'], m.writes_per_sec)
            self.iops.add_metric([p, 'other'], m.others_per_sec)
            # self.iops.add_metric([p, 'in'], m.input_per_sec)
            # self.iops.add_metric([p, 'out'], m.output_per_sec)

    def _ops_size(self):
        """
        Create array operation size performance metrics of gauge type.
        """
        for p in self.protocols:
            m = self.fb.get_array_performance(p)
            if m is None:
                continue
            self.ops_size.add_metric([p, 'per_op'], m.bytes_per_op)
            self.ops_size.add_metric([p, 'read'], m.bytes_per_read)
            self.ops_size.add_metric([p, 'write'], m.bytes_per_write)

    def _throughput(self):
        """
        Create array throughput performance metrics of gauge type.
        """
        for p in self.protocols:
            m = self.fb.get_array_performance(p)
            if m is None:
                continue
            self.throughput.add_metric([p, 'read'], m.read_bytes_per_sec)
            self.throughput.add_metric([p, 'write'], m.write_bytes_per_sec)

    def get_metrics(self):
        self._latency()
        self._iops()
        self._ops_size()
        self._throughput()
        yield self.latency
        yield self.iops
        yield self.ops_size
        yield self.throughput
