import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="Quantum Mechanics for Semiconductors", layout="wide")

st.title("Quantum Mechanism for Semiconductors: Band Theory")
st.markdown("""
This interactive tool demonstrates the **Kronig-Penney Model**. It visualizes how a periodic potential creates energy bands and gaps, and how electrons fill these states.
""")

# Sidebar Controls
st.sidebar.header("Parameters")
mu = st.sidebar.slider("Barrier Strength (μ)", 0.0, 20.0, 3.0, help="Higher μ represents stronger binding of electrons to ions.")
ef = st.sidebar.slider("Fermi Level (Ef)", 0.0, 45.0, 15.0, help="Adjust the total number of electrons in the system.")

# Physical Constants (Normalized)
a = 1.0        # Lattice constant
hbar = 1.0     # Normalized Planck constant
me = 1.0       # Electron mass

def get_kp_data(mu, ef):
    """Calculates the KP criterion and Extended Zone Scheme data."""
    # Ka: wavevector inside the potential well
    Ka = np.linspace(0.001, 3.0 * np.pi, 2500)
    # f(Ka) = cos(Ka) + mu * sin(Ka)/(Ka) [cite: 155, 172]
    f_vals = np.cos(Ka) + mu * np.sin(Ka) / Ka
    
    # Identify Allowed Zones (|f(Ka)| <= 1) [cite: 174]
    mask_allowed = np.abs(f_vals) <= 1
    # Energy E = (hbar^2 * Ka^2) / (2 * me * a^2) [cite: 154, 291]
    E = (hbar**2 * Ka**2) / (2 * me * a**2)
    
    # Map to Extended Zone Scheme k [cite: 171, 178]
    k_extended = []
    for i in range(len(Ka)):
        val_ka = Ka[i]
        val_f = f_vals[i]
        zone_n = int(np.ceil(val_ka / np.pi))
        
        if np.abs(val_f) <= 1:
            inner_k = np.arccos(val_f)
            # Mapping based on Brillouin Zone index [cite: 156, 175]
            if zone_n % 2 == 1: k_val = (zone_n - 1) * np.pi + inner_k
            else:               k_val = zone_n * np.pi - inner_k
        else:
            k_val = np.nan # Forbidden Gap [cite: 174]
        k_extended.append(k_val / a)
        
    k_ext = np.array(k_extended)
    # Mirror for negative k values
    k_full = np.concatenate([-k_ext[::-1], k_ext])
    E_full = np.concatenate([E[::-1], E])
    mask_full = np.concatenate([mask_allowed[::-1], mask_allowed])
    
    # Determine Filling Status (Red Electrons)
    valid = ~np.isnan(k_full)
    filled_mask = (E_full <= ef) & mask_full & valid
    
    return Ka, f_vals, k_full, E_full, mask_full, filled_mask

# Execute Data Calculation
Ka, f, k, E, mask, filled = get_kp_data(mu, ef)

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Kronig-Penney Criterion
ax1.plot(Ka, f, color='blue', lw=2, label=r'$f(Ka)$')
ax1.axhline(1, color='black', linestyle='--', alpha=0.5)
ax1.axhline(-1, color='black', linestyle='--', alpha=0.5)
ax1.fill_between(Ka, -1, 1, where=np.abs(f)<=1, color='green', alpha=0.15, label='Allowed Zone')

ax1.set_xlim(0, 3*np.pi)
ax1.set_ylim(-3, 8)
ax1.set_xlabel(r"$Ka$ (Wavevector in Potential Well)", fontsize=11)
ax1.set_ylabel(r"$f(Ka) = \cos(Ka) + \mu \frac{\sin(Ka)}{Ka}$", fontsize=13)
ax1.set_title("1. Kronig-Penney Criterion", fontsize=14)
ax1.legend(loc='upper right')
ax1.grid(alpha=0.2)

# Plot 2: Extended Zone Scheme
# Plot Allowed Bands
ax2.plot(k, np.where(mask, E, np.nan), color='black', lw=3, label='Allowed Bands')

# Plot Filled Electrons (Changed to RED)
ax2.scatter(k[filled], E[filled], color='red', s=7, label='Filled Electrons', zorder=5)

# Fermi Level Line
ax2.axhline(ef, color='orange', linestyle='--', lw=1.5, label=r'Fermi Level $E_F$')

ax2.set_xlim(-3*np.pi/a, 3*np.pi/a)
ax2.set_ylim(0, 50)
ax2.set_xlabel(r"Crystal Momentum $k$", fontsize=11)
ax2.set_ylabel("Energy $E$", fontsize=11)
ax2.set_title("2. Extended Zone Scheme Filling", fontsize=14)
ax2.grid(True, alpha=0.2)
ax2.legend(loc='upper right')

# Render Plot in Streamlit
st.pyplot(fig)

# Educational Summary
st.subheader("Physics Insights")
cols = st.columns(3)
with cols[0]:
    st.info("**Metal**: Partially filled bands allow easy electron movement.") [cite: 194]
with cols[1]:
    st.info("**Insulator**: Completely filled valence band with a large gap.") [cite: 196]
with cols[2]:
    st.info("**Semiconductor**: Completely filled band with a small gap.") [cite: 195]
