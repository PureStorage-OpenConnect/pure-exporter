from prometheus_client.core import GaugeMetricFamily


class FilesystemsReplicaMetrics():
    """
    Base class for FlashBlade Prometheus filesystem replica link metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.replica_links_lag = None

    def _replica_links_lag(self):
        """
        Create metrics of gauge type for filesystem replica link lag, with the
        local filesystem name, replication direction, remote array name,
        remote filesystem name and replication status  as labels.
        """
        self.replica_links_lag = GaugeMetricFamily(
                                   'purefb_bucket_filesystems_links_lag_msec',
                                   'FlashBlade bucket filesystem links lag',
                                   labels=['name', 'direction', 'remote_name',
                                           'remote_filesystem_name', 'status'])
        for f in self.fb.get_filesystem_replica_links():
            self.replica_links_lag.add_metric([f.local_file_system.name,
                                               f.direction,
                                               f.remote.name,
                                               f.remote_file_system.name,
                                               f.status], f.lag)

    def get_metrics(self):
        self._replica_links_lag()
        yield self.replica_links_lag
