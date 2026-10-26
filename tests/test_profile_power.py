from bootstrap import *
import tempfile,unittest
from pathlib import Path
from unittest.mock import Mock
from frost_cpu_power import ProfilePower
BASE={'performance':{'apu-slow-limit':90},'balanced':{'apu-slow-limit':74},'quiet':{'apu-slow-limit':50}}
class Checks(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.boost=Path(self.tmp.name)/'boost';self.boost.write_text('1')
 def make(self,value=50,state=None):
  q=ProfilePower(Mock(),{'balanced':38,'quiet':20},BASE,state,self.boost);q.read=Mock(return_value={'apu-slow-limit':value});q.write=Mock();return q
 def test_eco_cap_and_boost(self):
  q=self.make();q.read.side_effect=[{'apu-slow-limit':50},{'apu-slow-limit':20}];q.reconcile('quiet');q.write.assert_called_once_with({'apu-slow-limit':20});self.assertEqual(self.boost.read_text().strip(),'0');self.assertEqual(q.saved['boost'],{'original':1,'target':0})
 def test_balanced_keeps_boost(self):
  q=self.make(74);q.read.side_effect=[{'apu-slow-limit':74},{'apu-slow-limit':38}];q.reconcile('balanced');self.assertEqual(self.boost.read_text().strip(),'1')
 def test_eco_to_balanced_restores_owned_boost(self):
  self.boost.write_text('0');q=self.make(74,{'profile':'quiet','original':{'apu-slow-limit':50},'target':{'apu-slow-limit':20},'boost':{'original':1,'target':0}});q.read.side_effect=[{'apu-slow-limit':74},{'apu-slow-limit':38}];q.reconcile('balanced');self.assertEqual(self.boost.read_text().strip(),'1')
 def test_foreign_disabled_boost_preserved(self):
  self.boost.write_text('0');q=self.make(20);q.reconcile('balanced');self.assertEqual(self.boost.read_text().strip(),'0');self.assertEqual(q.saved['boost'],{})
 def test_foreign_lower_limit_preserved(self):
  q=self.make(10);q.reconcile('quiet');self.assertEqual(q.saved['target'],{})
 def test_reapply_retains_originals(self):
  self.boost.write_text('0');q=self.make(20,{'profile':'quiet','original':{'apu-slow-limit':64},'target':{'apu-slow-limit':20},'boost':{'original':1,'target':0}});q.reconcile('quiet');self.assertEqual(q.saved['original']['apu-slow-limit'],64);self.assertEqual(q.saved['boost']['original'],1)
 def test_performance_releases_carried_cap(self):
  self.boost.write_text('0');q=self.make(20,{'profile':'quiet','original':{'apu-slow-limit':50},'target':{'apu-slow-limit':20},'boost':{'original':1,'target':0}});q.read.side_effect=[{'apu-slow-limit':20},{'apu-slow-limit':90}];q.reconcile('performance');q.write.assert_called_once_with({'apu-slow-limit':90});self.assertEqual(self.boost.read_text().strip(),'1')
 def test_reset_restores_owned_settings(self):
  self.boost.write_text('0');q=self.make(20,{'profile':'quiet','original':{'apu-slow-limit':64},'target':{'apu-slow-limit':20},'boost':{'original':1,'target':0}});q.reset('quiet');q.write.assert_called_once_with({'apu-slow-limit':64});self.assertEqual(self.boost.read_text().strip(),'1')
 def test_reset_preserves_foreign_changed_limits(self):
  q=self.make(12,{'profile':'quiet','original':{'apu-slow-limit':50},'target':{'apu-slow-limit':20},'boost':{'original':1,'target':0}});q.reset('quiet');q.write.assert_called_once_with({});self.assertEqual(self.boost.read_text().strip(),'1')
 def test_drift_detection_boost(self):
  q=self.make(20);self.assertTrue(q.drifted('quiet'))
 def test_drift_detection_cap(self):self.assertTrue(self.make(74).drifted('balanced'))
if __name__=='__main__':unittest.main()
