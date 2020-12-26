from prometheus_client.core import GaugeMetricFamily


class FilesystemsSpaceMetrics():
    """
    Base class for FlashBlade Prometheus filesystem space metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.data_reduction = GaugeMetricFamily('purefb_filesystems_data_reduction',
                                                'FlashBlade filesystems data reduction',
                                                labels=['name'])
        self.space = GaugeMetricFamily('purefb_filesystems_space_bytes',
                                       'FlashBlade filesystems space',
                                       labels=['name', 'dimension'])
        self.filesystems = fb.get_filesystems()

    def _data_reduction(self):
        """
        Create metrics of gauge type for filesystems space indicators,
        with filesystem name as label.
        """
        for f in self.filesystems:
            self.data_reduction.add_metric([f.name], f.space.data_reduction if f.space.data_reduction is not None else 0)

    def _space(self):
        """
        Create metrics of gauge type for filesystems space indicators,
        with filesystem name as label.
        """
        for f in self.filesystems:
            self.space.add_metric([f.name, 'provisioned'], f.provisioned)
            self.space.add_metric([f.name, 'snapshots'], f.space.snapshots)
            self.space.add_metric([f.name, 'total_physical'], f.space.total_physical)
            self.space.add_metric([f.name, 'virtual'], f.space.virtual)
            self.space.add_metric([f.name, 'unique'], f.space.unique)

    def get_metrics(self):
        self._data_reduction()
        self._space()
        yield self.data_reduction
        yield self.space
