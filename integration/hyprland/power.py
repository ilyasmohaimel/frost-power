#!/usr/bin/python3
"""Pair ASUS power profiles with the existing login GPU policy and Eco display."""
import argparse,importlib.util,json,os,re,subprocess,tempfile,time
from pathlib import Path
HOME=Path.home();CONFIG=HOME/'.config/frost-hyprland';RUNTIME=Path(os.environ.get('XDG_RUNTIME_DIR','/run/user/'+str(os.getuid())))/'frost-power-presets';DISPLAY=RUNTIME/'display.json'
PRESETS={'performance':{'active':'Performance','ac':'Performance','battery':'Quiet','gpu':'auto'},'balanced':{'active':'Balanced','ac':'Balanced','battery':'Balanced','gpu':'igpu'},'eco':{'active':'Quiet','ac':'Quiet','battery':'Quiet','gpu':'eco'}}
def run(*args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=10)
 if p.returncode:raise RuntimeError((p.stderr or p.stdout).strip() or 'Command failed')
 return p.stdout

def read_json(path):
 try:
  v=json.loads(path.read_text());return v if isinstance(v,dict) else {}
 except (OSError,ValueError):return {}

def gpu_module():
 spec=importlib.util.spec_from_file_location('frost_hypr_gpu',Path(__file__).with_name('gpu.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def profile():return Path('/sys/class/platform-profile/platform-profile-0/profile').read_text().strip()
def preset_for(value):return 'eco' if value=='quiet' else value

def defaults():
 text=run('/usr/bin/asusctl','profile','get');d={}
 for label,pattern in [('active',r'Active profile:\s*(\w+)'),('ac',r'AC profile\s+(\w+)'),('battery',r'Battery profile\s+(\w+)')]:
  m=re.search(pattern,text)
  if not m or m[1] not in ('Quiet','Balanced','Performance'):raise RuntimeError('ASUS profile defaults unavailable')
  d[label]=m[1]
 return d

def set_defaults(data):
 run('/usr/bin/asusctl','profile','set','--ac',data['ac']);run('/usr/bin/asusctl','profile','set','--battery',data['battery']);run('/usr/bin/asusctl','profile','set',data['active'])

def monitor_snapshot():
 rows=json.loads(run('/usr/bin/hyprctl','monitors','-j'));return next((r for r in rows if r['name']=='eDP-1'),None)

def monitor_set(m,hz):
 spec={'output':m['name'],'mode':f"{m['width']}x{m['height']}@{hz:.2f}",'position':f"{m['x']}x{m['y']}",'scale':m['scale'],'transform':m.get('transform',0)}
 fields=', '.join(k+' = '+json.dumps(v) for k,v in spec.items());run('/usr/bin/hyprctl','eval','hl.monitor({ '+fields+' })')
 for _ in range(20):
  current=monitor_snapshot()
  if current and abs(current['refreshRate']-hz)<.6:return
  time.sleep(.1)
 raise RuntimeError('Display refresh did not change as requested')

def display_policy():
 if not os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):return {'changed':False,'reason':'No active Hyprland session'}
 m=monitor_snapshot()
 if not m:return {'changed':False,'reason':'Internal display unavailable'}
 old=read_json(DISPLAY);signature=os.environ['HYPRLAND_INSTANCE_SIGNATURE']
 if old.get('signature')!=signature:old={}
 eco=profile()=='quiet'
 if eco:
  if not any(v.startswith(f"{m['width']}x{m['height']}@60.") for v in m.get('availableModes',[])):return {'changed':False,'reason':'60 Hz unavailable'}
  if abs(m['refreshRate']-60)<.6:return {'changed':False,'refreshHz':m['refreshRate']}
  state={'signature':signature,'monitor':m,'ownedWidth':m['width'],'ownedHeight':m['height'],'ownedHz':60}
  gpu_module().atomic_json(DISPLAY,state)
  try:monitor_set(m,60)
  except Exception:
   # A failed readback may follow a successful display change. Roll it back
   # before releasing ownership; retain the record if rollback also fails.
   current=monitor_snapshot()
   if current and abs(current['refreshRate']-60)<.6:monitor_set(m,m['refreshRate'])
   DISPLAY.unlink(missing_ok=True);raise
  return {'changed':True,'refreshHz':60}
 if old and m['width']==old['ownedWidth'] and m['height']==old['ownedHeight'] and abs(m['refreshRate']-old['ownedHz'])<.6:
  original=old['monitor'];monitor_set(original,original['refreshRate']);DISPLAY.unlink(missing_ok=True);return {'changed':True,'refreshHz':original['refreshRate']}
 DISPLAY.unlink(missing_ok=True);return {'changed':False,'refreshHz':m['refreshRate']}

def select(name):
 if name not in PRESETS:raise ValueError('Unknown power preset')
 desired=PRESETS[name];old=defaults();gpu=gpu_module();prior=gpu.mode()
 try:
  set_defaults(desired);gpu.request(desired['gpu'])
 except Exception:
  set_defaults(old);gpu.request(prior);raise
 gpu.atomic_json(CONFIG/'power.json',{'preset':name})
 return {'preset':name,'profile':profile(),'nextGpuMode':desired['gpu'],'applies':'CPU now; desktop GPU at next login'}

def status():
 current=profile();gpu=gpu_module();data=gpu.status();config=read_json(Path('/etc/frost-thermal-tuning.json'));thermal=read_json(Path('/run/frost-thermal-tuning/state.json'))
 return {'tuningAvailable':bool(thermal) and not thermal.get('reset',False),'tuningReady':thermal.get('profile')==current and thermal.get('pending') is False,'preset':preset_for(current),'profile':current,'cpuLimitW':config.get('balancedCpuW') if current=='balanced' else config.get('quietCpuW') if current=='quiet' else None,'boostEnabled':Path('/sys/devices/system/cpu/cpufreq/boost').read_text().strip()=='1','desktop':data['desktop'],'nextMode':data['nextMode'],'nextGPU':data['nextGPU'],'rxOff':data['rxOff'],'rxRuntime':data['rxRuntime'],'active':data['active']}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('select','status','display'));parser.add_argument('preset',nargs='?',choices=tuple(PRESETS));args=parser.parse_args()
 try:
  if args.action=='select':
   if not args.preset:raise ValueError('Choose performance, balanced or eco')
   print(json.dumps(select(args.preset)))
  elif args.action=='display':print(json.dumps(display_policy()))
  else:print(json.dumps(status()))
 except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as e:parser.exit(1,str(e)+'\n')
if __name__=='__main__':main()
