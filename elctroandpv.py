import pypsa
import pandas as pd
import numpy as np

# -----------------------------
# Create a minimal working network
# -----------------------------
n = pypsa.Network()

# Buses
n.add("Bus", "electricity")
n.add("Bus", "hydrogen")

# -----------------------------
# PV generator (62 kW)
# -----------------------------
n.add("Generator", "PV",
      bus="electricity",
      p_nom=62,
      marginal_cost=0)

# -----------------------------
# Slack grid (makes model feasible)
# -----------------------------
n.add("Generator", "Grid",
      bus="electricity",
      p_nom=1e6,
      marginal_cost=100)   # expensive → only used when PV cannot supply

# -----------------------------
# Electrolyzer (electricity → H2)
# -----------------------------
n.add("Link", "Electrolyzer",
      bus0="electricity",
      bus1="hydrogen",
      efficiency=0.7,
      p_nom=62,
      marginal_cost=1)      # electrolyzer has cost > PV

# Prevent reverse flow
n.links.at["Electrolyzer", "p_min_pu"] = 0

# -----------------------------
# Hydrogen storage
# -----------------------------
n.add("Store", "H2_Tank",
      bus="hydrogen",
      e_nom=200,
      e_initial=0,
      e_cyclic=False)

# -----------------------------
# Hydrogen demand
# -----------------------------
n.add("Load", "H2_Demand",
      bus="hydrogen",
      p_set=0.3)           # must produce H2

# -----------------------------
# Simple 48h PV profile
# -----------------------------
snapshots = pd.date_range("2025-01-01", periods=48, freq="h")
hours = np.arange(48)
pv_profile = np.maximum(0, np.sin(2 * np.pi * (hours % 24) / 24))

n.set_snapshots(snapshots)
n.generators_t.p_max_pu.loc[:, "PV"] = pv_profile

# -----------------------------
# Solve
# -----------------------------
n.optimize(solver_name="highs")

# -----------------------------
# Results
# -----------------------------
print("\n=== RESULTS ===")
print("Total PV production (MWh):", n.generators_t.p["PV"].sum())
print("H2 Production (MWh):", n.links_t.p1["Electrolyzer"].sum())
print("Final H2 storage:", n.stores_t.e["H2_Tank"].iloc[-1])

print("\nPV output sample:")
print(n.generators_t.p["PV"].head())

print("\nElectrolyzer output sample:")
print(n.links_t.p1["Electrolyzer"].head())
