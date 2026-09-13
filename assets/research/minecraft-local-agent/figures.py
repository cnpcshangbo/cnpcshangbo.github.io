"""Portable research-note figure generator.

Reads only figure-inputs.json beside this file. It never contacts Minecraft.
Install requirements.txt, then run: python figures.py --output rendered
Add --no-video to skip the optional MP4 reconstruction.
"""
from pathlib import Path
import argparse
import json
import os

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent / 'rendered',
                    help='Output directory (default: rendered beside this script).')
parser.add_argument('--no-video', action='store_true', help='Generate four SVG/PNG figures only.')
args = parser.parse_args()
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT = args.output.resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(OUTPUT / '.matplotlib'))
data = json.loads((SCRIPT_DIR / 'figure-inputs.json').read_text(encoding='utf-8'))
if data.get('schemaVersion') != 1:
    raise ValueError('Unsupported figure-inputs.json schemaVersion')

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
from matplotlib.lines import Line2D

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11,
    'svg.fonttype': 'none', 'svg.hashsalt': 'wood-agent-note',
    'axes.titleweight': 'bold', 'axes.labelcolor': '#17212B',
    'text.color': '#17212B', 'axes.edgecolor': '#B8C2CC',
    'xtick.color': '#465665', 'ytick.color': '#465665',
    'savefig.facecolor': 'white', 'figure.facecolor': 'white',
})
BLUE, TEAL, ORANGE = '#0072B2', '#009E73', '#D55E00'
INK, MUTED, LIGHT = '#17212B', '#526370', '#EDF2F6'

observations = data['observations']
scenarios = data['scenarios']
route = np.asarray(observations['routeBlockXZ'], dtype=float) + .5
tree = np.asarray(observations['recoveryTreeBlockBasesXZ'], dtype=float) + .5
home = np.asarray(observations['homeXZ'], dtype=float)
stop = np.asarray(observations['finalStopXZ'], dtype=float)
mission = {'radius': observations['protectedRadiusBlocks']}
last = {'collectedLogs': observations['newInventoryLogs'],
        'homeDistance': observations['reportedHomeDistanceBlocks']}
audit = {'diagnosticWindow': observations['diagnosticWindow']}

def save(fig, name):
    fig.savefig(OUTPUT / f'{name}.svg', bbox_inches='tight', metadata={'Date': None})
    fig.savefig(OUTPUT / f'{name}.png', dpi=200, bbox_inches='tight')
    plt.close(fig)

def title(fig, heading, subheading):
    fig.text(.055, .958, heading, fontsize=20, weight='bold', va='top')
    fig.text(.055, .906, subheading, fontsize=11, color=MUTED, va='top')

def box(ax, xy, width, height, heading, body, color):
    x, y = xy
    ax.add_patch(FancyBboxPatch((x, y), width, height,
                               boxstyle='round,pad=0.010,rounding_size=0.018',
                               facecolor='white', edgecolor=color, linewidth=1.7))
    ax.text(x + width/2, y + height*.72, heading, ha='center', va='center',
            fontsize=12, weight='bold', color=color)
    ax.text(x + width/2, y + height*.32, body, ha='center', va='center',
            fontsize=10, linespacing=1.5)

def arrow(ax, start, end, label=None, color=MUTED, label_xy=None, rad=0):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle='-|>', mutation_scale=12,
                                color=color, linewidth=1.5,
                                connectionstyle=f'arc3,rad={rad}'))
    if label:
        xy = label_xy or ((start[0]+end[0])/2, (start[1]+end[1])/2+.025)
        ax.text(*xy, label, fontsize=9, color=color, ha='center', va='bottom',
                bbox=dict(facecolor='white', edgecolor='none', pad=1.5))

