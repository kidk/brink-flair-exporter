#!/usr/bin/env python3
import time
import random
from os import path
import yaml
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
import minimalmodbus
import math

class BrinkFlair(object):
    def __init__(self):
        self.instrument = minimalmodbus.Instrument ('/dev/ttyUSB0', 20) # port name, slave address (in decimal)

        self.instrument.serial.baudrate = 19200 # Baud
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = minimalmodbus.serial.PARITY_EVEN
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 0.5 # seconds
        self.instrument.mode = minimalmodbus.MODE_RTU # rtu or ascii mode
        self.instrument.clear_buffers_before_each_transaction = True

    def collect_gauge(self, name, description, value):
        gauge = GaugeMetricFamily(name, description)
        gauge.add_metric(['name'], value)
        return gauge

    def collect(self):
        value = self.instrument.read_register (8001, 0, 3, False)
        yield self.collect_gauge('brink_flair_power_level', 'The desired air flow rate (0 holiday, 1 low, 2 normal, 3 high)', value)
        switchPositionEnum = {0: 'holiday', 1: 'low', 2: 'normal', 3: 'high'}
        print ('brink_flair_power_level:', value, '(' + switchPositionEnum [value] + ')')

        value = self.instrument.read_register (4036, 0, 4, True) / 10
        yield self.collect_gauge('brink_flair_outside_temperature', 'Temperature sensor supply fan', value)
        print ('brink_flair_outside_temperature:', value, 'C')

        value = self.instrument.read_register (4037, 0, 4, True)
        yield self.collect_gauge('brink_flair_outside_humidity', 'Fan inlet sensor rel. humidity', value)
        print ('brink_flair_outside_humidity:', value, '%')

        value = self.instrument.read_register (4046, 0, 4, True) / 10
        yield self.collect_gauge('brink_flair_exhaust_temperature', 'Exhaust temperature', value)
        print ('brink_flair_exhaust_temperature:', value, 'C')

        value = self.instrument.read_register (4047, 0, 4, True)
        yield self.collect_gauge('brink_flair_exhaust_humidity', 'Exhaust humidity', value)
        print ('brink_flair_exhaust_humidity:', value, '%')

        value = self.instrument.read_register (4081, 0, 4, True) / 10
        yield self.collect_gauge('brink_flair_ntc1_temperature', 'NTC1 temperature', value)
        print ('brink_flair_ntc1_temperature:', value, 'C')

        value = self.instrument.read_register (4082, 0, 4, True) / 10
        yield self.collect_gauge('brink_flair_ntc2_temperature', 'NTC2 temperature', value)
        print ('brink_flair_ntc2_temperature:', value, 'C')

        value = self.instrument.read_register (4083, 0, 4, True)
        yield self.collect_gauge('brink_flair_rht_humidity', 'RHT humidity', value)
        print ('brink_flair_rht_humidity:', value, '%')

        value = self.instrument.read_register (4023, 0, 4, False) / 10
        yield self.collect_gauge('brink_flair_inlet_pressure', 'Inlet pressure', value)
        print ('brink_flair_inlet_pressure:', value, 'Pa')

        value = self.instrument.read_register (4024, 0, 4, False) / 10
        yield self.collect_gauge('brink_flair_outlet_pressure', 'Outlet pressure', value)
        print ('brink_flair_outlet_pressure:', value, 'Pa')

        value = self.instrument.read_register (4031, 0, 4, False)
        yield self.collect_gauge('brink_flair_inlet_air_volume_set', 'Inlet air volume set', value)
        print ('brink_flair_inlet_air_volume_set:', value, 'm3')

        value = self.instrument.read_register (4032, 0, 4, False)
        yield self.collect_gauge('brink_flair_inlet_air_volume_value', 'Inlet air volume value', value)
        print ('brink_flair_inlet_air_volume_value:', value, 'm3')

        value = self.instrument.read_register (4041, 0, 4, False)
        yield self.collect_gauge('brink_flair_output_air_volume_set', 'Outlet air volume set', value)
        print ('brink_flair_output_air_volume_set:', value, 'm3')

        value = self.instrument.read_register (4042, 0, 4, False)
        yield self.collect_gauge('brink_flair_output_air_volume_value', 'Outlet air valume value', value)
        print ('brink_flair_output_air_volume_value:', value, 'm3')

        value = self.instrument.read_register (6100, 0, 3, False)
        yield self.collect_gauge('brink_flair_bypass_mode', 'Bypass mode (0: automatic, 1: closed, 2: open)', value)
        bypassModeEnum = {0: 'automatic', 1: 'closed', 2: 'open'}
        print ('brink_flair_bypass_mode:', bypassModeEnum [value])

        value = self.instrument.read_register (4050, 0, 4, False)
        yield self.collect_gauge('brink_flair_bypass_state', 'Bypass state (0: initialize, 1: open, 2: closed, 3:open, 4:closed, 255:error)', value)
        bypassStateEnum = {0: 'initialize', 1: 'open', 2: 'closed', 3: 'open', 4: 'closed', 255: 'error'}
        print ('brink_flair_bypass_state:', bypassStateEnum [value])

        value = self.instrument.read_register (4100, 0, 4, False)
        yield self.collect_gauge('brink_flair_filter_status', 'Filter status (0: clean, 1: dirty', value)
        filterStateEnum = {0: 'clean', 1: 'dirty'}
        print ('Filter status:', filterStateEnum [value])

        # value = self.instrument.read_register (4060, 0, 4, False)
        # yield self.collect_gauge('brink_flair_outside_humidity', 'Outside humidity', value)
        # preheaterStateEnum = {0: 'initialize', 1: 'inactive', 2: 'active', 3: 'test mode'}
        # print ('Preheat status:', preheaterStateEnum [value])

        # value = self.instrument.read_register (4061, 0, 4, False)
        # yield self.collect_gauge('brink_flair_outside_humidity', 'Outside humidity', value)
        # print ('Preheat performance:', value, '%')

        # value = self.instrument.read_register (6033, 0, 3, False)
        # yield self.collect_gauge('brink_flair_outside_humidity', 'Outside humidity', value)
        # imbalanceEnum = {0: 'not allowed', 1: 'allowed'}
        # print ('Unbalanced:', imbalanceEnum [value])

        # value = self.instrument.read_register (6035, 0, 3, False)
        # yield self.collect_gauge('brink_flair_outside_humidity', 'Outside humidity', value)
        # print ('Supply unbalance:', value, '%')

        # value = self.instrument.read_register (6036, 0, 3, False)
        # yield self.collect_gauge('brink_flair_outside_humidity', 'Outside humidity', value)
        # print ('Deduction unbalance:', value, '%')

        # value = self.instrument.read_register (6000, 0, 3, False)
        # yield self.collect_gauge('brink_flair_flow_rate_absence', 'Outside humidity', value)
        # print ('Flow rate level 0 (absence):', value, 'm3')

        # value = self.instrument.read_register (6001, 0, 3, False)
        # yield self.collect_gauge('brink_flair_flow_rate_low', 'Outside humidity', value)
        # print ('Flow rate level 1 (low):', value, 'm3')

        # value = self.instrument.read_register (6002, 0, 3, False)
        # yield self.collect_gauge('brink_flair_flow_rate_middle', 'Outside humidity', value)
        # print ('Flow rate level 2 (middle):', value, 'm3')

        # value = self.instrument.read_register (6003, 0, 3, False)
        # yield self.collect_gauge('brink_flair_flow_rate_high', 'Outside humidity', value)
        # print ('Flow rate level 3 (high):', value, 'm3')

        value = self.instrument.read_register (4115, 0, 4, False)
        yield self.collect_gauge('brink_flair_filter_age', 'Filters used in hours', value)
        print ('brink_flair_filter_age:', value, 'hours')

if __name__ == "__main__":
    start_http_server(9000)
    REGISTRY.register(BrinkFlair())
    while True:
        # period between collection
        time.sleep(5)
