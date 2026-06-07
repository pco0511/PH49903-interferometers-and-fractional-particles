"""Stack the original Supp. Fig. 5 (extracted from the PDF) above our
reproduction so they can be compared directly."""
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

FIG = Path(__file__).parent / 'figures'
orig = mpimg.imread(FIG / 'supp-fig5.png')
repro = mpimg.imread(FIG / 'repro-supp-fig5.png')

fig, axs = plt.subplots(2, 1, figsize=(12, 11))
axs[0].imshow(orig)
axs[0].set_title('ORIGINAL  -  Supp. Fig. 5 (Nakamura et al. 2020)', fontsize=12)
axs[1].imshow(repro)
axs[1].set_title('REPRODUCTION  -  reproduce_simulation.py', fontsize=12)
for ax in axs:
    ax.axis('off')
fig.tight_layout()
out = FIG / 'compare-supp-fig5.png'
fig.savefig(out, dpi=130, bbox_inches='tight')
print(f'saved -> {out}')
