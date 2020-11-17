from prometheus_client.core import GaugeMetricFamily


class ArrayPerformanceMetrics():
    """
    Base class for FlashArray Prometheus array performance metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.latency = None
        self.bandwidth = None
        self.iops = None
        self.avg_bsz = None
        self.qdepth = None

    def _latency(self):
        """
        Create array latency performance metrics of gauge type.
        Metrics values can be iterated over.
        """

        array = self.fa.get_array() 
        self.latency = GaugeMetricFamily('purefa_array_performance_latency_usec',
                                         'FlashArray latency',
                                         labels=['dimension'])
        self.latency.add_metric(['read'], array['usec_per_read_op'])
        self.latency.add_metric(['write'], array['usec_per_write_op'])
        self.latency.add_metric(['mirrored_write'], array['usec_per_mirrored_write_op'])
        self.latency.add_metric(['local_queue'], array['local_queue_usec_per_op'])
        self.latency.add_metric(['san_read'], array['san_usec_per_read_op'])
        self.latency.add_metric(['san_write'], array['san_usec_per_write_op'])
        self.latency.add_metric(['san_mirrored_write'], array['san_usec_per_mirrored_write_op'])
        self.latency.add_metric(['queue_read'], array['queue_usec_per_read_op'])
        self.latency.add_metric(['queue_write'], array['queue_usec_per_write_op'])
        self.latency.add_metric(['queue_mirrored_write'], array['queue_usec_per_mirrored_write_op'])
        self.latency.add_metric(['qos_read'], array['qos_rate_limit_usec_per_read_op'])
        self.latency.add_metric(['qos_write'], array['qos_rate_limit_usec_per_write_op'])
        self.latency.add_metric(['qos_mirrored'], array['qos_rate_limit_usec_per_mirrored_write_op'])

    def _bandwidth(self):
        """
        Create array bandwidth performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        array = self.fa.get_array() 
        self.bandwidth = GaugeMetricFamily('purefa_array_performance_bandwidth_bytes',
                                           'FlashArray bandwidth',
                                           labels=['dimension'])
        self.bandwidth.add_metric(['read'], array['output_per_sec'])
        self.bandwidth.add_metric(['write'], array['input_per_sec'])
        self.bandwidth.add_metric(['mirrored_write'], array['mirrored_input_per_sec'])

    def _iops(self):
        """
        Create array iops performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        array = self.fa.get_array() 
        self.iops = GaugeMetricFamily('purefa_array_performance_iops',
                                      'FlashArray IOPS',
                                      labels=['dimension'])
        self.iops.add_metric(['read'], array['reads_per_sec'])
        self.iops.add_metric(['write'], array['writes_per_sec'])
        self.iops.add_metric(['mirrored_write'], array['mirrored_writes_per_sec'])

    def _avg_block_size(self):
        """
        Create array average block size performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        array = self.fa.get_array() 
        self.avg_bsz = GaugeMetricFamily('purefa_array_performance_avg_block_bytes',
                                         'FlashArray avg block size',
                                         labels=['dimension'])
        self.avg_bsz.add_metric(['read'], array['bytes_per_read'])
        self.avg_bsz.add_metric(['write'], array['bytes_per_write'])
        self.avg_bsz.add_metric(['mirrored_write'], array['bytes_per_mirrored_write'])

    def _qdepth(self):
        """
        Create array queue depth performance metric of gauge type.
        Metrics values can be iterated over.
        """
        array = self.fa.get_array() 
        self.qdepth = GaugeMetricFamily('purefa_array_performance_qdepth',
                                        'FlashArray queue depth',
                                        labels=[])
        self.qdepth.add_metric([], array['queue_depth'] if array['queue_depth'] is not None else 0)


    def get_metrics(self):
        self._latency()
        self._bandwidth()
        self._iops()
        self._avg_block_size()
        self._qdepth()
        yield self.latency
        yield self.bandwidth
        yield self.iops
        yield self.avg_bsz
        yield self.qdepth
