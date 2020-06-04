import urllib3
import six
from purity_fb import PurityFb, rest

# import third party modules
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FlashbladeCollector():
    """
    Instantiates the collector's methods and properties to retrieve status,
    space occupancy and performance metrics from Puretorage FlasBlade.
    Provides also a 'collect' method to allow Prometheus client registry
    to work properly.
    :param target: IP address or domain name of the target array's management
                   interface.
    :type target: str
    :param api_token: API token of the user with which to log in.
    :type api_token: str
    """
    def __init__(self, target, api_token, request = 'all'):
        # self.fb = PurityFb(endpoint, conn_timeo=ctimeo, read_timeo=rtimeo, retries=retries)
        self.fb = PurityFb(host=target)
        self.fb.disable_verify_ssl()
        self.fb._api_client.user_agent = 'Purity_FB_Prometheus_exporter/1.0'
        self.fb.request_timeout = urllib3.Timeout(connect=2.0, read=60.0)
        self.fb.login(api_token)
        self.request = request
        self.filesystems = self.fb.file_systems.list_file_systems()
        self.buckets = self.fb.buckets.list_buckets()


    def __del__(self):
        if self.fb is not None:
            self.fb.logout()

    def array_info(self):
        """Assemble a simple information metric defining the scraped system."""
        data = self.fb.arrays.list_arrays().items[0]

        yield InfoMetricFamily(
            'purefb',
            'FlashBlade system information',
            value={
                'array_name': data.name,
                'system_id': data.id,
                'os': data.os,
                'version': data.version
            })

    def array_hw(self):
        """
        Create a metric of gauge type for components status,
        with the hardware component name as label.
        Metrics values can be iterated over.
        """
        fb_hw = self.fb.hardware.list_hardware().items
        status = GaugeMetricFamily('purefb_hw_status',
                                   'Hardware components status',
                                   labels=['hw_id'])
        for h in fb_hw:
            state = h.status
            name = h.name
            labels_v = [name]
            if state == 'unused' or state == 'not_installed':
                continue
            elif state == 'healthy':
                status.add_metric(labels_v, 1)
            else:
                status.add_metric(labels_v, 0)
        yield status

    def array_hw(self):
        """Collect information about all system sensors."""
        data = self.fb.hardware.list_hardware().items

        chassis_health = GaugeMetricFamily(
            'purefb_hardware_chassis_health',
            'FlashBlade hardware chassis health status',
            labels=['chassis'])
        blade_health = GaugeMetricFamily(
            'purefb_hardware_blade_health',
            'FlashBlade hardware blade health status',
            labels=['chassis', 'flashmodule'])
        flashmodule_health = GaugeMetricFamily(
            'purefb_hardware_flashmodule_health',
            'FlashBlade hardware flashmodule health status',
            labels=['chassis', 'flashmodule'])
        component_health = GaugeMetricFamily(
            'purefa_hardware_component_health',
            'FlashArray hardware component health status',
            labels=['chassis', 'flashmodule', 'component', 'index'])
        power = GaugeMetricFamily(
            'purefa_hardware_power_volts',
            'FlashArray hardware power supply voltage',
            labels=['chassis', 'power_supply'])

        re_chassis = re.compile(r"^CH(\d+)$")
        re_blade = re.compile(r"^CH(\d+)\.FB(\d+)$")
        re_flashmodule = re.compile(r"^CH(\d+)\.FM(\d+)$")
        re_component = re.compile(r"^(CH|CT)(\d+)\.([A-Z]+)([0-9]+)$")

        for comp in data:
            if (comp.status == 'not_installed') or (comp.status == 'unused'):
                continue
            component_name = comp.name
            component_state = 1 if (comp.status == 'healthy') else 0

            # Chassis
            if re.match(r"^CH\d+$", component_name):
                detail = re_chassis.match(component_name)
                c_index = detail.group(1)
                chassis_health.add_metric([c_index], component_state)
                continue
            # Blade
            elif re.match(r"^CH\d+\.FB\d+$", component_name):
                detail = re_controller.match(component_name)
                c_index = detail.group(1)
                controller_health.add_metric([c_index], component_state)
            # FlashModule
            elif re.match(r"^CH\d+\.FM\d+$", component_name):
                detail = re_controller.match(component_name)
                c_index = detail.group(1)
                controller_health.add_metric([c_index], component_state)
                continue
            # Components
            elif re.match(r"^C(H|T)\d+\.[A-Z]+[0-9]+$", component_name):
                detail = re_component.match(component_name)
                c_base = detail.group(1)
                c_base_index = detail.group(2)
                c_type = detail.group(3)
                c_index = detail.group(4)

                if c_base == 'CH':
                    # Chassis-based
                    labelset = [c_base_index, '', c_type, c_index]
                else:
                    # Controller-based
                    labelset = ['', c_base_index, c_type, c_index]

                # Component health status
                component_health.add_metric(
                    labels=labelset, value=component_state)

                if c_type.lower() == 'tmp':
                    # Additional metric for temperature
                    if c_base == 'CH':
                        temperature.add_metric(
                            [c_base_index, '', c_index], float(comp['temperature']))
                    else:
                        temperature.add_metric(
                            ['', c_base_index, c_index], float(comp['temperature']))
                elif c_type.lower() == 'pwr':
                    # Additional metric for voltage level
                    if comp['voltage'] is not None:
                        power.add_metric([c_base_index, c_index],
                                         float(comp['voltage']))

        yield chassis_health
        yield controller_health
        yield component_health
        yield temperature
        yield power

    def array_events(self):
        """
        Create a metric of gauge type for the number of open alerts:
        critical, warning and info, with the severity as label.
        Metrics values can be iterated over.
        """
        fb_events = self.fb.alerts.list_alerts(filter="state='open'").items
        labels = ['severity']
        events = GaugeMetricFamily('purefb_open_events_total',
                                   'FlashBlade number of open events',
                                   labels=labels)

        # Inrement each counter for each type of event
        c_crit, c_warn, c_info = 0, 0, 0
        for msg in fb_events:
            if msg.severity == 'critical':
                c_crit += 1
            if msg.severity == 'warning':
                c_warn += 1
            if msg.severity == 'info':
                c_info += 1
        events.add_metric(['critical'], c_crit)
        events.add_metric(['warning'], c_warn)
        events.add_metric(['info'], c_info)
        yield events


    def array_space(self):
        """
        Create metrics of gauge type for array space indicators.
        Metrics values can be iterated over.
        """
        fb_space = self.fb.arrays.list_arrays_space().items[0]
        data_reduction = GaugeMetricFamily('purefb_array_space_data_reduction',
                                           'FlashBlade overall data reduction',
                                           labels=[])
        space = GaugeMetricFamily('purefb_array_space_bytes',
                                         'FlashBlade total space capacity',
                                         labels=['dimension'])
        data_reduction.add_metric([], fb_space.space.data_reduction)
        space.add_metric(['capacity'], fb_space.capacity)
        space.add_metric(['total_physical'], fb_space.space.total_physical)
        space.add_metric(['snapshots'], fb_space.space.snapshots)
        yield data_reduction
        yield space


    def buckets_space(self):
        """
        Create metrics of gauge type for buckets space indicators, with the
        account name and the bucket name as labels.
        Metrics values can be iterated over.
        """
        datareduction = GaugeMetricFamily('purefb_buckets_data_reduction',
                                        'FlashBlade buckets data reduction',
                                        labels=['account', 'name'])
        objcount = GaugeMetricFamily('purefb_buckets_object_count',
                                     'FlashBlade buckets objects counter',
                                     labels=['account', 'name'])
        space = GaugeMetricFamily('purefb_buckets_space_bytes',
                                  'FlashBlade buckets space',
                                  labels=['account', 'name', 'dimension'])
        for b in self.buckets.items:
            if b.space.data_reduction is None:
                b.space.data_reduction = 0
            datareduction.add_metric([b.account.name, b.name],
                                     b.space.data_reduction)
            objcount.add_metric([b.account.name, b.name], b.object_count)
            space.add_metric([b.account.name, b.name, 'snapshots'], b.space.snapshots)
            space.add_metric([b.account.name, b.name, 'total_physical'],
                               b.space.total_physical)
            space.add_metric([b.account.name, b.name, 'virtual'], b.space.virtual)
            space.add_metric([b.account.name, b.name, 'unique'], b.space.unique)
        yield datareduction
        yield objcount
        yield space

    def filesystems_space(self):
        """
        Create metrics of gauge type for filesystems space indicators,
        with filesystem name as label.
        Metrics values can be iterated over.
        """
        datareduction = GaugeMetricFamily('purefb_filesystems_data_reduction',
                                          'FlashBlade filesystems data reduction',
                                          labels=['name'])
        space = GaugeMetricFamily('purefb_filesystems_space_bytes',
                                  'FlashBlade filesystems space',
                                  labels=['name', 'dimension'])
        for f in self.filesystems.items:
            if f.space.data_reduction is None:
                f.space.data_reduction = 0
            datareduction.add_metric([f.name], f.space.data_reduction)
            space.add_metric([f.name, 'snapshots'], f.space.snapshots)
            space.add_metric([f.name, 'total_physical'], f.space.total_physical)
            space.add_metric([f.name, 'virtual'], f.space.virtual)
            space.add_metric([f.name, 'unique'], f.space.unique)
        yield datareduction
        yield space

    def array_perf(self):
        """
        Create array performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        protocols = ['http', 'nfs', 's3', 'smb']
        bpops = GaugeMetricFamily('purefb_array_performance_opns_bytes',
                                  'FlashBlade array average bytes per operations',
                                  labels=['protocol', 'dimension'])
        latency = GaugeMetricFamily('purefb_array_performance_latency_usec',
                                    'FlashBlade array latency',
                                    labels=['protocol', 'dimension'])
        iops = GaugeMetricFamily('purefb_array_performance_iops',
                                 'FlashBlade array IOPS',
                                 labels=['protocol', 'dimension'])
        throughput = GaugeMetricFamily('purefb_array_performance_throughput_bytes',
                                      'FlashBlade array throughput',
                                      labels=['protocol', 'dimension'])

        for proto in protocols:
            fb_perf = self.fb.arrays.list_arrays_performance(protocol=proto).items[0]

            bpops.add_metric([proto, 'per_op'], fb_perf.bytes_per_op)
            bpops.add_metric([proto, 'read'], fb_perf.bytes_per_read)
            bpops.add_metric([proto, 'write'], fb_perf.bytes_per_write)
            latency.add_metric([proto, 'read'], fb_perf.usec_per_read_op)
            latency.add_metric([proto, 'write'], fb_perf.usec_per_write_op)
            latency.add_metric([proto, 'other'], fb_perf.usec_per_other_op)
            iops.add_metric([proto, 'read'], fb_perf.reads_per_sec)
            iops.add_metric([proto, 'write'], fb_perf.writes_per_sec)
            iops.add_metric([proto, 'other'], fb_perf.others_per_sec)
            #iops.add_metric([proto, 'in'], fb_perf.input_per_sec)
            #iops.add_metric([proto, 'out'], fb_perf.output_per_sec)
            throughput.add_metric([proto, 'read'], fb_perf.read_bytes_per_sec)
            throughput.add_metric([proto, 'write'], fb_perf.write_bytes_per_sec)
        yield bpops
        yield latency
        yield iops
        yield throughput

    def filesystems_perf(self):
        """
        Create metrics of gauge type for filesystems performance indicators,
        with filesystem name as label.
        Metrics values can be iterated over.
        """

        bpops = GaugeMetricFamily('purefb_filesystem_performance_opns_bytes',
                                  'FlashBlade filesystem average bytes per operations',
                                  labels=['protocol', 'name', 'dimension'])
        latency = GaugeMetricFamily('purefb_filesystem_performance_latency_usec',
                                    'FlashBlade filesystem latency',
                                    labels=['protocol', 'name', 'dimension'])
        iops = GaugeMetricFamily('purefb_filesystem_performance_iops',
                                 'FlashBlade filesystem IOPS',
                                 labels=['protocol', 'name', 'dimension'])
        throughput = GaugeMetricFamily('purefb_filesystem_performance_throughput_bytes',
                                      'FlashBlade filesystem throughput',
                                      labels=['protocol', 'name', 'dimension'])
        for f in self.filesystems.items:
            if not f.nfs.enabled:
                continue
            fb_fs_perf = None
            try:
                fb_fs_perf = self.fb.file_systems.list_file_systems_performance(protocol='nfs',names=[f.name]).items[0]
            except Exception as e:
                continue
            bpops.add_metric(['nfs', f.name, 'per_op'], fb_fs_perf.bytes_per_op)
            bpops.add_metric(['nfs', f.name, 'read'], fb_fs_perf.bytes_per_read)
            bpops.add_metric(['nfs', f.name, 'write'], fb_fs_perf.bytes_per_write)
            latency.add_metric(['nfs', f.name, 'read'], fb_fs_perf.usec_per_read_op)
            latency.add_metric(['nfs', f.name, 'write'], fb_fs_perf.usec_per_write_op)
            latency.add_metric(['nfs', f.name, 'other'], fb_fs_perf.usec_per_other_op)
            iops.add_metric(['nfs', f.name, 'read'], fb_fs_perf.reads_per_sec)
            iops.add_metric(['nfs', f.name, 'write'], fb_fs_perf.writes_per_sec)
            iops.add_metric(['nfs', f.name, 'other'], fb_fs_perf.others_per_sec)
            throughput.add_metric(['nfs', f.name, 'read'], fb_fs_perf.read_bytes_per_sec)
            throughput.add_metric(['nfs', f.name, 'write'], fb_fs_perf.write_bytes_per_sec)

        yield bpops
        yield latency
        yield iops
        yield throughput

    def buckets_perf(self):
        """
        Create metrics of gauge type for buckets performace indicators, with the
        account name and the bucket name as labels.
        Metrics values can be iterated over.
        """
        latency = GaugeMetricFamily('purefb_bucket_performance_latency_usec',
                                    'FlashBlade bucket latency',
                                    labels=['name', 'dimension'])
        throughput = GaugeMetricFamily('purefb_bucket_performance_throughput_bytes',
                                       'FlashBlade bucket throughput',
                                       labels=['name', 'dimension'])

        for b in self.buckets.items:
            try:
                bperf = self.fb.buckets.list_buckets_s3_specific_performance(names=[b.name]).items[0]
            except Exception as e:
                continue
            #bperf = self.fb.buckets.list_buckets_performance(names=[b.name])
            latency.add_metric([b.name, 'read_buckets'], bperf.usec_per_read_bucket_op)
            latency.add_metric([b.name, 'read_objects'], bperf.usec_per_read_object_op)
            latency.add_metric([b.name, 'write_buckets'], bperf.usec_per_write_bucket_op)
            latency.add_metric([b.name, 'write_objects'], bperf.usec_per_write_object_op)
            latency.add_metric([b.name, 'other'], bperf.usec_per_other_op)
            throughput.add_metric([b.name, 'read_buckets'], bperf.read_buckets_per_sec)
            throughput.add_metric([b.name, 'read_objects'], bperf.read_objects_per_sec)
            throughput.add_metric([b.name, 'write_buckets'], bperf.write_buckets_per_sec)
            throughput.add_metric([b.name, 'write_objects'], bperf.write_objects_per_sec)
            throughput.add_metric([b.name, 'other'], bperf.others_per_sec)

        yield latency
        yield throughput

    def clientperf(self):
        """
        Create metrics of gauge type for client performance metrics.
        Metrics values can be iterated over.
        """
        fb_clientperf = self.fb.arrays.list_clients_performance()
        bpops = GaugeMetricFamily('purefb_client_performance_opns_bytes',
                                  'FlashBlade client average bytes per operations',
                                  labels=['name', 'port', 'dimension'])
        latency = GaugeMetricFamily('purefb_client_performance_latency_usec',
                                    'FlashBlade latency',
                                    labels=['name', 'port', 'dimension'])
        iops = GaugeMetricFamily('purefb_client_performance_iops',
                                 'FlashBlade IOPS',
                                 labels=['name', 'port', 'dimension'])
        throughput = GaugeMetricFamily('purefb_client_performance_throughput_bytes',
                                       'FlashBlade client_throughput',
                                       labels=['name', 'port', 'dimension'])

        for cperf in fb_clientperf.items:
            client, port = cperf.name.split(':')
            bpops.add_metric([client, port, 'per_op'], cperf.bytes_per_op)
            bpops.add_metric([client, port, 'read'], cperf.bytes_per_read)
            bpops.add_metric([client, port, 'write'], cperf.bytes_per_write)
            iops.add_metric([client, port, 'read'], cperf.reads_per_sec)
            iops.add_metric([client, port, 'write'], cperf.writes_per_sec)
            iops.add_metric([client, port, 'other'], cperf.others_per_sec)
            latency.add_metric([client, port, 'read'], cperf.usec_per_read_op)
            latency.add_metric([client, port, 'write'], cperf.usec_per_write_op)
            latency.add_metric([client, port, 'other'], cperf.usec_per_other_op)
            throughput.add_metric([client, port, 'read'], cperf.read_bytes_per_sec)
            throughput.add_metric([client, port, 'write'], cperf.write_bytes_per_sec)

        yield bpops
        yield latency
        yield iops
        yield throughput

    def collect(self):
        """Global collector method for all the collected array metrics."""
        if (self.request == 'all' or self.request == 'array'):
            yield from self.array_info()
            yield from self.array_hw()
            yield from self.array_events()
            yield from self.array_perf()
            yield from self.array_space()
            yield from self.filesystems_space()
            yield from self.buckets_space()
            yield from self.filesystems_perf()
            yield from self.buckets_perf()
        if (self.request == 'all' or self.request == 'clients'):
            yield from self.clientperf()
