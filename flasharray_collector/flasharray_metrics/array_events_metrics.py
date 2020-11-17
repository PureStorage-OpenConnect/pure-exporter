from prometheus_client.core import GaugeMetricFamily


class ArrayEventsMetrics():
    """
    Base class for FlashArray Prometheus events metrics
    """
    def __init__(self, fa):
        self.fa = fa
        self.open_events = None

    def _open_events(self):
        """
        Create a metric of gauge type for the number of open alerts:
        critical, warning and info, with the severity as label.
        Metrics values can be iterated over.
        """
        self.open_events = GaugeMetricFamily('purefa_alerts_total',
                                             'Number of alert events',
                                             labels=['severity'])

        # Inrement each counter for each type of event
        c_crit, c_warn, c_info = 0, 0, 0
        for alert in self.fa.get_open_alerts():
            if alert['current_severity'] == 'critical':
                c_crit += 1
            elif alert['current_severity'] == 'warning':
                c_warn += 1
            elif alert['current_severity'] == 'info':
                c_info += 1

        self.open_events.add_metric(['critical'], c_crit)
        self.open_events.add_metric(['warning'], c_warn)
        self.open_events.add_metric(['info'], c_info)

    def get_metrics(self):
        self._open_events()
        yield self.open_events
