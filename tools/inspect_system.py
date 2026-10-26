#!/usr/bin/env python3
"""Read identity and cached power policy; never apply settings or query dGPU telemetry."""
import json
from pathlib import Path
def read(path):
 try:return Path(path).read_text().strip()
 except OSError:return None
def main():
 gpus=[]
 for device in sorted(Path('/sys/bus/pci/devices').glob('*')):
  if (read(device/'class') or '').startswith('0x03'):
   gpus.append({'pci':device.name,'vendor':read(device/'vendor'),'device':read(device/'device'),'runtimePolicy':read(device/'power/control'),'runtimeStatus':read(device/'power/runtime_status'),'pciPowerState':read(device/'power_state')})
 cpu=next((line.split(':',1)[1].strip() for line in (read('/proc/cpuinfo') or '').splitlines() if line.startswith('model name')),None)
 print(json.dumps({'product':read('/sys/class/dmi/id/product_name'),'cpu':cpu,'profile':read('/sys/firmware/acpi/platform_profile'),'boost':read('/sys/devices/system/cpu/cpufreq/boost'),'epp':read('/sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference'),'gpus':gpus,'changesApplied':False},indent=2))
if __name__=='__main__':main()