def architecture():
    fig = plt.figure(figsize=(14, 8.2))
    title(fig, 'The architecture changed both cadence and access',
          'Conceptual comparison of screenshot-driven control and the local wood collector')
    ax = fig.add_axes([.055, .15, .89, .70]); ax.set(xlim=(0,1), ylim=(0,1)); ax.axis('off')
    ax.text(0, .98, 'A  DIRECT LLM CONTROL', color=BLUE, weight='bold', fontsize=12)
    xs = [.015, .275, .535, .795]
    for x, h, b in zip(xs, ['Screenshot', 'LLM', 'Desktop input', 'Minecraft'],
                       ['Rendered pixels', 'Interpret scene\nChoose next action',
                        'Timed keys / mouse\nBounded input pulse', 'World and\ncurrent player']):
        box(ax, (x,.63), .19, .21, h, b, BLUE)
    for a,b in zip(xs[:-1],xs[1:]): arrow(ax,(a+.20,.735),(b-.01,.735))
    ax.plot([.89,.89,.11,.11],[.85,.905,.905,.85], color=BLUE, lw=1.3)
    arrow(ax,(.11,.90),(.11,.845),color=BLUE)
    ax.text(.50,.904,'New rendered observation',ha='center',va='center',fontsize=9,
            color=BLUE,bbox=dict(facecolor='white',edgecolor='none',pad=2))

    ax.text(0, .515, 'B  LOCAL EXECUTION WITH ASTRA SUPERVISION', color=TEAL,
            weight='bold', fontsize=12)
    box(ax,(.015,.175),.24,.235,'Astra engineer / supervisor',
        'Build and revise controller\nSet goals, inspect, stop',TEAL)
    box(ax,(.380,.175),.24,.235,'Deterministic local worker',
        'Configured 50 ms scheduler\nState machine + safety gates',TEAL)
    box(ax,(.745,.175),.24,.235,'In-process game API',
        'Structured client state\nMovement + survival mining',TEAL)
    arrow(ax,(.265,.335),(.370,.335),'Commands',TEAL,label_xy=(.317,.35))
    arrow(ax,(.370,.24),(.265,.24),'Status / logs',TEAL,label_xy=(.317,.175))
    arrow(ax,(.630,.335),(.735,.335),'Actions',TEAL,label_xy=(.682,.35))
    arrow(ax,(.735,.24),(.630,.24),'Game state',TEAL,label_xy=(.682,.175))
    ax.text(.505,.06,'Privileged observation: blocks, position, inventory and client state',
            ha='center',fontsize=10,color=TEAL)
    fig.text(.055,.096,'Observation confound',fontsize=12,weight='bold')
    fig.text(.055,.061,'Pixels become structured state; desktop input becomes an in-process API. '
             'This is not an isolated test of model speed.',fontsize=10.5)
    fig.text(.055,.025,'“Privileged” means access to game internals, not elevated operating-system permissions.',
             fontsize=9,color=MUTED)
    save(fig,'01-control-architecture')

def cadence():
    fig = plt.figure(figsize=(11.8,7.2))
    title(fig,'Nominal cadence: illustrative sensitivity scenarios',
          'Assumed LLM cycle interval compared with a configured 50 ms local scheduler')
    ax=fig.add_axes([.12,.25,.82,.57])
    intervals=np.asarray(scenarios['assumedLlmIntervalsSeconds']); ratios=intervals/scenarios['nominalSchedulerDelaySeconds']
    bars=ax.bar(np.arange(4),ratios,width=.56,color=BLUE)
    for b,v in zip(bars,ratios):
        ax.text(b.get_x()+b.get_width()/2,v+9,f'{v:.0f}×',ha='center',weight='bold',fontsize=16)
    ax.set_xticks(np.arange(4),[f'{t} s' for t in intervals])
    ax.set_ylim(0,460); ax.set_yticks(np.arange(0,401,100))
    ax.set_ylabel('Nominal local dispatch opportunities\nper assumed LLM cycle',labelpad=13)
    ax.set_xlabel('Assumed interval between LLM control cycles',labelpad=12)
    ax.grid(axis='y',alpha=.22); ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    fig.text(.055,.14,'SCENARIOS — NOT MEASURED TASK SPEEDUP',color=ORANGE,fontsize=13,weight='bold')
    fig.text(.055,.095,'Ratio = assumed LLM interval ÷ 0.05 s. A dispatch opportunity is not a completed game action.',fontsize=10.5)
    diagnostic = audit['diagnosticWindow']
    fig.text(.055,.053,f'Short diagnostic trace: {diagnostic["observedGameTicksAdvanced"]} game ticks / '
             f'{diagnostic["observedSpanSeconds"]:.2f} s = {diagnostic["observedGameTickRateHz"]:.2f} game ticks/s.',
             fontsize=10,color=MUTED)
    fig.text(.055,.029,'This measures the game clock, not worker invocation timing or end-to-end task performance.',fontsize=10,color=MUTED)
    save(fig,'02-nominal-cadence-scenarios')

