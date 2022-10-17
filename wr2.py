#!/usr/bin/python3

import solaredge_modbus


def get_wechselrichter2_power():
    try:
        inverter = solaredge_modbus.Inverter(host="wechselrichter2.heidler-peg.lan", port=1502)
        #inverter = solaredge_modbus.Inverter(host="10.130.0.191", port=1502)
        values = inverter.read_all()
        power = values['power_ac'] * 10**values['power_ac_scale']
        return power
    except:
        return 0

p2 = get_wechselrichter2_power()
print(p2)
