.. _eos7:

EOS7
====

An extension of the :ref:`eos3` module for water/air mixtures, EOS7 represents the aqueous phase as a mixture of (pure) water and brine.
This approach is very useful for flow problems in which salinity does not reach saturated levels (:cite:label:`reeves1986theory, herbert1988coupled`).
The salinity of the aqueous phase is described by means of the brine mass fraction, Xb, and density and viscosity are interpolated from the values for the water and brine endmembers.
Salinity-dependent air solubility is also taken into account, but no allowance is made for reduction of vapor pressure with salinity.
The brine is modeled as NaCl solution, while the non-condensible gas is air, although the treatment could be adapted, with minor modifications, to other brines and gases.
The representation of the temperature and pressure dependence of thermophysical properties is somewhat more general than that of :cite:label:`reeves1986theory`, retaining the flexibility of the TOUGH3 formulation for nonisothermal processes.

EOS7 can describe phase conditions ranging from single-phase liquid to two-phase to single-phase gas.
However, the approach of describing variably saline fluids not as mixtures of water and salt but as mixtures of water and brine has specific limitations which need to be considered in applications.
For example, in problems with significant boiling it would be possible for salinity to reach saturated levels, corresponding to brine mass fraction :math:`X_b` = 1 (supposing that the brine component was chosen as fully saturated salt solution).
Upon further boiling solid salt would precipitate, but solubility limits and solids precipitation are not taken into account in the approach used in EOS7 (these can be modeled with the EWASG module, see the addendum for EWASG).
As evaporation continues from a saline aqueous phase, eventually brine mass fraction would increase beyond :math:`X_b` = 1, in which case other mass fractions would become negative, and non-physical results would be obtained.
From a physical viewpoint brine mass fraction in the gas phase should always be equal to zero, but the only way the brine mass balance can be maintained during phase transitions from two-phase to single-phase vapor conditions is by allowing :math:`X_b`, gas to vary freely.
Users need to carefully examine problem setups and results to guard against unphysical results in applications that involve boiling.

We now briefly summarize the treatment of thermophysical properties in EOS7.
The density of the aqueous phase is calculated from the assumption, shown to be very accurate by :cite:label:`herbert1988coupled`, that fluid volume is conserved when water and brine are mixed.
Mixture density :math:`\rho_m` can then be expressed in terms of water and brine densities as follows

.. math::
    :label: eq:eos7.1
    
    \frac{1}{\rho_m} = \frac{1 - X_b}{\rho_w} + \frac{X_b}{\rho_b}

where :math:`\rho_w` and :math:`\rho_b` are water and brine density, respectively.
Eq. :math:numref:`eq:eos7.1` applies to densities at fixed pressure and temperature conditions.
In order to achieve a simple approximation for fluid density at variable temperatures and pressures, EOS7 takes compressibility and expansivity of brine to be equal to those of water.
This will provide a reasonable approximation at least for a limited range of temperatures and pressures around the reference conditions (:math:`P_0`, :math:`T_0`).
The default reference brine has a density of 1185.1 kg/m\ :sup:`3` at reference conditions of :math:`P_0` = 1 bar, :math:`T_0` = 25˚C, corresponding to an NaCl solution of 24.98 wt-%, or 5.06 molar (:cite:label:`potter1977volumetric`; cited after :cite:label:`finley1982swift`).
The user may specify different reference conditions and brine densities.
Effects of salinity on the enthalpy of the aqueous phase are ignored.

Following :cite:label:`herbert1988coupled`, salinity effects on aqueous phase viscosity are modeled with a polynomial correction to the viscosity of pure water.
Mixture viscosity :math:`\mu_m` is represented as follows

.. math::
    :label: eq:eos7.2

    \mu_m (P, T, X_b) = \mu_w (P, T) f(X_b)

where

.. math::
    :label: eq:eos7.3

    f(X_b) = 1 + \nu_1 X_b + \nu_2 X_b^2 + \nu_3 X_b^3

with default values of :math:`\nu_1` = 0.4819, :math:`\nu_2` = -0.2774, and :math:`\nu_3` = 0.7814.
Different values for the coefficients may be specified by the user.

