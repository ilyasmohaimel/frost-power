"""Maintain a tested offset only while the existing policy holds the RX awake."""
import re,time
from pathlib import Path

class RxEfficiency:
 def __init__(self,offset=-30,base=Path('/sys/bus/pci/devices/0000:03:00.0'),owned=False):
  if offset not in (-20,-30):raise ValueError('Untested RX offset')
  self.base=base;self.offset=offset;self.owned=owned;self.applied=False;self.active_since=None;self.last_control=None;self.status='waiting for RX policy';self.blocked=False
 def state(self):return {'offsetRequestedMv':self.offset,'applied':self.applied,'owned':self.owned,'status':self.status}
 def read_offset(self):
  match=re.search(r'OD_VDDGFX_OFFSET:\s*(-?\d+)mV',(self.base/'pp_od_clk_voltage').read_text())
  if not match:raise RuntimeError('RX voltage control unavailable')
  return int(match[1])
 def write_offset(self,value):
  level=self.base/'power_dpm_force_performance_level';od=self.base/'pp_od_clk_voltage'
  if level.read_text().strip()!='auto':raise RuntimeError('Another tool owns manual GPU clocks')
  try:
   level.write_text('manual\n');od.write_text(f'vo {value}\n');od.write_text('c\n')
  finally:level.write_text('auto\n')
  if self.read_offset()!=value:raise RuntimeError('RX offset readback mismatch')
 def rearm(self):
  self.applied=False;self.blocked=False;self.active_since=None
 def tick(self,now=None):
  before=self.state();now=time.monotonic() if now is None else now
  # These power attributes are cached kernel state. Never read hardware sensors
  # or voltage controls when the established GPU policy allows suspension.
  control=(self.base/'power/control').read_text().strip()
  if control!='on':
   self.applied=False;self.active_since=None;self.status='waiting for RX policy';self.last_control=control
   return self.state()!=before
  self.last_control=control
  if self.applied or self.blocked:return False
  if (self.base/'power/runtime_status').read_text().strip()!='active':
   self.active_since=None;return False
  if self.active_since is None:self.active_since=now
  if now-self.active_since<5:return False
  sensor=next((self.base/'hwmon').iterdir())/'temp2_input'
  if int(sensor.read_text())>=65000:
   self.status='waiting for RX to cool below 65C';return self.state()!=before
  current=self.read_offset()
  if current not in (0,self.offset):
   self.blocked=True;self.status='different user voltage setting preserved';return self.state()!=before
  if current==0:
   try:self.write_offset(self.offset)
   except Exception:
    try:self.write_offset(0)
    finally:self.blocked=True;self.status='RX adjustment failed and was reset'
    raise
   self.owned=True
  self.applied=True;self.status='applied';return self.state()!=before
 def reset(self):
  if not self.owned:return
  # Voltage controls reject reads in D3cold. Explicit rollback temporarily
  # holds the card awake; routine monitoring never changes its power policy.
  control=self.base/'power/control';original=control.read_text().strip()
  if original not in ('on','auto'):raise RuntimeError('Unexpected RX runtime policy')
  temporary=original=='auto'
  try:
   if temporary:control.write_text('on\n')
   deadline=time.monotonic()+5
   while (self.base/'power/runtime_status').read_text().strip()!='active':
    if time.monotonic()>=deadline:raise RuntimeError('RX did not wake for explicit rollback')
    time.sleep(.1)
   if self.read_offset()==self.offset:self.write_offset(0)
  finally:
   if temporary and control.read_text().strip()=='on':control.write_text('auto\n')
  self.owned=False;self.applied=False;self.status='reset'
