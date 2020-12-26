from prometheus_client.core import GaugeMetricFamily


class BucketsPerformanceMetrics():
    """
    Base class for FlashBlade Prometheus buckets performace metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.latency = GaugeMetricFamily('purefb_bucket_performance_latency_usec',
                                         'FlashBlade bucket latency',
                                         labels=['name', 'dimension'])
        self.throughput = GaugeMetricFamily('purefb_bucket_performance_throughput_bytes',
                                            'FlashBlade bucket throughput',
                                            labels=['name', 'dimension'])
        self.buckets_performance = self.fb.get_buckets_performance()

    def _latency(self):
        """
        Create metrics of gauge type for buckets performace latency, with the
        account name and the bucket name as labels.
        """
        for b in self.buckets_performance:
            self.latency.add_metric([b.name, 'read_buckets'], b.usec_per_read_bucket_op)
            self.latency.add_metric([b.name, 'read_objects'], b.usec_per_read_object_op)
            self.latency.add_metric([b.name, 'write_buckets'], b.usec_per_write_bucket_op)
            self.latency.add_metric([b.name, 'write_objects'], b.usec_per_write_object_op)
            self.latency.add_metric([b.name, 'other'], b.usec_per_other_op)

    def _throughput(self):
        """
        Create metrics of gauge type for buckets performace throughput, with
        the account name and the bucket name as labels.
        """
        for b in self.buckets_performance:
            self.throughput.add_metric([b.name, 'read_buckets'], b.read_buckets_per_sec)
            self.throughput.add_metric([b.name, 'read_objects'], b.read_objects_per_sec)
            self.throughput.add_metric([b.name, 'write_buckets'], b.write_buckets_per_sec)
            self.throughput.add_metric([b.name, 'write_objects'], b.write_objects_per_sec)
            self.throughput.add_metric([b.name, 'other'], b.others_per_sec)

    def get_metrics(self):
        self._latency()
        self._throughput()
        yield self.latency
        yield self.throughput