Gas (air) dissolution in the aqueous phase is modeled by Henry's law, as follows

.. math::
    :label: eq:eos7.4

    P_a = K_h x_{aq}^a

where :math:`K_h` is Henry's constant and :math:`x_{aq}^a` is air mole fraction in the aqueous phase.
In saline solutions, gases are generally less soluble than in water ("salting out" effect).
For a 5 :math:`N` (molar) NaCl solution, nitrogen solubility is virtually independent of temperature in the range 0˚C ≤ :math:`T` ≤ 100˚C, and corresponds to a Henry's constant of :math:`K_h` = 4.0 x 10\ :sup:`10` Pa (:cite:label:`cygan1991solubility`).

We retain the value of :math:`K_h` = 10\ :sup:`10` Pa for pure water, and represent air solubility (inverse of Henry's constant) as a linear function of mixture molarity :math:`N_m`, as follows

.. math::
    :label: eq:eos7.5

    \frac{1}{K_h} = 1.0 \times 10^{-10} + \frac{N_m}{5} \left( \frac{1}{4.0 \times 10^{10}} - 10^{-10} \right)


Specifications
--------------

A summary of EOS7 specifications and parameters appears in :numref:`tab:eos7`.
The default parameter settings are (``NK``, ``NEQ``, ``NPH``, ``NB``) = (3, 3, 2, 6).
The ``NK`` = 2 (no air) option may only be used for problems with single-phase liquid conditions throughout.
The primary variables are (:math:`P`, :math:`X_b`, :math:`X`, :math:`T`) for single-phase conditions and (:math:`P`, :math:`X_b`, :math:`S` + 10, :math:`T`) for two-phase conditions, where :math:`X` is air mass fraction.

.. list-table:: Summary of EOS7.
    :name: tab:eos7
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: brine
          | #3: air (optional)*
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (3, 3, 2, 6) water, brine, air, isothermal (default)
          | (3, 4, 2, 6) water, brine, air, nonisothermal
          | (2, 2, 2, 6) water, brine, isothermal*
          | (2, 3, 2, 6) water, brine, nonisothermal*
          | Molecular diffusion can be modeled by setting ``NB`` = 8
    *   - Primary variables
        - | Single-phase conditions:
          | (:math:`P`, :math:`X_b`, :math:`X`, :math:`T`): (pressure, brine mass fraction, air mass fraction, temperature)
          | Two-phase conditions:
          | (:math:`P`, :math:`X_b`, :math:`S` + 10, :math:`T`): (gas phase pressure, brine mass fraction, gas saturation plus ten, temperature)

.. note::

    \* The ``NK`` = 2 (no air) option may only be used for problems with single-phase liquid conditions throughout.


Selections
----------

Users may specify parameters for reference brine in the TOUGH3 input file by means of an optional data block **SELEC**, as follows

.. list-table:: Record **SELEC.1**.
    :name: tab:eos7.selec.1
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``IE(1)``
        - I5
        - set equal to 2, to read two additional data records (a larger value with more additional data records is acceptable, but only the first two will be used by EOS7).

.. list-table:: Record **SELEC.2**.
    :name: tab:eos7.selec.2
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - :math:`P_0`\*
        - E10.4
        - reference pressure (Pa).
    *   - :math:`T_0`\*
        - E10.4
        - reference temperature (˚C).
    *   - :math:`\rho_b`\*
        - E10.4
        - brine density at (:math:`P_0`, :math:`T_0`) (kg/m\ :sup:`3`).

.. note::

    \* If any of these parameters is entered as zero, default values of :math:`P_0` = 1 bar, :math:`T_0` = 25˚C, :math:`\rho_b` = 1185.1 kg/m\ :sup:`3` will be used.
    For :math:`P_0` < 0, brine properties will be assumed identical to water.

.. list-table:: Record **SELEC.3**.
    :name: tab:eos7.selec.3
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - :math:`\nu_1`, :math:`\nu_2`, :math:`\nu_3`
        - 3E10.4
        - coefficients for salinity correction of aqueous phase viscosity, see Eq. :math:numref:`eq:eos7.3`.
