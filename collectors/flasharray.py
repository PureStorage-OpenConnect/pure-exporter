import re
import urllib3
import purestorage

# import third party modules
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

# disable ceritificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FlasharrayCollector:
    """
    Instantiates the collector's methods and properties to retrieve metrics
    from Puretorage Flasharray. Provides also a 'collect' method to allow
    Prometheus client registry to work as intended.

    :param target: IP address or domain name of the target array's management
                   interface.
    :type target: str
    :param api_token: API token of the user with which to log in.
    :type api_token: str
    """

    def __init__(self, target, api_token):
        self.connection = purestorage.FlashArray(
            target,
            api_token=api_token,
            user_agent='Purity_FA_Prometheus_exporter/1.0')

    def collect(self):
        """Global collector method for all the collected metrics."""
        yield from self.array_info()
        yield from self.array_hw()
        yield from self.array_events()
        yield from self.array_space()
        yield from self.array_perf()
        yield from self.vol_space()
        yield from self.vol_perf()

    def array_info(self):
        """Assemble a simple information metric defining the scraped system."""
        data = self.connection.get()

        yield InfoMetricFamily(
            'purefa',
            'FlashArray system information',
            value={
                'array_name': data['array_name'],
                'system_id': data['id'],
                'version': data['version']
            })

    def array_hw(self):
        """Collect information about all system sensors."""
        data = self.connection.list_hardware()

        chassis_health = GaugeMetricFamily(
            'purefa_hardware_chassis_health',
            'FlashArray hardware chassis health status')
        controller_health = GaugeMetricFamily(
            'purefa_hardware_controller_health',
            'FlashArray hardware controller health status',
            labels=['controller'])
        component_health = GaugeMetricFamily(
            'purefa_hardware_component_health',
            'FlashArray hardware component health status',
            labels=['chassis', 'controller', 'component', 'index'])
        temperature = GaugeMetricFamily(
            'purefa_hardware_temperature_celsius',
            'FlashArray hardware temperature sensors',
            labels=[
                'chassis',
                'controller',
                'sensor'])
        power = GaugeMetricFamily(
            'purefa_hardware_power_volts',
            'FlashArray hardware power supply voltage',
            labels=[
                'chassis',
                'power_supply'])

        re_chassis = re.compile(r"^CH(\d+)$")
        re_controller = re.compile(r"^CT(\d+)$")
        re_component = re.compile(r"^(CH|CT)(\d+)\.([A-Z]+)([0-9]+)$")

        for comp in data:
            component_name = comp['name']
            component_state = 1 if (comp['status'] == 'ok' or
                                    comp['status'] == 'not_installed') else 0

            # Chassis
            if re.match(r"^CH\d+$", component_name):
                detail = re_chassis.match(component_name)
                c_index = detail.group(0)
                chassis_health.add_metric([c_index], component_state)
                continue
            # Controller
            elif re.match(r"^CT\d+$", component_name):
                detail = re_controller.match(component_name)
                c_index = detail.group(0)
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
        data = self.connection.list_messages(open=True)
        events = GaugeMetricFamily('purefa_alerts_total',
                                   'Number of alert events',
                                   labels=['severity'])

        # Inrement each counter for each type of event
        c_crit, c_warn, c_info = 0, 0, 0
        for alert in data:
            if alert['current_severity'] == 'critical':
                c_crit += 1
            elif alert['current_severity'] == 'warning':
                c_warn += 1
            elif alert['current_severity'] == 'info':
                c_info += 1

        events.add_metric(['critical'], c_crit)
        events.add_metric(['warning'], c_warn)
        events.add_metric(['info'], c_info)

        yield events

    def array_space(self):
        """
        Create array space metrics of gauge type.
        Metrics values can be iterated over.
        """
        data = self.connection.get(space=True)[0]

        reduction = GaugeMetricFamily('purefa_space_datareduction_ratio',
                                      'FlashArray overall data reduction')
        capacity = GaugeMetricFamily('purefa_space_capacity_bytes',
                                     'FlashArray overall space capacity')
        provisioned = GaugeMetricFamily('purefa_space_provisioned_bytes',
                                        'FlashArray overall provisioned space')
        used = GaugeMetricFamily('purefa_space_used_bytes',
                                 'FlashArray overall used space',
                                 labels=['dimension'])

        reduction.add_metric([], data['data_reduction'])
        capacity.add_metric([], data['capacity'])
        provisioned.add_metric([], data['provisioned'])
        used.add_metric(['shared'], data['shared_space'])
        used.add_metric(['system'], data['system'])
        used.add_metric(['volumes'], data['volumes'])
        used.add_metric(['snapshots'], data['volumes'])

        yield capacity
        yield reduction
        yield provisioned
        yield used

    def array_perf(self):
        """
        Create array performance metrics of gauge type.
        Metrics values can be iterated over.
        """
        data = self.connection.get(action='monitor', mirrored=True)[0]
        labels = ['dimension']  # common labels

        latency = GaugeMetricFamily('purefa_performance_latency_usec',
                                    'FlashArray read latency',
                                    labels=labels)
        iops = GaugeMetricFamily('purefa_performance_iops',
                                 'FlashArray read IOPS',
                                 labels=labels)
        throughput = GaugeMetricFamily('purefa_performance_throughput_bytes',
                                       'FlashArray read throughput',
                                       labels=labels)
        latency_mirror_write = GaugeMetricFamily(
            'purefa_mirror_write_latency_usec',
            'FlashArray mirror write latency')
        iops_mirror_write = GaugeMetricFamily(
            'purefa_mirror_write_iops',
            'FlashArray mirror write IOPS')
        throughput_mirror_write = GaugeMetricFamily(
            'purefa_mirror_write_bytes',
            'FlashArray mirror write bandwidth')
        
        latency.add_metric(['read'], data['usec_per_read_op'])
        latency.add_metric(['write'], data['usec_per_write_op'])
        iops.add_metric(['read'], data['reads_per_sec'])
        iops.add_metric(['write'], data['writes_per_sec'])
        throughput.add_metric(['read'], data['output_per_sec'])
        throughput.add_metric(['write'], data['input_per_sec'])
        latency_mirror_write.add_metric([], data['usec_per_mirrored_write_op'])
        iops_mirror_write.add_metric([], data['mirrored_writes_per_sec'])
        throughput_mirror_write.add_metric([], data['mirrored_input_per_sec'])

        yield latency
        yield iops
        yield throughput
        yield latency_mirror_write
        yield iops_mirror_write
        yield throughput_mirror_write

    def vol_space(self):
        """
        Create volumes space metrics of gauge type, with the volume name
        as a label. Metrics values can be iterated over.
        """
        data = self.connection.list_volumes(space=True)

        datareduction = GaugeMetricFamily(
            'purefa_volume_datareduction_ratio',
            'FlashArray volume data reduction ratio',
            labels=['volume'],
            unit='ratio')
        size = GaugeMetricFamily('purefa_volume_size_bytes',
                                 'FlashArray volume size',
                                 labels=['volume'])
        allocated = GaugeMetricFamily('purefa_volume_space_bytes',
                                      'FlashArray volume allocated space',
                                      labels=['volume', 'dimension'])
        # Temporarily left out 'thin_provisioning' and 'total_reduction'
        for v in data:
            datareduction.add_metric([v['name']], v['data_reduction'])
            size.add_metric([v['name']], v['size'])
            allocated.add_metric([v['name'], 'volumes'], v['volumes'])
            allocated.add_metric([v['name'], 'snapshots'], v['snapshots'])
            allocated.add_metric([v['name'], 'shared'],
                                 v['shared'] if 'shared' in v else 0)
            allocated.add_metric([v['name'], 'system_space'],
                                 v['system_space'] if 'system_space' in v else 0)

            yield datareduction
            yield size
            yield allocated

    def vol_perf(self):
        """
        Create volumes performance metrics of gauge type, with
        volume name as label. Metrics values can be iterated over.
        """
        data = self.connection.list_volumes(action='monitor')
        labels = ['volume', 'dimension']  # common labels

        latency = GaugeMetricFamily('purefa_volume_latency_usec',
                                    'FlashArray volume IO latency',
                                    labels=labels)
        throughput = GaugeMetricFamily('purefa_volume_throughput_bytes',
                                       'FlashArray volume throughput',
                                       labels=labels)
        iops = GaugeMetricFamily('purefa_volume_iops',
                                 'FlashArray volume IOPS',
                                 labels=labels)
        for v in data:
            latency.add_metric([v['name'], 'read'], v['usec_per_read_op'])
            latency.add_metric([v['name'], 'write'], v['usec_per_write_op'])
            throughput.add_metric([v['name'], 'read'], v['output_per_sec'])
            throughput.add_metric([v['name'], 'write'], v['input_per_sec'])
            iops.add_metric([v['name'], 'read'], v['reads_per_sec'])
            iops.add_metric([v['name'], 'write'], v['writes_per_sec'])

            yield latency
            yield throughput
            yield iops
