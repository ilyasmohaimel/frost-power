from bootstrap import *
import importlib.machinery,types,unittest
from unittest.mock import patch,Mock,call
loader=importlib.machinery.SourceFileLoader('thermal',str(ROOT/'src/frost-thermal-tuning'));m=types.ModuleType(loader.name);loader.exec_module(m)
CONFIG={'curveOptimizer':-5,'maxCpuC':90,'gpuOffsetMv':-30}
class ControllerChecks(unittest.TestCase):
 def apply_case(self,limit,old,target,original):
  with patch.object(m,'profile',return_value='performance'),patch.object(m,'info',side_effect=[limit,target]),patch.object(m,'previous',return_value=old),patch.object(m,'run') as run,patch.object(m,'save') as save,patch.object(m.time,'sleep'):
   m.apply(CONFIG);run.assert_called_once_with('--set-coall=1048571','--tctl-temp='+str(target));self.assertEqual(save.call_args.args[0]['originalCpuTargetC'],original)
 def test_initial_cap(self):self.apply_case(95,{},90,95)
 def test_preserve_lower_target(self):self.apply_case(85,{},85,85)
 def test_profile_carryover(self):self.apply_case(90,{'cpuTargetC':90,'originalCpuTargetC':95},90,95)
 def test_firmware_changed_baseline(self):self.apply_case(93,{'cpuTargetC':89,'originalCpuTargetC':95},90,93)
 def test_reset_owned_limit_and_gpu(self):
  rx=Mock()
  with patch.object(m,'RX',rx),patch.object(m,'profile',return_value='performance'),patch.object(m,'info',side_effect=[89,95]),patch.object(m,'previous',return_value={'cpuTargetC':89,'originalCpuTargetC':95}),patch.object(m,'run') as run,patch.object(m,'save'):
   m.reset(CONFIG);self.assertEqual(run.call_args_list,[call('--set-coall=0'),call('--tctl-temp=95')]);rx.reset.assert_called_once()
 def test_preserve_other_lower_target(self):
  with patch.object(m,'profile',return_value='quiet'),patch.object(m,'info',side_effect=[80,80]),patch.object(m,'previous',return_value={'cpuTargetC':89,'originalCpuTargetC':95}),patch.object(m,'run') as run,patch.object(m,'save'):
   m.reset(CONFIG);run.assert_called_once_with('--set-coall=0')
 def test_profile_change_retries_without_cpu_write(self):
  with patch.object(m,'profile',side_effect=['quiet','performance']),patch.object(m,'run') as run:
   self.assertFalse(m.apply(CONFIG));run.assert_not_called()
 def test_gpu_reset_attempted_when_cpu_command_fails(self):
  rx=Mock()
  with patch.object(m,'RX',rx),patch.object(m,'profile',return_value='performance'),patch.object(m,'previous',return_value={}),patch.object(m,'run',side_effect=RuntimeError('SMU unavailable')):
   with self.assertRaises(RuntimeError):m.reset(CONFIG)
   rx.reset.assert_called_once()
if __name__=='__main__':unittest.main()
