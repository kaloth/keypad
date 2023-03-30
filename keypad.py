import serial
import time
import keyboard
import json
import os
import weakref
import pywintypes
import win32file
import argparse
import msvcrt
from threading import Thread
import win32gui, win32process, psutil

def active_window_process_name():
    try:
        pid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
        return(psutil.Process(pid[-1]).name())
    except:
        return None

class SharedFile:
	def open_for_read(self, path):
		try:
			fhandle = self.fhandle = win32file.CreateFile(
				path,
				win32file.GENERIC_READ,
				win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_DELETE,
				None,
				win32file.OPEN_EXISTING,
				win32file.FILE_ATTRIBUTE_NORMAL,
				None)

			self._closer = weakref.ref(
				self, lambda x: win32file.CloseHandle(fhandle))

			self.write_enabled = False
			return open(msvcrt.open_osfhandle(fhandle.Detach(), os.O_TEXT | os.O_RDONLY), 'r')

		except pywintypes.error as e:
			raise IOError("Unable to open %s: %s" % (path, e)) 
		
	#def open_for_write(self, path):
	#	try:
	#		fhandle = self.fhandle = win32file.CreateFile(
	#			path,
	#			win32file.GENERIC_READ | win32file.GENERIC_WRITE,
	#			win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
	#			None,
	#			win32file.OPEN_EXISTING,
	#			win32file.FILE_ATTRIBUTE_NORMAL,
	#			None)
	#		
	#		self.write_enabled = True
	#		self._closer = weakref.ref(
	#			self, lambda x: win32file.CloseHandle(fhandle))
	#
	#		return fhandle
	#
	#	except pywintypes.error as e:
	#		raise IOError("Unable to open %s: %s" % (path, e))

elite_status_map = {
	0  : "Docked (on a landing pad)",
	1  : "Landed (on planet surface)",
	2  : "Landing Gear Down",
	3  : "Shields Up",
	4  : "Supercruise",
	5  : "FlightAssist Off",
	6  : "Hardpoints Deployed",
	7  : "In Wing",
	8  : "LightsOn",
	9  : "Cargo Scoop Deployed",
	10 : "Silent Running",
	11 : "Scooping Fuel",
	12 : "Srv Handbrake",
	13 : "Srv using Turret view",
	14 : "Srv Turret retracted (close to ship)",
	15 : "Srv DriveAssist",
	16 : "Fsd MassLocked",
	17 : "Fsd Charging",
	18 : "Fsd Cooldown",
	19 : "Low Fuel ( < 25% )",
	20 : "Over Heating ( > 100% )",
	21 : "Has Lat Long",
	22 : "IsInDanger",
	23 : "Being Interdicted",
	24 : "In MainShip",
	25 : "In Fighter",
	26 : "In SRV",
	27 : "Hud in Analysis mode",
	28 : "Night Vision",
}

class StatusService:
	def register(self, driver):
		# Register this StatusService with the keypad driver.
		pass
	
	def get_light_state(self, ident):
		# Map an light to a status in some external system. Then return it's value (0 or 1).
		pass
	
	def set_key_state(self, ident, value):
		# Map an key to a status in some external system. Then set it's value (0 or 1).
		pass

class DebugStatusService(StatusService):
	def __init__(self):
		pass
	
	def register(self, driver):
		# Register this StatusService with the keypad driver.
		self.driver = driver
		driver.register_key_service(self, ['debug'])
	
	def set_key_state(self, key, value):
		print('\tkey[' + str(key['idx']) + '] = ' + str(value))

class DefaultStatusService(StatusService):
	def __init__(self):
		pass
	
	def register(self, driver):
		# Register this StatusService with the keypad driver.
		self.driver = driver
		driver.register_light_service(self, ['always', 'never', 'pattern'])
		driver.register_key_service(self, ['default', 'hw_toggle', 'sw_toggle', 'press_release_ud', 'press_release_u', 'press_release_d'])
	
	def get_light_state(self, light):
		# Map an light to a status in some external system. Then return it's value (0 or 1).
		if light['type'] == 'always':
			return 1
		elif light['type'] == 'never':
			return 0
		elif light['type'] == 'pattern':
			tok = light['pattern'][int(time.time()*8.0) % len(light['pattern'])] if 'pattern' in light else '#'
			return 1 if tok == '#' else 0
	
	def set_key_state(self, key, value):
		# Map an key to a status in some external system. Then set it's value (0 or 1).
		key['state'] = value
		
		if key['type'] in ['default', 'hw_toggle']:
			if value == 1:
				self.driver.press(key)
			else:
				self.driver.release(key)
		elif key['type'] == 'press_release_ud':
			self.driver.press_and_release(key)
		elif key['type'] == 'press_release_u' and value == 0:
			self.driver.press_and_release(key)
		elif key['type'] == 'press_release_d' and value == 1:
			self.driver.press_and_release(key)
		elif key['type'] == 'sw_toggle' and value == 0:
			if not 'toggle_count' in key:
				key['toggle_count'] = 1
			else:
				key['toggle_count'] += 1
			if key['toggle_count'] % 2 == 0:
				self.driver.press(key)
			else:
				self.driver.release(key)

