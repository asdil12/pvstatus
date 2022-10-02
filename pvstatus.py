#!/usr/bin/python3

import requests
import solaredge_modbus


def get_wechselrichter2_power():
	inverter = solaredge_modbus.Inverter(host="wechselrichter2", port=1502)
	#inverter = solaredge_modbus.Inverter(host="10.130.0.191", port=1502)
	values = inverter.read_all()
	power = values['power_ac'] * 10**values['power_ac_scale']
	return power


def get_wechselrichter1_power():
	try:
		res = requests.get("http://wechselrichter.heidler-peg.lan/solar_api/v1/GetPowerFlowRealtimeData.fcgi", timeout=3)
		j = res.json()
		p = int(j["Body"]["Data"]["Site"]["P_PV"])
	except:
		# eg. during night when it is powered off
		p = 0
	return p

def get_sonnenbatterie_status():
	s = requests.session()
	s.get('http://sonnenbatterie:8080/')
	s.post('http://sonnenbatterie:8080/login', data={'username': 'user', 'password': 'Sonnen2016'})
	j = s.get('http://sonnenbatterie:8080/api/v1/status').json()
	return {
		"consumption": j['Consumption_W'],
		"production": j['Production_W'],
		"battery_level": j['RSOC'],
		"battery_is_charging": j['BatteryCharging'],
		"battery_is_discharging": j['BatteryDischarging'],
		"battery_charging": j['Pac_total_W'] * -1,
		"grid_feedin": j['GridFeedIn_W'],
	}


p1 = get_wechselrichter1_power()
p2 = get_wechselrichter2_power()
sb = get_sonnenbatterie_status()

#sb = {'consumption': 570, 'production': 506, 'battery_level': 35, 'battery_is_charging': True, 'battery_is_discharging': False, 'battery_charging': 283, 'grid_feedin': 71}


print(p1)
print(p2)
print(sb)

bat = min(max(0, sb['battery_level']), 99)
cd = "CHR" if sb['battery_is_charging'] else '   '
cd = "DIS" if sb['battery_is_discharging'] else cd
cdr = "@% 5iW" % abs(sb['battery_charging']) if sb['battery_is_charging'] or sb['battery_is_discharging'] else '      '

g_io = 'GO' if sb['grid_feedin'] >= 0 else 'GI'


line1 = "WR1:% 6iW    Prod:" % p1
line2 = "WR2:% 6iW   % 5iW" % (p2, sb['production'])
line3 = "Bat:% 3i%% %s %s" % (bat, cd, cdr)
line4 = "C:% 6iW %s:% 6iW" % (sb['consumption'], g_io, abs(sb['grid_feedin']))


print('#'*22)
print('#'+line1+'#')
print('#'+line2+'#')
print('#'+line3+'#')
print('#'+line4+'#')
print('#'*22)