def draw_plan(ax,detail=False):
    ax.add_patch(Circle(home,mission['radius'],facecolor=TEAL,alpha=.075,edgecolor='none'))
    ax.add_patch(Circle(home,mission['radius'],fill=False,edgecolor=TEAL,linestyle='--',lw=1.4))
    ax.plot(route[:,0],route[:,1],color=BLUE,lw=1.25 if detail else 1,alpha=.9,zorder=3)
    ax.scatter(*home,marker='s',s=48,c=INK,zorder=5)
    ax.scatter(route[0,0],route[0,1],marker='o',s=45,facecolors='white',edgecolors=BLUE,lw=1.8,zorder=6)
    ax.scatter(tree[:,0],tree[:,1],marker='^',s=72 if detail else 50,color=TEAL,
               edgecolors='white',linewidths=.8,zorder=7)
    ax.scatter(*stop,marker='X',s=125 if detail else 85,c=ORANGE,
               edgecolors='white',linewidths=.8,zorder=8)
    if detail:
        offsets=[(-24,9),(-30,8),(-27,1),(8,-9)]
        for i,(p,off) in enumerate(zip(tree,offsets),1):
            ax.annotate(f'T{i}',p,xytext=off,textcoords='offset points',color=TEAL,
                        weight='bold',fontsize=10)
        ax.annotate('Final stop',stop,xytext=(12,-24),textcoords='offset points',color=ORANGE,
                    fontsize=10,weight='bold',arrowprops=dict(arrowstyle='-',color=ORANGE))
        ax.set_xlim(-680,-580);ax.set_ylim(408,344)
    else:
        ax.set_xlim(-843,-543); ax.set_ylim(418,51)
        ax.annotate('Home reference',home,xytext=(-93,-24),textcoords='offset points',fontsize=9)
        ax.annotate('128-block protected radius',(-804,264),xytext=(-11,15),textcoords='offset points',
                    color=TEAL,fontsize=9,rotation=-21)
        ax.add_patch(Rectangle((-680,344),100,64,fill=False,lw=.9,edgecolor=MUTED))
    ax.set_aspect('equal',adjustable='box')
    ax.set_xlabel('Minecraft X (blocks)'); ax.set_ylabel('Minecraft Z (blocks; south increases downward)')
    ax.grid(alpha=.18);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False)

def route_figure():
    fig=plt.figure(figsize=(13,9.2))
    title(fig,'Recorded breadcrumbs and the final return stop',
          f'{len(route)} saved entries • Plan view of coordinates, not a terrain map')
    ax=fig.add_axes([.065,.155,.46,.69]); draw_plan(ax)
    detail=fig.add_axes([.58,.49,.365,.32]);draw_plan(detail,True)
    detail.set_title('Recovery area detail',loc='left',fontsize=13,pad=12)
    detail.set_ylabel('Z (blocks)');detail.set_xlabel('X (blocks)')
    note=fig.add_axes([.575,.155,.38,.255]);note.axis('off')
    handles=[Line2D([],[],color=BLUE,lw=2,label='Saved breadcrumb order'),
             Line2D([],[],color=INK,marker='s',linestyle='none',label='Home reference'),
             Line2D([],[],color=BLUE,marker='o',markerfacecolor='white',linestyle='none',label='First saved breadcrumb'),
             Line2D([],[],color=TEAL,marker='^',linestyle='none',label='Four recovery tree bases'),
             Line2D([],[],color=ORANGE,marker='X',linestyle='none',label='Final stop during return')]
    note.legend(handles=handles,loc='upper left',frameon=False,fontsize=10,handlelength=2,labelspacing=.75)
    note.text(0,-.05,f'Final snapshot: {last["collectedLogs"]} new logs; return incomplete.\n'
              f'Health-change stop; reported home distance: {last["homeDistance"]:.1f} blocks.',
              fontsize=10,color=INK,linespacing=1.55)
    fig.text(.065,.065,'The saved sequence has no timestamps and does not record the return leg. '
             'Only the final return stop is plotted.',fontsize=10.5)
    fig.text(.065,.035,'Breadcrumbs and tree bases use block centers (X + 0.5, Z + 0.5); '
             'the stop uses the recorded continuous position. Height is omitted.',fontsize=9.5,color=MUTED)
    save(fig,'03-recorded-route')

