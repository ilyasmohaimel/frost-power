from bootstrap import *
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from frost_rx_efficiency import RxEfficiency
class Rollback(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name);(self.base/'power').mkdir();self.control=self.base/'power/control';self.control.write_text('auto');(self.base/'power/runtime_status').write_text('active');self.rx=RxEfficiency(-30,self.base,owned=True)
 def test_wakes_for_reset_then_releases_policy(self):
  def read():self.assertEqual(self.control.read_text().strip(),'on');return -30
  with patch.object(self.rx,'read_offset',side_effect=read),patch.object(self.rx,'write_offset') as write:
   self.rx.reset();write.assert_called_once_with(0)
  self.assertEqual(self.control.read_text().strip(),'auto');self.assertFalse(self.rx.owned)
 def test_failed_reset_releases_policy_and_retains_ownership(self):
  with patch.object(self.rx,'read_offset',side_effect=OSError('test failure')):
   with self.assertRaises(OSError):self.rx.reset()
  self.assertEqual(self.control.read_text().strip(),'auto');self.assertTrue(self.rx.owned)
 def test_wake_timeout_releases_policy(self):
  (self.base/'power/runtime_status').write_text('suspended')
  with patch('frost_rx_efficiency.time.monotonic',side_effect=[0,6]):
   with self.assertRaises(RuntimeError):self.rx.reset()
  self.assertEqual(self.control.read_text().strip(),'auto');self.assertTrue(self.rx.owned)
if __name__=='__main__':unittest.main(verbosity=2)