class EliteDangerousStatusService(StatusService):
	def __init__(self):
		self.esmask = 0
		self.esmask_date = None
		self.key_state_dirty = True
		
		self.es_thread = Thread(target=self.sync_elite_status, args=(False, ), daemon=True)
		self.es_thread.start()
	
	def register(self, driver):
		# Register this StatusService with the keypad driver.
		self.driver = driver
		driver.register_light_service(self, ['elite_dangerous_status'])
		driver.register_key_service(self, ['elite_dangerous_autotoggle'])
	
	def get_light_state(self, light):
		# Map an light to a status in some external system. Then return it's value (0 or 1).
		state = ((self.esmask >> abs(light['edstatus'])) & 1)
		if state:
			tok = light['pattern'][int(time.time()*8.0) % len(light['pattern'])] if 'pattern' in light else '#'
			return 1 if tok == '#' else 0
		else:
			return 0
	
	def set_key_state(self, key, value):
		# Map an key to a status in some external system. Then set it's value (0 or 1).
		key['state'] = value
		self.key_state_dirty = True
	
	def read_elite_status(self, dbg=False):
		fn = os.path.join(os.environ['USERPROFILE'], "Saved Games/Frontier Developments/Elite Dangerous/Status.json")
		
		if not os.path.exists(fn):
			return
		
		date = os.path.getmtime(fn)
		flags = 0
		
		# avoid reading the file lots when it hasn't changed..
		if self.esmask_date == date:
			return
		
		try:
			sf = SharedFile()
			fd = sf.open_for_read(fn)
			
			data = json.load(fd)
			flags = data['Flags']
			
			if dbg:
				for i in range(29):
					if ((1<<i) & flags) != 0:
						print(elite_status_map[i])
		except json.decoder.JSONDecodeError:
			# sometimes the json may be partially written when we open it, so ignore errors.
			# return the previous date so the code above will call us again later.
			return
		
		self.esmask_date = date;
		self.esmask = flags
	
	def sync_elite_status(self, dbg=False):
		while True:
			self.read_elite_status()
			
			if dbg:
				print(self.esmask_date, self.key_state_dirty)
			
			if self.key_state_dirty:
				# Synchronize the key state..
				self.key_state_dirty = False
				for key in self.driver.keymap.values():
					if not 'edstatus' in key:
						continue
					
					if 'state' in key and ((self.esmask >> key['edstatus']) & 1) != key['state']:
						if dbg:
							print('Syncing %s to: %u' % (elite_status_map[key['edstatus']], key['state']))
						self.driver.press_and_release(key)
			
			time.sleep(0.25)

class KeypadSettings:
	def __init__(self, fn = "settings.json"):
		with open(fn, 'r') as fd:
			self.data = json.load(fd)
	
	def get_settings_for_app(self, app):
		if app in self.data:
			settings = self.data[app]
		elif '_default_' in self.data:
			settings = self.data['_default_']
		else:
			settings = {'keymap' : {}, 'lightmap' : {}}
		
		for key in settings['keymap']:
			settings['keymap'][key]['idx'] = key
		
		for light in settings['lightmap']:
			settings['lightmap'][light]['idx'] = light
		
		return settings

class KeypadDriver:
	def __init__(self, args):
		self.args = args
		self.settings = KeypadSettings(args.settings_file)
		self.light_services = {}
		self.key_services = {}
		self.lightmask = 0
		self.connected = False
		
		DebugStatusService().register(self)
		DefaultStatusService().register(self)
		EliteDangerousStatusService().register(self)
		
		self.app = "_default_"
		s = self.settings.get_settings_for_app(self.app)
		self.keymap = s['keymap']
		self.lightmap = s['lightmap']
		
		self.pn_thread = Thread(target=self.scan_for_process_name, daemon=True)
		self.pn_thread.start()
	
	def scan_for_process_name(self):
		while True:
			self.app = active_window_process_name()
			#print(self.app)
			
			s = self.settings.get_settings_for_app(self.app)
			self.keymap = s['keymap']
			self.lightmap = s['lightmap']
			
			time.sleep(1)
	
	def register_light_service(self, srv, types):
		for typ in types:
			self.light_services[typ] = srv
	
	def register_key_service(self, srv, types):
		for typ in types:
			self.key_services[typ] = srv
	
	def press_and_release(self, key):
		keyboard.press_and_release(key['keypress'])
	
	def press(self, key):
		keyboard.press(key['keypress'])
	
	def release(self, key):
		keyboard.release(key['keypress'])
	
	def communicate(self):
		ard = serial.Serial(self.args.com_port,115200,timeout=5)
		
		while True:
			if self.connected:
				plightmask = self.lightmask
				for value in self.lightmap:
					light = self.lightmap[value]
					state = self.light_services[light['type']].get_light_state(light)
					if state:
						self.lightmask |= 1 << int(value)
					else:
						self.lightmask &= ~(1 << int(value))
				
				if plightmask != self.lightmask:
					for value in self.lightmap:
						if self.lightmask & (1 << int(value)):
							ard.write(b"l%u\n" % (int(value),))
						else:
							ard.write(b"d%u\n" % (int(value),))
					ard.flush()
			
			if ard.in_waiting > 0:
				msg = ard.readline()
				if msg:
					msg = msg.decode("utf-8", errors="ignore").strip()
					
					if len(msg) < 2:
						continue
					
					command = msg[-1]
					value = msg[:-1]
					
					if(command == 'u'):
						if value in self.keymap:
							key = self.keymap[value]
							self.key_services[key['type']].set_key_state(key, 1 if key['invert'] else 0)
					elif(command == 'd'):
						if value in self.keymap:
							key = self.keymap[value]
							self.key_services[key['type']].set_key_state(key, 0 if key['invert'] else 1)
					elif(command == 'h'):
						print("Handshake recieved.")
						self.connected = True
					elif(command == 'b'):
						print("Keypad reported %u buttons." % (int(value)))
					elif(command == 'l'):
						print("Keypad reported %u lights." % (int(value)))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--com_port', type=str, required=True,
						help='The com port name where your keypad is attached. (eg: COM3)')
	parser.add_argument('-s', '--settings_file', type=str, default="settings.json",
						help='Path to your json settings file')
	
	driver = KeypadDriver(parser.parse_args())
	driver.communicate()