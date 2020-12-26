from prometheus_client.core import GaugeMetricFamily


class FilesystemsPerformanceMetrics():
    """
    Base class for FlashBlade Prometheus filesystem performance metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.latency = GaugeMetricFamily('purefb_filesystem_performance_latency_usec',
                                         'FlashBlade filesystem latency',
                                         labels=['protocol', 'name', 'dimension'])
        self.iops = GaugeMetricFamily('purefb_filesystem_performance_iops',
                                      'FlashBlade filesystem IOPS',
                                      labels=['protocol', 'name', 'dimension'])
        self.ops_size = GaugeMetricFamily('purefb_filesystem_performance_opns_bytes',
                                          'FlashBlade filesystem average bytes per operations',
                                          labels=['protocol', 'name', 'dimension'])
        self.throughput = GaugeMetricFamily('purefb_filesystem_performance_throughput_bytes',
                                            'FlashBlade filesystem throughput',
                                            labels=['protocol', 'name', 'dimension'])
        self.nfs_filesystems_performance = fb.get_nfs_filesystems_performance()



    def _latency(self):
        """
        Create metrics of gauge type for filesystems latency,
        with filesystem name as label.
        """
        for f in self.nfs_filesystems_performance:
            self.latency.add_metric(['nfs', f.name, 'read'], f.usec_per_read_op)
            self.latency.add_metric(['nfs', f.name, 'write'], f.usec_per_write_op)
            self.latency.add_metric(['nfs', f.name, 'other'], f.usec_per_other_op)

    def _iops(self):
        """
        Create metrics of gauge type for filesystems iops,
        with filesystem name as label.
        """
        for f in self.nfs_filesystems_performance:
            self.iops.add_metric(['nfs', f.name, 'read'], f.reads_per_sec)
            self.iops.add_metric(['nfs', f.name, 'write'], f.writes_per_sec)
            self.iops.add_metric(['nfs', f.name, 'other'], f.others_per_sec)

    def _ops_size(self):
        """
        Create metrics of gauge type for filesystems average operations size,
        with filesystem name as label.
        """

        for f in self.nfs_filesystems_performance:
            self.ops_size.add_metric(['nfs', f.name, 'per_op'], f.bytes_per_op)
            self.ops_size.add_metric(['nfs', f.name, 'read'], f.bytes_per_read)
            self.ops_size.add_metric(['nfs', f.name, 'write'], f.bytes_per_write)

    def _throughput(self):
        """
        Create metrics of gauge type for filesystems throughput,
        with filesystem name as label.
        """
        for f in self.nfs_filesystems_performance:
            self.throughput.add_metric(['nfs', f.name, 'read'], f.read_bytes_per_sec)
            self.throughput.add_metric(['nfs', f.name, 'write'], f.write_bytes_per_sec)

    def get_metrics(self):
        self._latency()
        self._iops()
        self._ops_size()
        self._throughput()
        yield self.latency
        yield self.iops
        yield self.ops_size
        yield self.throughput
