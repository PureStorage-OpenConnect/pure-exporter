import re
from prometheus_client.core import GaugeMetricFamily


class ArrayHardwareMetrics():
    """
    Base class for FlashBlade Prometheus hardware metrics
    """
    def __init__(self, fb):
        self.fb = fb
        self.chassis_health = None
        self.fb_health = None
        self.fm_health = None
        self.fmcomponent_health = None
        self.power_health = None

### NOT YET IMPLEMENTED
#        self.xfm_health = None
#        self.xfmcomponent_health = None
#        self.temperature = None
#        self.power = None

    def _array_hardware_status(self):
        """
        Create metric of gauge types for components status.

        WARNING: I do not have an External Fabric Module(xfm) to test against. 
                 On my test system all component have a termperature field, but
                    they all report None.
                 Those sections are commented out.
        """
        data = self.fb.get_hardware_status()

        self.hardware_status = GaugeMetricFamily(
                               'purefb_hw_status',
                               'Hardware components status',
                               labels=['model','name','serial','type'])

        self.chassis_health = GaugeMetricFamily(
                              'purefb_hardware_chassis_health',
                              'FlashBlade hardware chassis health status',
                              labels=['index','name','serial'])
        self.flashblade_health = GaugeMetricFamily(
                                 'purefb_hardware_flashblade_health',
                                 'FlashBlade hardware flashblade health status',
                                 labels=['chassis','model','name','serial','slot'])
        self.fabricmodule_health = GaugeMetricFamily(
                                   'purefb_hardware_fabricmodule_health',
                                   'FlashBlade hardware fabric module health status',
                                   labels=['chassis','model', 'name', 'serial', 'slot'])
        self.fmcomponent_health = GaugeMetricFamily(
                                  'purefb_hardware_fmcomponent_health',
                                  'FlashBlade hardware fabric module component health status',
                                  labels=['chassis', 'fabricmodule', 'model', 'name', 'serial', 'slot', 'type'])
        self.power_health = GaugeMetricFamily(
                            'purefb_hardware_power_health',
                            'FlashBlade hardware power health status',
                             labels=['chassis', 'model', 'name', 'serial', 'slot'])

### NOT YET IMPLEMENTED
#        self.xfabricmodule_health = GaugeMetricFamily(
#                                      'purefb_hardware_extfabricmodule_health',
#                                      'FlashBlade hardware external fabric module health status',
#                                      labels=['model', 'name', 'serial'])

#        self.xfmcomponent_health = GaugeMetricFamily(
#                                   'purefb_hardware_fmcomponent_health',
#                                   'FlashBlade hardware fabric module component health status',
#                                   labels=['fabricmodule', 'component', 'index'])


# Leaving commented out as there is a temperature field for each component but it's currently empty.
#   Hopefully this means in the future we get temperature and this can be completed correctly
#        self.temperature = GaugeMetricFamily(
#                           'purefb_hardware_temperature_celsius',
#                           'FlashBlade hardware temperature sensors',
#                           labels=['model', 'name', 'serial', 'type'])

# Leaving this commented out, currently there is not a way to pull voltage used
#        self.power = GaugeMetricFamily(
#            'purefb_hardware_power_volts',
#            'FlashBlade hardware power supply voltage',
#            labels=['chassis', 'power_supply'])

        re_fb = re.compile(r"^(CH\d+)\.(FB[0-9]+)$")
        re_fm = re.compile(r"^(CH\d+)\.(FM[0-9]+)$")
        re_xfm = re.compile(r"^(CH\d+)\.(XFM[0-9]+)$")
        re_fmcomponent = re.compile(r"^(CH\d+)\.(FM\d+)\.([A-Z]+)([0-9]+)$")
        re_pwr = re.compile(r"^(CH\d+)\.(PWR[0-9]+)$")

        for comp in data:
            if comp.status in ['unused', 'not_installed']:
                continue
            component_name = comp.name
            component_state = 1 if comp.status in ['healthy'] else 0
            component_type = comp.type

            # Simple component health metric
            self.hardware_status.add_metric([comp.model or '',comp.name,comp.serial or '',comp.type], component_state)

            # Types are per https://purity-fb.readthedocs.io/en/latest/Hardware/
            # Chassis
            if component_type == 'ch':
                self.chassis_health.add_metric([str(comp.index), comp.name, comp.serial or ''], component_state)
                continue

            # Flash Blade
            elif component_type == 'fb':
                detail = re_fb.match(component_name)
                chassis = detail.group(1)
                self.flashblade_health.add_metric([chassis, comp.model or '', comp.name, comp.serial or '', str(comp.slot)], component_state)
                continue

            # Fabric Modue or External Fabric Module
            elif component_type == 'fm':
                detail = re_fm.match(component_name)
                chassis = detail.group(1)
                self.fabricmodule_health.add_metric([chassis, comp.model or '', comp.name, comp.serial or '', str(comp.slot)], component_state)
                continue

#            # External Fabric Module
#            elif component_type == 'xfm':
#                detail = re_xfm.match(component_name)
#                chassis = detail.group(1)
#                self.xfabricmodule_health.add_metric([chassis, comp.model or '', comp.name, comp.serial or ''], component_state)
#                continue

            # FM Components
            elif re.match(r"^CH\d+\.FM\d+\.[A-Z]+[0-9]+$", component_name):
                detail = re_fmcomponent.match(component_name)
                chassis = detail.group(1)
                fabricmodule = detail.group(1)+'.'+detail.group(2)

                # Component health status
                self.fmcomponent_health.add_metric([chassis, fabricmodule, comp.model or '', comp.name, comp.serial or '', str(comp.slot) or '', comp.type], component_state) 

            # Power
            elif component_type == 'pwr':
                detail = re_pwr.match(component_name)
                chassis = detail.group(1)
                self.power_health.add_metric([chassis, comp.model or '', comp.name, comp.serial or '', str(comp.slot)], component_state)
                continue

    def get_metrics(self):
        self._array_hardware_status()
        yield self.hardware_status
        yield self.chassis_health
        yield self.flashblade_health
        yield self.fabricmodule_health
        yield self.fmcomponent_health
        yield self.power_health

### NOT YET IMPLEMENTED
#        yield self.xfm_health
#        yield self.temperature
#        yield self.power
