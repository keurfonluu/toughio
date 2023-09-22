import numpy as np
import matplotlib.pyplot as plt


def permeability(porosity, phi_r=0.8, Gamma=0.8):
    theta = (porosity - phi_r) / (1.0 - phi_r)
    omega = 1.0 + (1.0 / Gamma) / (1.0 / phi_r - 1.0)

    return theta**2 * (1.0 - Gamma + Gamma / omega**2) / (1.0 - Gamma + Gamma * (theta / (theta + omega - 1.0))**2)


# Calculate porosity-permeability relationship
phi = np.linspace(0.80, 1.0, 201)
k = permeability(phi)

# Plot figure
style = {
    "font.size": 20,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
}
plt.rcParams.update(style)

fig, ax = plt.subplots(1, 1, figsize=(8, 6))
ax.plot(phi, k, c="black", lw=2)
ax.set_xlabel("$\phi / \phi_0$")
ax.set_ylabel("$k / k_0$")
ax.set_xlim(phi.min(), phi.max())
ax.set_ylim(k.min(), k.max())
ax.set_xticks(np.linspace(0.8, 1.0, 5))

fig.tight_layout()
# fig.savefig("porosity_permeability.png", dpi=300)