def amortization():
    fig=plt.figure(figsize=(11.5,7.4))
    title(fig,'Setup amortization depends on two unmeasured quantities',
          'Illustrative break-even task counts; setup costs and per-task savings below are assumptions')
    ax=fig.add_axes([.22,.26,.7,.50])
    setup=np.asarray(scenarios['assumedSetupMinutes'])*60
    saving=np.asarray(scenarios['assumedPerTaskSavingsSeconds'])
    n=np.ceil(setup[:,None]/saving[None,:]).astype(int)
    ax.imshow(np.log10(n),cmap='Blues',vmin=0,vmax=3.65,aspect='auto')
    for (i,j),v in np.ndenumerate(n):
        ax.text(j,i,f'{v:,}',ha='center',va='center',weight='bold',fontsize=18,
                color='white' if np.log10(v)>2.2 else INK)
    ax.set_xticks(range(4),['5 s','15 s','60 s','300 s'])
    ax.set_yticks(range(3),['15 min','60 min','180 min'])
    ax.set_xlabel('Assumed time saved per subsequent task',labelpad=13)
    ax.set_ylabel('Assumed one-time setup cost',labelpad=13)
    ax.tick_params(length=0)
    ax.set_xticks(np.arange(-.5,4,1),minor=True);ax.set_yticks(np.arange(-.5,3,1),minor=True)
    ax.grid(which='minor',color='white',lw=2);ax.tick_params(which='minor',length=0)
    fig.text(.055,.155,'Break-even task count = ceiling(setup cost ÷ time saved per task)',fontsize=13,weight='bold')
    fig.text(.055,.102,'ILLUSTRATIVE SCENARIOS — NO MEASURED BREAK-EVEN CLAIM',fontsize=12,color=ORANGE,weight='bold')
    fig.text(.055,.055,'Assumes positive, constant time savings and excludes maintenance. Neither input was established by this case.',
             fontsize=10,color=MUTED)
    save(fig,'04-illustrative-amortization')

def replay():
    import imageio.v2 as imageio
    fig,ax=plt.subplots(figsize=(10.8,7.2),dpi=100)
    fig.subplots_adjust(left=.10,right=.72,bottom=.12,top=.84)
    draw_plan(ax)
    ax.texts[0].xyann = (-95, 15)
    # Replace the full route with a reveal of saved order, not inferred travel time.
    ax.lines[0].set_visible(False)
    trail,=ax.plot([],[],color=BLUE,lw=1.5,zorder=4)
    head,=ax.plot([],[],marker='o',color=BLUE,markersize=5,zorder=9)
    fig.text(.06,.955,'RECONSTRUCTION, NOT GAMEPLAY',weight='bold',fontsize=16)
    fig.text(.06,.915,'Uniform step timing is illustrative; the saved sequence has no timestamps.',fontsize=11)
    fig.text(.755,.74,'Saved breadcrumb\norder only',color=BLUE,weight='bold',fontsize=12,linespacing=1.5)
    counter=fig.text(.755,.64,'',fontsize=12)
    fig.text(.755,.57,'The return leg\nwas not recorded.\nThe orange X marks\nonly the final stop.',
             fontsize=11,linespacing=1.6,va='top')
    fig.text(.755,.30,'Green triangles:\nrecovery tree bases.\n\nNot a terrain map.\nHeight omitted.',
             fontsize=10,color=MUTED,linespacing=1.5,va='top')
    indices=np.linspace(1,len(route),140).astype(int)
    with imageio.get_writer(OUTPUT/'05-breadcrumb-reconstruction.mp4',fps=10,
                            codec='libx264',quality=8,macro_block_size=2) as writer:
        for k in list(indices)+[len(route)]*20:
            trail.set_data(route[:k,0],route[:k,1]);head.set_data([route[k-1,0]],[route[k-1,1]])
            counter.set_text(f'Entry {k} / {len(route)}')
            fig.canvas.draw()
            writer.append_data(np.asarray(fig.canvas.buffer_rgba())[:,:,:3])
    fig.savefig(OUTPUT/'05-breadcrumb-reconstruction-poster.png',dpi=150)
    plt.close(fig)

if __name__ == '__main__':
    architecture()
    cadence()
    route_figure()
    amortization()
    if not args.no_video:
        replay()
    print(f'Wrote four SVG/PNG figures and {"no video" if args.no_video else "the optional reconstruction video"}.')
