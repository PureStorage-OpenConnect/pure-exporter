from prometheus_client.core import InfoMetricFamily


class ArrayInfoMetrics():
    """
    Base class for FlashBlade Prometheus array info
    """
    def __init__(self, fb):
        self.fb = fb
        self.info = None

    def _info(self):
        """Assemble a simple information metric defining the scraped system."""
        info = self.fb.get_array_info()

        self.info = InfoMetricFamily('purefb', 'FlashBlade system information',
                                     value={'array_name': info.name,
                                            'system_id': info.id,
                                            'os': info.os,
                                            'version': info.version
                                            })

    def get_metrics(self):
        self._info()
        yield self.info
