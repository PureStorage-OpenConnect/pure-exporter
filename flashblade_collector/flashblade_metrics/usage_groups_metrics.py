from prometheus_client.core import GaugeMetricFamily


class UsageGroupsMetrics():
    """
    Base class for FlashBlade Prometheus groups usage metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.usage = None

    def _usage(self):
        """
        Create metrics of gauge type for groups usage indicators.
        """
        self.usage = GaugeMetricFamily('purefb_filesystem_group_usage_bytes',
                                       'FlashBlade filesystem groups usage',
                                       labels=['name', 'group_name', 'gid',
                                               'dimension'])
        for gu in self.fb.get_groups_usage():
            grpname = gu.group.name if gu.group.name is not None else ''
            gid = str(gu.group.id)
            self.usage.add_metric(
                    [gu.file_system.name, grpname, gid, 'quota'], gu.quota if gu.quota is not None else 0)
            self.usage.add_metric(
                    [gu.file_system.name, grpname, gid, 'usage'], gu.usage)

    def get_metrics(self):
        self._usage()
        yield self.usage
