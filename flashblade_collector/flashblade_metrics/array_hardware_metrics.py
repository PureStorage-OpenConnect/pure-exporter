from prometheus_client.core import GaugeMetricFamily


class ArrayHardwareMetrics():
    """
    Base class for FlashBlade Prometheus hardware metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.hardware_status = GaugeMetricFamily('purefb_hw_status',
                                                 'Hardware components status',
                                                 labels=['hw_id'])
        self.fb_hardware_status = self.fb.get_hardware_status()

    def _hardware_status(self):
        """
        Create a metric of gauge type for components status,
        with the hardware component name as label.
        """
        for h in self.fb_hardware_status:
            name = h.name
            labels_v = [name]
            if h.status in ['unused', 'not_installed']:
                continue
            status = 1 if h.status in ['healthy'] else 0
            self.hardware_status.add_metric([h.name], status)

    def get_metrics(self):
        self._hardware_status()
        yield self.hardware_status
