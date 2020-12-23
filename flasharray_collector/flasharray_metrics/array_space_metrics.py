from prometheus_client.core import GaugeMetricFamily
from . import mappings


class ArraySpaceMetrics():
    """
    Base class for FlashArray Prometheus array space metrics
    """
    def __init__(self, fa):
        self.fa = fa
        self.data_reduction = GaugeMetricFamily('purefa_array_space_datareduction_ratio',
                                                'FlashArray overall data reduction',
                                                labels=['dimension'],
                                                unit='ratio')
        self.capacity = GaugeMetricFamily('purefa_array_space_capacity_bytes',
                                          'FlashArray overall space capacity',
                                          labels=['dimension'])
        self.provisioned = GaugeMetricFamily('purefa_array_space_provisioned_bytes',
                                             'FlashArray overall provisioned space',
                                             labels=['dimension'])
        self.used = GaugeMetricFamily('purefa_array_space_used_bytes',
                                      'FlashArray overall used space',
                                      labels=['dimension'])

    def _data_reduction(self):
        """
        Create metrics of gauge type for array data reduction.
        Metrics values can be iterated over.
        """
        for k in mappings.array_drr_mapping:
            self.data_reduction.add_metric(mappings.array_drr_mapping[k], 
                                           self.fa.get_array_elem(k) if self.fa.get_array_elem(k) is not None else 0)

    def _capacity(self):
        """
        Create metrics of gauge type for array capacity indicators.
        Metrics values can be iterated over.
        """
        for k in mappings.array_capacity_mapping:
            self.capacity.add_metric(mappings.array_capacity_mapping[k],
                                     self.fa.get_array_elem(k) if self.fa.get_array_elem(k) is not None else 0)

    def _provisioned(self):
        """
        Create metrics of gauge type for array provisioned space indicators.
        Metrics values can be iterated over.
        """
        for k in mappings.array_provisioned_mapping:
            self.provisioned.add_metric(mappings.array_provisioned_mapping[k],
                                        self.fa.get_array_elem(k) if self.fa.get_array_elem(k) is not None else 0)

    def _used(self):
        """
        Create metrics of gauge type for array used space indicators.
        Metrics values can be iterated over.
        """
        for k in mappings.array_used_mapping:
            self.used.add_metric(mappings.array_used_mapping[k],
                                 self.fa.get_array_elem(k) if self.fa.get_array_elem(k) is not None else 0)

    def get_metrics(self):
        self._data_reduction()
        self._capacity()
        self._provisioned()
        self._used()
        yield self.data_reduction
        yield self.capacity
        yield self.provisioned
        yield self.used
