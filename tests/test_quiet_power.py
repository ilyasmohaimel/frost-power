from bootstrap import *
import unittest
from unittest.mock import Mock
from frost_cpu_power import QuietPower,KEYS
NATIVE={'apu-slow-limit':50}
PERF={'apu-slow-limit':90}
TARGET={k:35 for k in KEYS}
BASE={'quiet':NATIVE,'performance':PERF,'balanced':PERF}
class Checks(unittest.TestCase):
 def make(self,state=None):
  q=QuietPower(Mock(),35,BASE,state);q.read=Mock(return_value=dict(NATIVE));q.write=Mock();return q
 def test_quiet_caps_and_readback(self):
  q=self.make();q.read.side_effect=[NATIVE,TARGET];q.reconcile('quiet');q.write.assert_called_once_with(TARGET);self.assertEqual(q.state()['original'],NATIVE)
 def test_keep_lower_foreign_limits(self):
  q=self.make();low={k:20 for k in KEYS};q.read.return_value=low;q.reconcile('quiet');q.write.assert_called_once_with({});self.assertEqual(q.saved['target'],{})
 def test_same_profile_carries_baseline(self):
  q=self.make({'profile':'quiet','target':TARGET,'original':NATIVE});q.read.return_value=TARGET;q.reconcile('quiet');self.assertEqual(q.saved['original'],NATIVE)
 def test_performance_releases_carried_caps(self):
  q=self.make({'profile':'quiet','target':TARGET,'original':NATIVE});q.read.side_effect=[TARGET,PERF];q.reconcile('performance');q.write.assert_called_once_with(PERF)
 def test_performance_keeps_native_limits(self):
  q=self.make({'profile':'quiet','target':TARGET,'original':NATIVE});q.read.return_value=PERF;q.reconcile('performance');q.write.assert_called_once_with({})
 def test_reset_quiet_to_original(self):
  q=self.make({'profile':'quiet','target':TARGET,'original':NATIVE});q.read.return_value=TARGET;q.reset('quiet');q.write.assert_called_once_with(NATIVE)
 def test_reset_preserves_changed_user_limit(self):
  q=self.make({'profile':'quiet','target':TARGET,'original':NATIVE});q.read.return_value={k:20 for k in KEYS};q.reset('quiet');q.write.assert_called_once_with({})
 def test_foreign_lower_limit_survives_profile_change(self):
  q=self.make();low={k:20 for k in KEYS};q.read.return_value=low;q.reconcile('quiet');q.reconcile('performance');self.assertEqual(q.saved['original'],low);self.assertEqual(q.write.call_args.args[0],{})
 def test_detects_power_drift(self):self.assertTrue(self.make().drifted('quiet'))
if __name__=='__main__':unittest.main()
