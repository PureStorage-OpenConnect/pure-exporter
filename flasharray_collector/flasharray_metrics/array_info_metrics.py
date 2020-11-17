from prometheus_client.core import InfoMetricFamily


class ArrayInfoMetrics():
    """
    Base class for FlashArray Prometheus array info
    """
    def __init__(self, fa):
        self.fa = fa
        self.info = None

    def _info(self):
        """Assemble a simple information metric defining the scraped system."""
        array = self.fa.get_array()

        self.info = InfoMetricFamily('purefa', 'FlashArray system information',
                                     value={
                                         'array_name': array['array_name'],
                                         'system_id': array['id'],
                                         'version': array['version'],
                                         'hostname': array['hostname']})

    def get_metrics(self):
        self._info()
        yield self.info
