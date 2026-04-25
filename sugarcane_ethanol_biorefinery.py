# sugarcane_ethanol_biorefinery.py
# Extracted example: sugarcane-to-ethanol biorefinery using BioSTEAM
# (See original notebook for full narrative and additional cells.)

import argparse
import warnings
import io

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import biosteam as bst
from biosteam import units
import numpy as np

# Minimal helpers and setup (truncated from original full script)

def show_gv_with_matplotlib(digraph, title=None):
    if digraph is None:
        print("[Diagram note] BioSTEAM did not return a Graphviz object (None).")
        return
    try:
        digraph.graph_attr["bgcolor"] = "white"
        png_bytes = digraph.pipe(format="png")
        buf = io.BytesIO(png_bytes)
        img = mpimg.imread(buf, format="png")
        plt.figure(figsize=(16, 4))
        if title:
            plt.title(title)
        plt.imshow(img)
        plt.axis("off")
    except Exception as e:
        print("[Diagram display error] Could not render diagram via Graphviz.")
        print(" - Ensure 'dot -V' works and 'python-graphviz' is installed.")
        print(f" - Details: {e}")

# For full flowsheet, refer to the original notebook in the workspace:
# BioSTEAM/Sugarcane_ethanol_biorefinery.ipynb

if __name__ == '__main__':
    print('This is a compact entrypoint for the sugarcane biorefinery example.')
    print('See BioSTEAM/Sugarcane_ethanol_biorefinery.ipynb for the full case study.')
