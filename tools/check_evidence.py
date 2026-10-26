#!/usr/bin/env python3
"""Check published measurement arithmetic without touching hardware."""
import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(name):return json.loads((R/'data'/name).read_text())
def main():
 rows=load('2026-10-26/installed-results.json');assert len(rows)==8
 for row in rows:
  assert row['exit']==0 and row['stop'] is None
  assert math.isfinite(row['meanCpuC']) and row['maxCpuC']>=row['meanCpuC']
  if row['name'].endswith('igpu'):assert len(row['fps'])==4 and row['rxReturnedToSleep']
  else:assert row['rxSuspendedEverySample']
 matrix={x['name'].split('-')[1]:x for x in rows if x['name'].endswith('matrix')};base=matrix['performance']['score']
 for mode,cap in [('performance',90),('balanced',38),('eco',20)]:
  x=matrix[mode];assert x['limits']=={'limitC':[90.0],'apuLimitW':[float(cap)]}
  print(f"{mode}: {x['socketW']:.2f} W, {100*x['score']/base:.2f}% CPU throughput retained, {x['meanCpuC']:.2f} C")
 assert abs(100*(1-matrix['balanced']['score']/base)-19.04)<.01
 assert abs(100*(1-matrix['eco']['score']/base)-43.22)<.01
 life=load('2026-10-26/lifecycle.json');assert all(life[k] for k in ['fullResetPassed','reEnablePassed','automaticRestartPreservedOwnership']);assert life['resetBoost']==1 and life['resetUnitEnabled']=='disabled'
 print('Evidence arithmetic and saved workload invariants passed. No hardware test was run.')
if __name__=='__main__':main()
