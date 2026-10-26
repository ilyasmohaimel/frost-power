from bootstrap import *
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from frost_rx_efficiency import RxEfficiency
class RxChecks(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
  (self.base/'power').mkdir();(self.base/'power/control').write_text('on');(self.base/'power/runtime_status').write_text('active')
  (self.base/'hwmon/hwmon0').mkdir(parents=True);(self.base/'hwmon/hwmon0/temp2_input').write_text('55000')
  self.rx=RxEfficiency(-30,self.base)
 def test_auto_policy_never_reads_gpu(self):
  (self.base/'power/control').write_text('auto')
  with patch.object(self.rx,'read_offset',side_effect=AssertionError('GPU read')),patch.object(self.rx,'write_offset',side_effect=AssertionError('GPU write')):
   for t in range(10):self.rx.tick(t)
 def test_suspended_never_reads_gpu(self):
  (self.base/'power/runtime_status').write_text('suspended')
  with patch.object(self.rx,'read_offset',side_effect=AssertionError('GPU read')):
   for t in range(10):self.rx.tick(t)
 def test_active_debounce(self):
  with patch.object(self.rx,'read_offset',return_value=0) as read,patch.object(self.rx,'write_offset') as write:
   self.rx.tick(0);self.rx.tick(4);read.assert_not_called();self.rx.tick(5);write.assert_called_once_with(-30)
 def test_hot_gpu_waits(self):
  (self.base/'hwmon/hwmon0/temp2_input').write_text('70000')
  with patch.object(self.rx,'read_offset',side_effect=AssertionError('GPU read')):
   self.rx.tick(0);self.rx.tick(6);self.assertFalse(self.rx.applied)
 def test_foreign_offset_preserved(self):
  with patch.object(self.rx,'read_offset',return_value=-50),patch.object(self.rx,'write_offset') as write:
   self.rx.tick(0);self.rx.tick(6);write.assert_not_called();self.assertTrue(self.rx.blocked)
 def test_applied_is_not_polled(self):
  with patch.object(self.rx,'read_offset',return_value=0) as read,patch.object(self.rx,'write_offset'):
   self.rx.tick(0);self.rx.tick(6);self.rx.tick(7);self.rx.tick(8);self.assertEqual(read.call_count,1)
 def test_auto_transition_only_rearms(self):
  self.rx.applied=True;self.rx.owned=True;(self.base/'power/control').write_text('auto')
  with patch.object(self.rx,'write_offset') as write:
   self.rx.tick(0);write.assert_not_called();self.assertFalse(self.rx.applied);self.assertTrue(self.rx.owned)
 def test_unowned_reset_never_reads_gpu(self):
  with patch.object(self.rx,'read_offset',side_effect=AssertionError('GPU read')):self.rx.reset()
 def test_owned_reset(self):
  self.rx.owned=True
  with patch.object(self.rx,'read_offset',return_value=-30),patch.object(self.rx,'write_offset') as write:
   self.rx.reset();write.assert_called_once_with(0);self.assertFalse(self.rx.owned)
 def test_changed_user_offset_preserved_on_reset(self):
  self.rx.owned=True
  with patch.object(self.rx,'read_offset',return_value=-40),patch.object(self.rx,'write_offset') as write:
   self.rx.reset();write.assert_not_called()
if __name__=='__main__':unittest.main()
