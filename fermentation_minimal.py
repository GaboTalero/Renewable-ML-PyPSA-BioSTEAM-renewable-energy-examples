# fermentation_minimal.py
# A tiny, self-contained BioSTEAM example for a "fermentation" unit.

import biosteam as bst
from thermosteam import Chemical, Chemicals

# -----------------------------
# 1) Define chemicals & thermo
# -----------------------------
# Core species for simple glucose fermentation: C6H12O6 -> 2 C2H5OH + 2 CO2
chemicals = Chemicals([
    Chemical('Water', phase='l'),
    Chemical('Glucose', phase='l'),
    Chemical('Ethanol', phase='l'),
    Chemical('CO2', phase='g'),
])


# Set a default thermodynamic package for the flowsheet
bst.settings.set_thermo(chemicals, cache=True)

# -----------------------------
# 2) Define a minimal unit op
# -----------------------------
class SimpleFermenter(bst.Unit):
    """
    Minimal demonstration fermenter:
    - 1 inlet, 1 outlet
    - Applies a single stoichiometric reaction with given conversion
    - Sets outlet temperature; no energy balance or sizing (for simplicity)
    """
    _N_ins = 1
    _N_outs = 1
    line = "Simple Fermenter"

    # Default parameters
    def __init__(self, ID='', ins=None, outs=(), T=303.15, X_glc=0.90, form_biomass=False):
        super().__init__(ID, ins, outs)
        self.T = float(T)               # outlet temperature [K]
        self.X_glc = float(X_glc)       # glucose conversion (0-1)
        self.form_biomass = bool(form_biomass)

        # Stoichiometric reaction (mass basis handled internally by BioSTEAM)
        # Reaction is written on a molar basis as a string; BioSTEAM parses it.
        # Here, we model classic ethanol fermentation (no biomass sink).
        # You can add a biomass yield variant below if desired.
        self.ethanol_rxn = bst.Reaction('Glucose -> 2 Ethanol + 2 CO2', 'Glucose', X=self.X_glc)

        # Optional: divert some glucose to biomass (very rough)
        # e.g., 5% of converted glucose to "Biomass"
        self.biomass_rxn = bst.Reaction('Glucose -> Biomass', 'Glucose', X=0.05 * self.X_glc) if form_biomass else None

    def _run(self):
        feed = self.ins[0]
        broth = self.outs[0]

        # Copy inlet → outlet, set temperature
        broth.copy_like(feed)
        broth.T = self.T

        # Apply reactions on the OUTLET stream (in place)
        if self.form_biomass and self.biomass_rxn is not None:
            # First, create biomass from a fraction of glucose
            self.biomass_rxn(broth)
            # Then convert remaining glucose to ethanol + CO2
            # Adjust ethanol reaction conversion to account for glucose already consumed
            # Remaining glucose fraction:
            glc_in = feed.imass['Glucose'] if 'Glucose' in feed.imass.index else 0.0
            glc_out_before = broth.imass['Glucose']
            if glc_in > 0:
                # Effective remaining conversion target
                remaining_target = max(self.X_glc - (1.0 - glc_out_before / max(glc_in, 1e-12)), 0.0)
            else:
                remaining_target = 0.0
            self.ethanol_rxn.X = remaining_target
            self.ethanol_rxn(broth)
        else:
            # Only ethanol reaction
            self.ethanol_rxn.X = self.X_glc
            self.ethanol_rxn(broth)

    # No design or costing here—kept intentionally minimal


# -----------------------------
# 3) Build a tiny flowsheet
# -----------------------------
def build_and_run():
    # Define a feed stream: dilute glucose solution
    # Units are mass flow unless specified; here 1000 kg/h water + 50 kg/h glucose.
    feed = bst.Stream(
        'feed',
        Water=1000, Glucose=50,  # kg/h
        units='kg/hr',
        T=303.15, P=101325,
    )

    # Instantiate the fermenter
    F1 = SimpleFermenter(
        'F1',
        ins=feed,
        outs=('broth',),
        T=303.15,
        X_glc=0.90,
        form_biomass=False   # <-- turn off biomass sink
    )


    # Simulate (very light—no recycle, no system object required)
    F1.simulate()

    # Results
    broth = F1.outs[0]
    print("\n=== SIMPLE FERMENTATION RESULTS ===")
    broth.show()  # pretty print composition, T, P, etc.

    # Quick mass balance check (glucose consumption)
    glc_in = feed.imass['Glucose']
    glc_out = broth.imass['Glucose']
    print(f"\nGlucose in  : {glc_in:8.3f} kg/h")
    print(f"Glucose out : {glc_out:8.3f} kg/h")
    print(f"Consumed    : {glc_in - glc_out:8.3f} kg/h")

    # Ethanol and CO2 production
    EtOH = broth.imass['Ethanol']
    CO2  = broth.imass['CO2']
    print(f"Ethanol out : {EtOH:8.3f} kg/h")
    print(f"CO2 out     : {CO2:8.3f} kg/h")

if __name__ == "__main__":
    build_and_run()
