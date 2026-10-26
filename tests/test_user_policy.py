from bootstrap import *
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import Mock,patch
HOME=Path.home()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=load('preset',ROOT/'integration/hyprland/power.py')
g=load('gpu',ROOT/'integration/hyprland/gpu.py')
u=load('usb',ROOT/'integration/hyprland/frost_usb_charge.py')
class Policy(unittest.TestCase):
 def test_noisy_hyprland_instances(self):
  rows=[{'pid':123,'instance':'test'}]
  self.assertEqual(g.parse_instances('debug [startup] log\n'+json.dumps(rows)+'\nnoise'),rows)
 def test_missing_instances_rejected(self):
  for value in ('[]','garbage','[{"bad":1}]'):
   with self.assertRaises(ValueError):g.parse_instances(value)
 def test_select_pairs_defaults_with_gpu(self):
  gpu=Mock();gpu.mode.return_value='auto'
  with patch.object(p,'defaults',return_value={'active':'Performance','ac':'Performance','battery':'Quiet'}),patch.object(p,'set_defaults') as write,patch.object(p,'gpu_module',return_value=gpu),patch.object(p,'profile',return_value='balanced'):
   p.select('balanced');write.assert_called_once_with(p.PRESETS['balanced']);gpu.request.assert_called_once_with('igpu')
 def test_gpu_failure_restores_defaults_and_mode(self):
  gpu=Mock();gpu.mode.return_value='auto';gpu.request.side_effect=[RuntimeError('test failure'),None];old={'active':'Performance','ac':'Performance','battery':'Quiet'}
  with patch.object(p,'defaults',return_value=old),patch.object(p,'set_defaults') as write,patch.object(p,'gpu_module',return_value=gpu):
   with self.assertRaises(RuntimeError):p.select('eco')
   self.assertEqual(write.call_args_list[-1].args[0],old);self.assertEqual(gpu.request.call_args_list[-1].args[0],'auto');gpu.atomic_json.assert_not_called()
 def test_display_eco_then_restore(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p,'DISPLAY',Path(d)/'display.json'),patch.dict(p.os.environ,{'HYPRLAND_INSTANCE_SIGNATURE':'test'}),patch.object(p,'gpu_module',return_value=g):
   monitor={'name':'eDP-1','width':1920,'height':1080,'x':0,'y':0,'scale':1,'refreshRate':300,'availableModes':['1920x1080@60.00Hz']}
   with patch.object(p,'profile',return_value='quiet'),patch.object(p,'monitor_snapshot',return_value=monitor),patch.object(p,'monitor_set') as setmode:
    self.assertTrue(p.display_policy()['changed']);setmode.assert_called_once_with(monitor,60)
   low={**monitor,'refreshRate':60}
   with patch.object(p,'profile',return_value='balanced'),patch.object(p,'monitor_snapshot',return_value=low),patch.object(p,'monitor_set') as setmode:
    self.assertTrue(p.display_policy()['changed']);setmode.assert_called_once_with(monitor,300);self.assertFalse(p.DISPLAY.exists())
 def test_foreign_display_change_preserved(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p,'DISPLAY',Path(d)/'display.json'),patch.dict(p.os.environ,{'HYPRLAND_INSTANCE_SIGNATURE':'test'}),patch.object(p,'profile',return_value='balanced'),patch.object(p,'monitor_snapshot',return_value={'width':1920,'height':1080,'refreshRate':120}),patch.object(p,'monitor_set') as setmode:
   p.DISPLAY.write_text(json.dumps({'signature':'test','ownedWidth':1920,'ownedHeight':1080,'ownedHz':60,'monitor':{'refreshRate':300}}));self.assertFalse(p.display_policy()['changed']);setmode.assert_not_called()
 def test_partial_display_failure_restores_original(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p,'DISPLAY',Path(d)/'display.json'),patch.dict(p.os.environ,{'HYPRLAND_INSTANCE_SIGNATURE':'test'}),patch.object(p,'gpu_module',return_value=g),patch.object(p,'profile',return_value='quiet'):
   monitor={'name':'eDP-1','width':1920,'height':1080,'x':0,'y':0,'scale':1,'refreshRate':300,'availableModes':['1920x1080@60.00Hz']}
   with patch.object(p,'monitor_snapshot',side_effect=[monitor,{**monitor,'refreshRate':60}]),patch.object(p,'monitor_set',side_effect=[RuntimeError('readback failed'),None]) as setmode:
    with self.assertRaises(RuntimeError):p.display_policy()
    self.assertEqual(setmode.call_args_list[-1].args,(monitor,300));self.assertFalse(p.DISPLAY.exists())
 def test_failed_display_rollback_retains_ownership(self):
  with tempfile.TemporaryDirectory() as d,patch.object(p,'DISPLAY',Path(d)/'display.json'),patch.dict(p.os.environ,{'HYPRLAND_INSTANCE_SIGNATURE':'test'}),patch.object(p,'gpu_module',return_value=g),patch.object(p,'profile',return_value='quiet'):
   monitor={'name':'eDP-1','width':1920,'height':1080,'x':0,'y':0,'scale':1,'refreshRate':300,'availableModes':['1920x1080@60.00Hz']}
   with patch.object(p,'monitor_snapshot',side_effect=[monitor,{**monitor,'refreshRate':60}]),patch.object(p,'monitor_set',side_effect=RuntimeError('display unavailable')):
    with self.assertRaises(RuntimeError):p.display_policy()
    self.assertEqual(json.loads(p.DISPLAY.read_text())['monitor']['refreshRate'],300)
 def test_usb_respects_balanced(self):
  self.assertEqual(u.desired('usb-c','barrel',lambda:{'Battery':'Balanced'}),'Balanced')
  for default in ('Quiet','Performance'):self.assertEqual(u.desired('usb-c','barrel',lambda:{'Battery':default}),'Quiet')
 def test_usb_unplug_restores_battery_default(self):
  self.assertEqual(u.desired('battery','usb-c',lambda:{'Battery':'Balanced'}),'Balanced')
  self.assertIsNone(u.desired('barrel','battery',lambda:{}))
if __name__=='__main__':unittest.main(verbosity=2)
