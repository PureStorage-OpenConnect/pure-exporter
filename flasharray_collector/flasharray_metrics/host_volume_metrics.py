from prometheus_client.core import GaugeMetricFamily


class HostVolumeMetrics():
    """
    Base class for mapping FlashArray hosts to connected volumes
    """

    def __init__(self, fa):
        self.fa = fa
        self.map_host_vol = GaugeMetricFamily('purefa_host_volumes_info',
                                              'FlashArray host volumes connections',
                                              labels=['host', 'naaid'])

    def _map_host_vol(self):
        for hv in self.fa.get_host_volumes():
            self.map_host_vol.add_metric([hv['host'], hv['naaid']], 1)



    def get_metrics(self):
        self._map_host_vol()
        yield self.map_host_vol