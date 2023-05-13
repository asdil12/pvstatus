#!/usr/bin/python3

import os
import requests
import solaredge_modbus
import lcd_i2c
import time
import subprocess


def get_wechselrichter2_power():
    try:
        inverter = solaredge_modbus.Inverter(host="wechselrichter2.heidler-peg.lan", port=1502)
        #inverter = solaredge_modbus.Inverter(host="10.130.0.191", port=1502)
        values = inverter.read_all()
        power = values['power_ac'] * 10**values['power_ac_scale']
        return power
    except:
        return 0


def get_wechselrichter1_power():
    try:
        res = requests.get("http://wechselrichter.heidler-peg.lan/solar_api/v1/GetPowerFlowRealtimeData.fcgi", timeout=3)
        j = res.json()
        return int(j["Body"]["Data"]["Site"]["P_PV"])
    except:
        return 0

def get_sonnenbatterie_status():
	s = requests.session()
	#s.get('http://sonnenbatterie.heidler-peg.lan:8080/')
	#s.post('http://sonnenbatterie.heidler-peg.lan:8080/login', data={'username': 'user', 'password': 'Sonnen2016'})
	#j = s.get('http://sonnenbatterie.heidler-peg.lan:8080/api/v1/status').json()
	j = s.get('http://sonnenbatterie.heidler-peg.lan/api/v2/status').json()
	return {
		"consumption": j['Consumption_W'],
		"production": j['Production_W'],
		"battery_level": j['RSOC'],
		"battery_is_charging": j['BatteryCharging'],
		"battery_is_discharging": j['BatteryDischarging'],
		"battery_charging": j['Pac_total_W'] * -1,
		"grid_feedin": j['GridFeedIn_W'],
	}

lcd_i2c.lcd_init()

while True:
    p1 = get_wechselrichter1_power()
    #p2 = get_wechselrichter2_power()
    p2 = int(subprocess.check_output([os.path.join(os.path.dirname(__file__), "wr2.py")]))
    sb = get_sonnenbatterie_status()

    #sb = {'consumption': 570, 'production': 506, 'battery_level': 35, 'battery_is_charging': True, 'battery_is_discharging': False, 'battery_charging': 283, 'grid_feedin': 71}
    #sb = {'consumption': 0, 'production': p1+p2, 'battery_level': 0, 'battery_is_charging': False, 'battery_is_discharging': False, 'battery_charging': 0, 'grid_feedin': 0}


    print(f"{p1=}")
    print(f"{p2=}")
    print(f"{sb=}")

    bat = min(max(0, sb['battery_level']), 99)
    cd = "CHR" if sb['battery_is_charging'] else '   '
    cd = "DIS" if sb['battery_is_discharging'] else cd
    cdr = "@% 5iW" % abs(sb['battery_charging']) if sb['battery_is_charging'] or sb['battery_is_discharging'] else '       '

    g_io = 'GO' if sb['grid_feedin'] >= 0 else 'GI'


    line1 = "WR1:% 6iW    Prod:" % p1
    line2 = "WR2:% 6iW  % 6iW" % (p2, sb['production'])
    line3 = "%s:% 6iW C:% 6iW" % (g_io, abs(sb['grid_feedin']), sb['consumption'])
    line4 = "Bat:% 3i%% %s %s" % (bat, cd, cdr)


    print('#'*22)
    print('#'+line1+'#')
    print('#'+line2+'#')
    print('#'+line3+'#')
    print('#'+line4+'#')
    print('#'*22)

    lcd_i2c.lcd_string(line1, lcd_i2c.LCD_LINE_1)
    lcd_i2c.lcd_string(line2, lcd_i2c.LCD_LINE_2)
    lcd_i2c.lcd_string(line3, lcd_i2c.LCD_LINE_3)
    lcd_i2c.lcd_string(line4, lcd_i2c.LCD_LINE_4)

    time.sleep(0.2)
