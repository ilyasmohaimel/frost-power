from bootstrap import *
import importlib.machinery,types,unittest
from unittest.mock import patch,Mock
loader=importlib.machinery.SourceFileLoader('thermal',str(ROOT/'src/frost-thermal-tuning'));m=types.ModuleType(loader.name);loader.exec_module(m)
class Checkpoint(unittest.TestCase):
 def test_ownership_saved_before_wait_even_if_profile_changes(self):
  events=[];power=Mock();power.reconcile.return_value=True
  with patch.object(m,'POWER',power),patch.object(m,'profile',side_effect=['quiet','balanced']),patch.object(m,'previous',return_value={'bootId':m.BOOT_ID}),patch.object(m,'save',side_effect=lambda data:events.append(('save',dict(data)))),patch.object(m.time,'sleep',side_effect=lambda seconds:events.append(('sleep',seconds))),patch.object(m,'run') as run:
   self.assertFalse(m.apply({'curveOptimizer':-5,'maxCpuC':90}))
   self.assertEqual(events[0][0],'save');self.assertTrue(events[0][1]['pending']);self.assertEqual(events[1],('sleep',8));run.assert_not_called()
if __name__=='__main__':unittest.main()
