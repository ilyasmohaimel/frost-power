"""Draw the README comparison and the laptop's original measurement display."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties,fontManager
R=Path(__file__).resolve().parents[2];A=R/'media/composition/assets';F=A/'fonts';F.mkdir(parents=True,exist_ok=True)
for p in F.glob('*.ttf'):fontManager.addfont(str(p))
regular=FontProperties(fname=str(F/'Barlow-Regular.ttf'));medium=FontProperties(fname=str(F/'Barlow-Medium.ttf'));condensed=FontProperties(fname=str(F/'BarlowCondensed-SemiBold.ttf'))
BG='#161b21';FG='#f3f5f7';MUTED='#aab4c2';COLORS=['#aab4c2','#96baff','#a8d5bf']
rows=json.loads((R/'data/2026-10-26/installed-results.json').read_text());m={x['name'].split('-')[1]:x for x in rows if x['name'].endswith('matrix')};order=['performance','balanced','eco'];base=m['performance']['score']
plt.rcParams.update({'font.family':'Barlow','svg.fonttype':'path','axes.facecolor':BG,'figure.facecolor':BG,'savefig.facecolor':BG,'text.color':FG,'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':FG})
fig,axes=plt.subplots(1,3,figsize=(14,5.4),gridspec_kw={'wspace':.42});fig.subplots_adjust(left=.13,right=.94,top=.72,bottom=.22)
metrics=[('CPU socket power','W',[m[k]['socketW'] for k in order],85),('CPU throughput','% retained',[100*m[k]['score']/base for k in order],112),('Mean CPU temperature','°C',[m[k]['meanCpuC'] for k in order],105)]
for i,(ax,(title,unit,values,maximum)) in enumerate(zip(axes,metrics)):
 ax.barh([2,1,0],values,height=.48,color=COLORS);ax.set_xlim(0,maximum);ax.set_ylim(-.6,2.65);ax.set_yticks([2,1,0],['Performance','Balanced','Eco'] if i==0 else []);ax.tick_params(axis='both',length=0,labelsize=13,pad=12);ax.set_xticks([])
 for spine in ax.spines.values():spine.set_visible(False)
 for y,v,c in zip([2,1,0],values,COLORS):ax.text(v+maximum*.035,y,f'{v:.2f}',va='center',fontproperties=medium,fontsize=15,color=FG)
 ax.set_title(title+'\n'+unit,loc='left',pad=23,fontproperties=medium,fontsize=17,color=FG)
fig.text(.045,.9,'The same workload. Three power choices.',fontproperties=medium,fontsize=25)
fig.text(.045,.075,'60 s verified matrix • cooler • barrel power • iGPU session • tuned Performance baseline',fontproperties=regular,fontsize=12,color=MUTED)
fig.savefig(R/'assets/measurements.svg',metadata={'Date':None});plt.close(fig)
p=R/'assets/measurements.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
fig=plt.figure(figsize=(19.2,10.8),dpi=100);ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1920);ax.set_ylim(1080,0);ax.axis('off')
ax.text(110,135,'Frost Power',fontproperties=medium,fontsize=56,color=FG)
ax.text(110,205,'Measured presets / Ryzen 9 5900HX',fontproperties=regular,fontsize=25,color=MUTED)
for y,label,v,c,throughput in zip([370,575,780],['Performance','Balanced','Eco'],[m[k]['socketW'] for k in order],COLORS,[100*m[k]['score']/base for k in order]):
 ax.text(110,y,label,fontproperties=medium,fontsize=32,color=c);ax.barh(y+50,v/80*1200,height=26,left=110,color=c);ax.text(1710,y+45,f'{v:.2f} W',ha='right',fontproperties=condensed,fontsize=60,color=FG);ax.text(1710,y+95,f'{throughput:.2f}% CPU throughput',ha='right',fontproperties=regular,fontsize=22,color=MUTED)
ax.text(110,1000,'60 s matrix / cooler / barrel power / iGPU session',fontproperties=regular,fontsize=23,color=MUTED)
fig.savefig(A/'measurement-screen.png',dpi=100);plt.close(fig)
print('Measurement figure and display texture drawn from published JSON.')
