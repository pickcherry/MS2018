import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 网页标题与说明
st.title("Quantum Mechanism: Extended Zone Scheme")
st.markdown("""
通过调节滑块观察势垒强度 $\mu$ 如何影响能带裂解，以及电子如何在能带中填充。
[公式参考：$f(Ka) = \cos(Ka) + \mu \\frac{\sin(Ka)}{Ka}$]
""")

# 侧边栏滑块
mu = st.sidebar.slider("Barrier Strength (μ)", 0.0, 20.0, 3.0)
ef = st.sidebar.slider("Fermi Level (Ef)", 0.0, 45.0, 15.0)

# 物理逻辑计算 (与之前相同)
a = 1.0
hbar = 1.0
me = 1.0

def get_data(mu, ef):
    Ka = np.linspace(0.001, 3.0 * np.pi, 2000)
    f_vals = np.cos(Ka) + mu * np.sin(Ka) / Ka
    mask_allowed = np.abs(f_vals) <= 1
    E = (hbar**2 * Ka**2) / (2 * me * a**2)
    
    k_ext = []
    for i in range(len(Ka)):
        zone_n = int(np.ceil(Ka[i] / np.pi))
        if np.abs(f_vals[i]) <= 1:
            inner_k = np.arccos(f_vals[i])
            k_val = ((zone_n - 1) * np.pi + inner_k) if zone_n % 2 == 1 else (zone_n * np.pi - inner_k)
        else:
            k_val = np.nan
        k_ext.append(k_val / a)
        
    k_full = np.concatenate([-np.array(k_ext)[::-1], k_ext])
    E_full = np.concatenate([E[::-1], E])
    mask_full = np.concatenate([mask_allowed[::-1], mask_allowed])
    filled = (E_full <= ef) & mask_full & (~np.isnan(k_full))
    return Ka, f_vals, k_full, E_full, mask_full, filled

Ka, f, k, E, mask, filled = get_data(mu, ef)

# 绘图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# KP Criterion
ax1.plot(Ka, f, 'b')
ax1.axhline(1, color='r', ls='--'); ax1.axhline(-1, color='r', ls='--')
ax1.fill_between(Ka, -1, 1, where=np.abs(f)<=1, color='green', alpha=0.2)
ax1.set_ylabel(r"$f(Ka) = \cos(Ka) + \mu \frac{\sin(Ka)}{Ka}$")
ax1.set_title("1. KP Criterion")

# Extended Zone
ax2.plot(k, np.where(mask, E, np.nan), 'black', lw=2)
ax2.scatter(k[filled], E[filled], color='blue', s=5)
ax2.axhline(ef, color='orange', ls='--')
ax2.set_ylim(0, 50)
ax2.set_title("2. Extended Zone Filling")

st.pyplot(fig)
