from .flashblade_metrics.flashblade import FlashBlade
from .flashblade_metrics.array_info_metrics import ArrayInfoMetrics
from .flashblade_metrics.array_hardware_metrics import ArrayHardwareMetrics
from .flashblade_metrics.array_events_metrics import ArrayEventsMetrics
from .flashblade_metrics.array_space_metrics import ArraySpaceMetrics
from .flashblade_metrics.array_performance_metrics import ArrayPerformanceMetrics
from .flashblade_metrics.array_specific_performance_metrics import ArraySpecificPerformanceMetrics
from .flashblade_metrics.filesystems_space_metrics import FilesystemsSpaceMetrics
from .flashblade_metrics.filesystems_performance_metrics import FilesystemsPerformanceMetrics
from .flashblade_metrics.buckets_space_metrics import BucketsSpaceMetrics
from .flashblade_metrics.buckets_performance_metrics import BucketsPerformanceMetrics
from .flashblade_metrics.clients_performance_metrics import ClientsPerformanceMetrics
from .flashblade_metrics.buckets_replica_metrics import BucketsReplicaMetrics
from .flashblade_metrics.filesystems_replica_metrics import FilesystemsReplicaMetrics
from .flashblade_metrics.usage_users_metrics import UsageUsersMetrics
from .flashblade_metrics.usage_groups_metrics import UsageGroupsMetrics


class FlashbladeCollector():
    """
    Instantiates the collector's methods and properties to retrieve status,
    space occupancy and performance metrics from Puretorage FlasBlade.
    Provides also a 'collect' method to allow Prometheus client registry
    to work properly.
    :param target: IP address or domain name of the target array's management
                   interface.
    :type target: str
    :param api_token: API token of the user with which to log in.
    :type api_token: str
    """
    def __init__(self, endpoint, api_token, request='all'):
        # self.fb = PurityFb(endpoint, conn_timeo=ctimeo, read_timeo=rtimeo,
        #                    retries=retries)
        self.fb = FlashBlade(endpoint, api_token)
        self.request = request

    def collect(self):
        """Global collector method for all the collected array metrics."""
        if self.request in ['all', 'array']:
            yield from ArrayInfoMetrics(self.fb).get_metrics()
            yield from ArrayHardwareMetrics(self.fb).get_metrics()
            yield from ArrayEventsMetrics(self.fb).get_metrics()
            yield from ArrayPerformanceMetrics(self.fb).get_metrics()
            yield from ArraySpecificPerformanceMetrics(self.fb).get_metrics()
            yield from ArraySpaceMetrics(self.fb).get_metrics()
            yield from FilesystemsSpaceMetrics(self.fb).get_metrics()
            yield from BucketsSpaceMetrics(self.fb).get_metrics()
            yield from FilesystemsPerformanceMetrics(self.fb).get_metrics()
            yield from BucketsPerformanceMetrics(self.fb).get_metrics()
            yield from BucketsReplicaMetrics(self.fb).get_metrics()
            yield from FilesystemsReplicaMetrics(self.fb).get_metrics()
        if self.request in ['all', 'usage']:
            yield from UsageUsersMetrics(self.fb).get_metrics()
            yield from UsageGroupsMetrics(self.fb).get_metrics()
        if self.request in ['all', 'clients']:
            yield from ClientsPerformanceMetrics(self.fb).get_metrics()
