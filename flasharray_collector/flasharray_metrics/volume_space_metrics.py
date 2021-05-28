from prometheus_client.core import GaugeMetricFamily
import re


class VolumeSpaceMetrics():
    """
    Base class for FlashArray Prometheus volume space metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = GaugeMetricFamily('purefa_volume_space_datareduction_ratio',
                                                'FlashArray volumes data reduction ratio',
                                                labels=['volume', 'naaid', 'pod', 'vgroup'],
                                                unit='ratio')
        self.thin_provision = GaugeMetricFamily('purefa_volume_space_thinprovision_ratio',
                                                'FlashArray volumes data thin provision ratio',
                                                labels=['volume', 'naaid', 'pod', 'vgroup'],
                                                unit='ratio')
        self.size = GaugeMetricFamily('purefa_volume_space_size_bytes',
                                      'FlashArray volumes size',
                                      labels=['volume', 'naaid', 'pod', 'vgroup'])
        self.allocated = GaugeMetricFamily('purefa_volume_space_bytes',
                                           'FlashArray allocated space',
                                           labels=['volume', 'naaid', 'pod', 'vgroup', 'dimension'])

    def __split_vname(self, vname):
        p = re.compile(r'::')
        v_name = p.split(vname)
        if len(v_name) == 1:
            v_name = ['/'] + v_name
        return v_name

    def _data_reduction(self):
        """
        Create metrics of gauge type for volume data reduction
        Metrics values can be iterated over.
        """
        for v in self.fa.get_volumes():
            v_name = self.__split_vname(v['name'])
            self.data_reduction.add_metric([v_name[1], v['naaid'], v_name[0], v['vgroup']], v['data_reduction'] if v['data_reduction'] is not None else 0)

    def _thin_provision(self):
        for v in self.fa.get_volumes():
            v_name = self.__split_vname(v['name'])
            self._thin_provision.add_metric([v_name[1], v['naaid'], v_name[0], v['vgroup']], v['thin_provision'] if v['thin_provision'] is not None else 0)

    def _size(self):
        for v in self.fa.get_volumes():
            v_name = self.__split_vname(v['name'])
            self.size.add_metric([v_name[1], v['naaid'], v_name[0], v['vgroup']], v['size'] if v['size'] is not None else 0)

    def _allocated(self):
        for v in self.fa.get_volumes():
            v_name = self.__split_vname(v['name'])
            self.allocated.add_metric([v_name[1], v['naaid'], v_name[0], v['vgroup'], 'volumes'], v['volumes'] if v['volumes'] is not None else 0)
            self.allocated.add_metric([v_name[1], v['naaid'], v_name[0], v['vgroup'], 'snapshots'], v['snapshots'] if v['snapshots'] is not None else 0)
            self.allocated.add_metric([v_name[1], v['naaid'], v_name[0], v['vgroup'], 'total'], v['total'] if v['total'] is not None else 0)

    def get_metrics(self):
        self._data_reduction()
        self._size()
        self._allocated()
        yield self.data_reduction
        yield self.size
        yield self.allocated
