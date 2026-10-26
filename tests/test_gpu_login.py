from bootstrap import *
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

BASE=Path(__file__).parent

def load(name,path):
    spec=importlib.util.spec_from_loader(name,importlib.machinery.SourceFileLoader(name,str(path)))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

gpu=load('hypr_gpu',ROOT/'integration/hyprland/gpu.py')
power=load('hypr_power',ROOT/'reference/g513qy/frost-gpu-power')
launcher=load('hypr_launcher',ROOT/'integration/hyprland/frost-hyprland-session')

REAL_SPEC = importlib.util.spec_from_file_location
class LoginGPU(unittest.TestCase):
    def setUp(self):
        # These are policy fixtures, not hardware tests. Never read a runner's GPU.
        def local_spec(name,path,*args,**kwargs):
            if name == 'frost_power': path=ROOT/'reference/g513qy/frost_power.py'
            if name == 'hypr_gpu': path=ROOT/'integration/hyprland/gpu.py'
            return REAL_SPEC(name,path,*args,**kwargs)
        self.patches=[patch.object(importlib.util,'spec_from_file_location',side_effect=local_spec),
                      patch.object(Path,'is_char_device',return_value=True),
                      patch.object(gpu,'power_source',return_value={'source':'barrel','useRX':True})]
        for item in self.patches:item.start();self.addCleanup(item.stop)

    def test_automatic_power_sources(self):
        for source,rx in [('barrel',True),('usb-c',False),('battery',False),('external-unknown',False)]:
            self.assertEqual(gpu.select('auto',{'source':source,'useRX':rx}),'rx' if rx else 'igpu')
    def test_manual_and_eco_ignore_charger(self):
        for rx in (False,True):
            for mode,target in [('igpu','igpu'),('rx','rx'),('eco','igpu')]:
                self.assertEqual(gpu.select(mode,{'useRX':rx}),target)
    def test_request_only_saves_next_login(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'gpu.json'
            with patch.object(gpu.subprocess,'run',side_effect=AssertionError('A save cannot change hardware')):
                for mode in gpu.MODES:
                    gpu.request(mode,path);self.assertEqual(gpu.mode(path),mode)
            self.assertEqual(path.stat().st_mode&0o777,0o600)
    def test_invalid_config_falls_back_to_auto(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'gpu.json'
            for data in ['bad','[]','{"mode":"garbage"}']:
                path.write_text(data);self.assertEqual(gpu.mode(path),'auto')
    def test_stale_session_is_not_current(self):
        with patch.dict(gpu.os.environ,{'HYPRLAND_INSTANCE_SIGNATURE':'new','FROST_HYPRLAND_TOKEN':'token'}):
            self.assertFalse(gpu.active_session({'signature':'old','token':'token','selected':'rx'}))
            self.assertFalse(gpu.active_session({'signature':'new','token':'old','selected':'rx'}))
            self.assertTrue(gpu.active_session({'signature':'new','token':'token','selected':'igpu'}))
    def test_power_validation_rejects_kde_and_stale_process(self):
        data={'selected':'igpu','token':'token','session':'3'}
        env={'FROST_HYPRLAND_GPU':'igpu','FROST_HYPRLAND_TOKEN':'token','XDG_SESSION_ID':'3'}
        session={'User':'1000','Desktop':'Hyprland','Active':'yes','Type':'wayland'}
        self.assertEqual(power.verified_hyprland_mode(data,env,session),'igpu')
        for key,value in [('Desktop','KDE'),('Active','no'),('User','0')]:
            self.assertIsNone(power.verified_hyprland_mode(data,env,{**session,key:value}))
        self.assertIsNone(power.verified_hyprland_mode(data,{**env,'FROST_HYPRLAND_TOKEN':'old'},session))
    def test_existing_kde_policy_is_unchanged(self):
        for ac in (False,True):
            self.assertEqual(power.policy(ac,'auto'),'on' if ac else 'auto')
            for mode in ('eco','igpu'):self.assertEqual(power.policy(ac,mode),'auto')
            self.assertEqual(power.policy(ac,'rx'),'on')
    def test_hyprland_current_gpu_controls_runtime_policy(self):
        self.assertEqual(power.policy(True,'igpu'),'auto')
        self.assertEqual(power.policy(False,'rx'),'on')
    def test_launcher_is_native_and_isolates_kde(self):
        with patch.dict(launcher.os.environ,{'FROST_GPU_LIVE_SESSION':'1','ZSS_SOCKET':'bad','KWIN_RENDER_NODES':'bad','LD_PRELOAD':'/opt/frost-gpu/lib/libzss_airlock.so'}):
            for mode in ('igpu','rx','eco'):
                env,state=launcher.session_environment(mode)
                self.assertNotIn('ZSS_SOCKET',env);self.assertNotIn('KWIN_RENDER_NODES',env)
                self.assertNotIn('FROST_GPU_LIVE_SESSION',env);self.assertNotIn('LD_PRELOAD',env)
                self.assertEqual(env['FROST_HYPRLAND_MODE'],mode)
                self.assertEqual(state['selected'],'rx' if mode=='rx' else 'igpu')
                self.assertTrue(env['FROST_HYPRLAND_TOKEN'])
    def test_automatic_login_honors_saved_mode(self):
        with tempfile.TemporaryDirectory() as d, patch.dict(launcher.os.environ,{'XDG_CONFIG_HOME':d}):
            for requested in gpu.MODES:
                gpu.request(requested)
                env,state=launcher.session_environment('auto')
                self.assertEqual(state['mode'],requested)
                self.assertEqual(state['selected'],gpu.select(requested,gpu.power_source()))
                self.assertEqual(env['FROST_HYPRLAND_MODE'],requested)
    def test_eco_profile_is_only_set_on_activation(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'session.json'
            env={'XDG_CURRENT_DESKTOP':'Hyprland','FROST_HYPRLAND_TOKEN':'test',
                 'FROST_HYPRLAND_GPU':'igpu','FROST_HYPRLAND_MODE':'eco',
                 'HYPRLAND_INSTANCE_SIGNATURE':'test-instance'}
            with patch.dict(gpu.os.environ,env), patch.object(gpu,'runtime_path',return_value=path), \
                 patch.object(gpu.subprocess,'check_output',return_value='[{"instance":"test-instance","pid":123}]'), \
                 patch.object(gpu.subprocess,'run') as run:
                gpu.activate()
                self.assertEqual(json.loads(path.read_text())['selected'],'igpu')
                run.assert_called_once_with(['/usr/bin/asusctl','profile','set','Quiet'],check=True,timeout=8,capture_output=True)
                run.reset_mock()
                with patch.dict(gpu.os.environ,{'FROST_HYPRLAND_MODE':'igpu'}):gpu.activate()
                run.assert_not_called()
    def test_read_status_never_opens_gpu_telemetry(self):
        original=gpu.text;paths=[]
        def record(path):paths.append(str(path));return original(path)
        with patch.object(gpu,'text',record):gpu.status()
        self.assertFalse(any('temp' in p or 'busy' in p or '/dev/dri' in p for p in paths))

if __name__=='__main__':unittest.main(verbosity=2)
