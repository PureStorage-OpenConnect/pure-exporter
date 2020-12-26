from prometheus_client.core import GaugeMetricFamily


class BucketsReplicaMetrics():
    """
    Base class for FlashBlade Prometheus buckets replication metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.replica_links = GaugeMetricFamily(
                                       'purefb_bucket_replica_links_lag_msec',
                                       'FlashBlade bucket replica links lag',
                                       labels=['name',
                                               'direction',
                                               'remote_name',
                                               'remote_bucket_name',
                                               'remote_account',
                                               'status'])
        self.r_links = fb.get_bucket_replica_links()

    def _replica_links(self):
        """
        Create metrics of gauge type for bucket  indicators, with the
        account name and the bucket name as labels.
        """
        for l in self.r_links:
            self.replica_links.add_metric([l.local_bucket.name,
                                           l.direction,
                                           l.remote.name,
                                           l.remote_bucket.name, 
                                           l.remote_credentials.name,
                                           l.status], l.lag)

    def get_metrics(self):
        self._replica_links()
        yield self.replica_links
