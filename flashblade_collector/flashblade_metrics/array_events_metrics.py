from prometheus_client.core import GaugeMetricFamily


class ArrayEventsMetrics():
    """
    Base class for FlashBlade Prometheus events metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.events = GaugeMetricFamily('purefb_open_events_total',
                                        'FlashBlade number of open events',
                                        labels=['severity'])
        self.fb_events = fb.get_open_alerts()

    def _open_events(self):
        """
        Create a metric of gauge type for the number of open alerts:
        critical, warning and info, with the severity as label.
        """
        # Inrement each counter for each type of event
        c_crit, c_warn, c_info = 0, 0, 0
        for msg in self.fb_events:
            if msg.severity == 'critical':
                c_crit += 1
            if msg.severity == 'warning':
                c_warn += 1
            if msg.severity == 'info':
                c_info += 1
        self.events.add_metric(['critical'], c_crit)
        self.events.add_metric(['warning'], c_warn)
        self.events.add_metric(['info'], c_info)

    def get_metrics(self):
        self._open_events()
        yield self.events
