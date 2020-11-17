import re
from prometheus_client.core import GaugeMetricFamily


class ArrayHardwareMetrics:

    def __init__(self, fa):
        self.fa = fa
        self.chassis_health = None
        self.controller_health = None
        self.component_health = None
        self.temperature = None
        self.temperature = None

    def _array_hardware_status(self):
        """Collect information about all system sensors."""
        data = self.fa.get_hardware_status()

        self.chassis_health = GaugeMetricFamily(
                                   'purefa_hardware_chassis_health',
                                   'FlashArray hardware chassis health status')
        self.controller_health = GaugeMetricFamily(
                                'purefa_hardware_controller_health',
                                'FlashArray hardware controller health status',
                                labels=['controller'])
        self.component_health = GaugeMetricFamily(
                                            'purefa_hardware_component_health',
                                 'FlashArray hardware component health status',
                                 labels=['chassis', 'controller', 'component',
                                         'index'])
        self.temperature = GaugeMetricFamily(
                                     'purefa_hardware_temperature_celsius',
                                     'FlashArray hardware temperature sensors',
                                     labels=['chassis', 'controller',
                                             'sensor'])
        self.power = GaugeMetricFamily(
            'purefa_hardware_power_volts',
            'FlashArray hardware power supply voltage',
            labels=['chassis', 'power_supply'])

        re_chassis = re.compile(r"^CH(\d+)$")
        re_controller = re.compile(r"^CT(\d+)$")
        re_component = re.compile(r"^(CH|CT)(\d+)\.([A-Z]+)([0-9]+)$")

        for comp in data:
            if (comp['status'] == 'not_installed'):
                continue
            component_name = comp['name']
            component_state = 1 if (comp['status'] == 'ok') else 0

            # Chassis
            if re.match(r"^CH\d+$", component_name):
                detail = re_chassis.match(component_name)
                c_index = detail.group(1)
                self.chassis_health.add_metric([c_index], component_state)
                continue
            # Controller
            elif re.match(r"^CT\d+$", component_name):
                detail = re_controller.match(component_name)
                c_index = detail.group(1)
                self.controller_health.add_metric([c_index], component_state)
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
                self.component_health.add_metric(
                    labels=labelset, value=component_state)

                if c_type.lower() == 'tmp':
                    # Additional metric for temperature
                    if c_base == 'CH':
                        self.temperature.add_metric(
                            [c_base_index, '', c_index], float(comp['temperature']))
                    else:
                        self.temperature.add_metric(
                            ['', c_base_index, c_index], float(comp['temperature']))
                elif c_type.lower() == 'pwr':
                    # Additional metric for voltage level
                    if comp['voltage'] is not None:
                        self.power.add_metric([c_base_index, c_index],
                                         float(comp['voltage']))

    def get_metrics(self):
        self._array_hardware_status()
        yield self.chassis_health
        yield self.controller_health
        yield self.component_health
        yield self.temperature
        yield self.power
