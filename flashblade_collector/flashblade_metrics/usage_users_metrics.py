from prometheus_client.core import GaugeMetricFamily


class UsageUsersMetrics():
    """
    Base class for FlashBlade Prometheus users quota metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.usage = None

    def _usage(self):
        """
        Create metrics of gauge type for users usage indicators.
        """
        self.usage = GaugeMetricFamily('purefb_filesystem_user_usage_bytes',
                                       'FlashBlade filesystem users usage',
                                       labels=['name', 'user_name', 'uid',
                                               'dimension'])
        for uu in self.fb.get_users_usage():
            uname = uu.user.name if uu.user.name is not None else ''
            uid = str(uu.user.id)
            self.usage.add_metric(
                    [uu.file_system.name, uname, uid, 'quota'], uu.quota if uu.quota is not None else 0)
            self.usage.add_metric(
                    [uu.file_system.name, uname, uid, 'usage'], uu.usage)

    def get_metrics(self):
        self._usage()
        yield self.usage
