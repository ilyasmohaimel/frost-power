"""Own only the measured Quiet power caps and restore them across profiles."""
import re,subprocess
KEYS={'apu-slow-limit':'PPT LIMIT APU'}
class QuietPower:
 def __init__(self,run,cap,baselines,state=None):
  if cap not in (30,35,40):raise ValueError('Untested Quiet power cap')
  self.run=run;self.cap=cap;self.baselines=baselines;self.saved=state or {}
 def read(self):
  text=self.run('--info')
  return {k:float(re.search(r'\| '+re.escape(label)+r'\s*\|\s*([\d.]+)',text)[1]) for k,label in KEYS.items()}
 def write(self,values):
  if values:self.run(*(f'--{k}={round(v*1000)}' for k,v in values.items()))
 def reconcile(self,profile):
  now=self.read();old=self.saved;original=dict(now);changes={}
  for key,value in now.items():
   owned=old.get('target',{}).get(key)
   if owned is not None and abs(value-owned)<.1:
    original[key]=(old.get('original',{}).get(key,value) if old.get('profile')==profile else self.baselines[profile][key])
  if profile=='quiet':
   target={k:min(original[k],self.cap) for k in KEYS}
  else:target=original
  changes={k:v for k,v in target.items() if abs(now[k]-v)>.1}
  self.saved={'profile':profile,'original':original,'target':{k:v for k,v in target.items() if profile=='quiet' and v<original[k]-.1}}
  self.write(changes)
  actual=self.read() if changes else now
  if any(abs(actual[k]-target[k])>.5 for k in KEYS):raise RuntimeError('CPU power limit readback mismatch')
  return bool(changes)
 def drifted(self,profile):
  if profile!='quiet':return False
  current=self.read()
  return any(current[k]>self.cap+.5 for k in KEYS)
 def reset(self,profile):
  old=self.saved
  if not old.get('target'):return
  current=self.read();changes={}
  for k,owned in old['target'].items():
   if abs(current[k]-owned)<.1:
    changes[k]=old['original'][k] if old.get('profile')==profile else self.baselines[profile][k]
  self.write(changes);self.saved={}
 def state(self):return self.saved

class ProfilePower(QuietPower):
 """Maintain Balanced/Eco CPU limits and own Eco's reversible boost setting."""
 def __init__(self,run,caps,baselines,state=None,boost_path=__import__('pathlib').Path('/sys/devices/system/cpu/cpufreq/boost')):
  if set(caps)!={'quiet','balanced'} or caps['quiet'] not in (15,18,20) or caps['balanced'] not in (30,35,38,40):raise ValueError('Untested profile CPU caps')
  self.run=run;self.caps=caps;self.baselines=baselines;self.saved=state or {};self.boost_path=boost_path
 def read_boost(self):
  value=self.boost_path.read_text().strip()
  if value not in ('0','1'):raise RuntimeError('CPU boost control unavailable')
  return int(value)
 def reconcile(self,profile):
  now=self.read();old=self.saved;original=dict(now)
  for key,value in now.items():
   owned=old.get('target',{}).get(key)
   if owned is not None and abs(value-owned)<.1:
    original[key]=old['original'][key] if old.get('profile')==profile else self.baselines[profile][key]
  target={k:min(v,self.caps[profile]) if profile in self.caps else v for k,v in original.items()}
  boost=self.read_boost();old_boost=old.get('boost',{});original_boost=old_boost.get('original',boost) if boost==old_boost.get('target') else boost
  desired_boost=0 if profile=='quiet' else original_boost
  self.saved={'profile':profile,'original':original,'target':{k:v for k,v in target.items() if v<original[k]-.1},'boost':{'original':original_boost,'target':desired_boost} if desired_boost!=original_boost else {}}
  changes={k:v for k,v in target.items() if abs(v-now[k])>.1};self.write(changes)
  if boost!=desired_boost:self.boost_path.write_text(str(desired_boost)+'\n')
  actual=self.read() if changes else now
  if any(abs(actual[k]-target[k])>.5 for k in KEYS) or self.read_boost()!=desired_boost:raise RuntimeError('CPU profile settings readback mismatch')
  return bool(changes) or boost!=desired_boost
 def drifted(self,profile):
  if profile in self.caps and any(v>self.caps[profile]+.5 for v in self.read().values()):return True
  return profile=='quiet' and self.read_boost()!=0
 def reset(self,profile):
  old=self.saved;current=self.read();changes={}
  for k,owned in old.get('target',{}).items():
   if abs(current[k]-owned)<.1:changes[k]=old['original'][k] if old.get('profile')==profile else self.baselines[profile][k]
  self.write(changes);boost=old.get('boost',{})
  if boost and self.read_boost()==boost['target']:self.boost_path.write_text(str(boost['original'])+'\n')
  self.saved={}
