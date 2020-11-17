from prometheus_client.core import GaugeMetricFamily


class PodStatusMetrics():
    """
    Base class for FlashArray Prometheus pod stattus metrics
    """

    def __init__(self, fa):
        self.fa = fa
        self.status = None

    def _status(self):
        """
        Create pods status metrics of gauge type, with pod name, array id and
        array name as label.
        Metrics values can be iterated over.
        """

        self.status = GaugeMetricFamily('purefa_pod_status',
                                        'FlashArray pod status',
                                        labels=['pod', 'array_id', 'array_name'])
        self.mediator_status = GaugeMetricFamily('purefa_pod_mediator_status',
                                                 'FlashArray pod mediatorstatus',
                                                 labels=['pod', 'array_id', 'array_name'])
        self.progress = GaugeMetricFamily('purefa_pod_progress_percent',
                                          'FlashArray pod synchronization status percentage',
                                          labels=['pod', 'array_id', 'array_name'])
        for p in self.fa.get_pods():
            arrays = p['arrays']
            self.status.add_metric([p['name'], arrays[0]['array_id'], arrays[0]['name']], 1 if arrays[0]['status'] == 'online' else 0)
            self.mediator_status.add_metric([p['name'], arrays[0]['array_id'], arrays[0]['name']], 1 if arrays[0]['mediator_status'] == 'online' else 0)
            if 'progress' in arrays[0]:
                self.progress.add_metric([p['name'], arrays[0]['array_id'], arrays[0]['name']], arrays[0]['progress'] if arrays[0]['progress'] is not None else 101)
            if len(arrays) == 1:
                continue
            self.status.add_metric([p['name'], arrays[1]['array_id'], arrays[1]['name']], 1 if arrays[1]['status'] == 'online' else 0)
            self.mediator_status.add_metric([p['name'], arrays[1]['array_id'], arrays[1]['name']], 1 if arrays[1]['mediator_status'] == 'online' else 0)
            if 'progress' in arrays[1]:
                self.progress.add_metric([p['name'], arrays[1]['array_id'], arrays[1]['name']], arrays[1]['progress'] if arrays[1]['progress'] is not None else 101)

    def get_metrics(self):
        self._status()
        yield self.status
        yield self.mediator_status
        yield self.progress
