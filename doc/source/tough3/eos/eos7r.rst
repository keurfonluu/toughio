.. _eos7r:

EOS7R
=====

This is an enhanced version of the :ref:`eos7` module in which two additional mass components have been added, providing radionuclide transport capability for TOUGH3.
These components can undergo decay with user-specified half-life, with radionuclide 1 (Rn1 for short) being the "parent" and Rn2 the "daughter".
The radionuclides are considered water-soluble as well as volatile, but are not allowed to form a separate non-aqueous fluid phase.
Sorption onto the solid grains is also included.
The decaying components are normally referred to as radionuclides, but they may in fact be any trace components that decay, adsorb, and volatilize.
The decay process need not to be radioactive decay, but could be any process that follows a first-order decay law, such as biodegradation.
Stable trace components, such as volatile and water soluble organic chemicals (VOCs), can be modeled simply by setting half-life to very large values.
A detailed description of the mathematical model and numerical implementation used in EOS7R is available in a laboratory report, which also presents a number of illustrative problems, including verification against analytical solutions (:cite:label:`oldenburg1995eos7r`).
Here we highlight the main aspects of the thermophysical properties model.
Note that the current TOUGH3 does not include the dispersion module T2DM, therefore cannot simulate Fickian hydrodynamic dispersion.

Radionuclide decay is described by

.. math::
    :label: eq:eos7r.1

    \frac{dM^{\kappa}}{dt} = -\lambda_{\kappa} M^{\kappa}

where :math:`M^{\kappa}` is the mass of radionuclide :math:`\kappa` (= Rn1, Rn2) per unit volume, and the decay constant :math:`\lambda_{\kappa}` is related to the half-life by

.. math::
    :label: eq:eos7r.2

    T_{1/2} = \frac{\log(2)}{\lambda_{\kappa}}

Adsorption of radionuclides on the solid grains is modeled as reversible instantaneous linear sorption, so that mass of radionuclide component :math:`\kappa` per unit reservoir volume is given by

.. math::
    :label: eq:eos7r.3

    M^{\kappa} = \phi \sum_{\beta} S_{\beta} \rho_{\beta} X_{\beta}^{\kappa} + \left( 1 - \phi \right) \rho_R \rho_{aq} X_{aq}^{\kappa} K_d

where :math:`K_d` is the aqueous phase distribution coefficient (:cite:label:`de1986quantitative`, p. 256).

In addition to adsorbing onto solid matrix grains, the radionuclide components may volatilize into the gas phase, if present.
Radionuclides partition between aqueous and gaseous phases according to Henry's law:

.. math::
    :label: eq:eos7r.4

    P_a^{\kappa} = K_h^{\kappa} x_{aq}^{\kappa}

where :math:`P_a^{\kappa}` is the partial pressure in the gas phase of radionuclide :math:`\kappa`, :math:`K_h^{\kappa}` is Henry's constant and :math:`x_{aq}^{\kappa}` is the mole fraction of radionuclide :math:`\kappa` in the aqueous phase.
In EOS7R as in :ref:`eos7`, no solubility constraints are enforced for the brine.
Users need to be aware that there are inherent limitations in the ability of a water-brine mixture model to describe processes that involve significant vaporization.
Unphysical results may be obtained in thermal problems with strong vaporization effects.

For the gas phase we assume ideal gas law for air and the radionuclides, and additivity of partial pressures.

.. math::
    :label: eq:eos7r.5

    P_{gas} = P_{air} + P_{vapor} + P_{Rn1} + P_{Rn2}

Gas phase density is calculated as the sum of the partial densities of gaseous components, while gas phase viscosity and enthalpy are calculated from the same air-vapor mixing models used in :ref:`eos3`.
Apart from these approximations for gas phase viscosity and enthalpy, there is no restriction to "small" radionuclide concentrations in the gas phase, fully allowing gas phase radionuclide partial pressures.

The thermophysical properties of the aqueous phase are assumed independent of radionuclide concentrations.
Implicit in this approximation is the assumption that aqueous radionuclide concentrations are small.
Users need to keep this limitation in mind, because EOS7R does not provide any intrinsic constraints on radionuclide concentrations.


Specifications
--------------

A summary of EOS7R specifications and parameters are given in :numref:`tab:eos7r`.
The default parameter settings are (``NK``, ``NEQ``, ``NPH``, ``NB``) = (5, 5, 2, 8).
The ``NK`` = 4 (no air) option may only be used for problems with single-phase liquid conditions throughout.
The primary variables are (:math:`P`, :math:`X_b`, :math:`X_{Rn1}`, :math:`X_{Rn2}`, :math:`X_{air}`, :math:`T`) for single-phase conditions and (:math:`P`, :math:`X_b`, :math:`X_{Rn1}`, :math:`X_{Rn2}`, :math:`S` + 10, :math:`T`) for two-phase conditions.

.. list-table:: Summary of EOS7R.
    :name: tab:eos7r
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: brine
          | #3: Rn1 (radionuclide 1; "parent")
          | #4: Rn2 (radionuclide 2; "daughter")
          | #5: air (optional)†
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``)\ :sup:`§` =
          | (5, 5, 2, 8) water, brine, Rn1, Rn2, air, isothermal (default)
          | (5, 6, 2, 8) water, brine, Rn1, Rn2, air, nonisothermal
          | (4, 4, 2, 8) water, brine, Rn1, Rn2, no air, isothermal
          | (4, 5, 2, 8) water, brine, Rn1, Rn2, no air, nonisothermal
          | Molecular diffusion can be suppressed by setting ``NB`` = 6
    *   - Primary variables\ :sup:`§`
        - | Single-phase conditions:
          | (:math:`P`, :math:`X_b`, :math:`X_{Rn1}`, :math:`X_{Rn2}`, :math:`X_{air}`, :math:`T`): (pressure, brine mass fraction, mass fraction of Rn1, mass fraction of Rn2, temperature)
          | Two-phase conditions:
          | (:math:`P`, :math:`X_b`, :math:`X_{Rn1}`, :math:`X_{Rn2}`, :math:`S` + 10, :math:`T`): (gas phase pressure, brine mass fraction, mass fraction of Rn1, mass fraction of Rn2, gas saturation plus ten, temperature)*

.. note::

    | † the no air option (``NK`` = 4) may only be used for problems with single-phase liquid conditions throughout.
    | \ :sup:`§` parameter NKIN following NB may optionally be set to ``NKIN`` = ``NK`` - 2, in which caseradionuclide mass fractions will be omitted, and initialization will be made from only four :ref:`eos7`-style variables; radionuclide mass fractions will be initialized as zero.
    | \* in two-phase conditions, :math:`X_{Rn1}` and :math:`X_{Rn2}` are mass fractions in the aqueous phase.

The phase change diagnostics are as follows.
For single-phase liquid conditions, Henry's law is used to calculate the partial pressures that the non-condensible gases would have if a gas phase were present.
The total pressure that a gas phase would have if present is then calculated from Eq. :math:numref:`eq:eos7r.5`, using saturated vapor pressure at prevailing temperature.
This is compared with the aqueous phase pressure, and a transition to two-phase conditions is made when :math:`P_{gas}` :math:`P_{gas}` > :math:`P_{aq}`.
In two-phase conditions, the saturation variable is monitored.
A phase transition to single-phase liquid occurs when :math:`S_g` < 0, while for :math:`S_g` > 1 a transition to single-phase gas conditions is made.
For transitions from two-phase to single-phase liquid conditions, liquid pressure is initialized as :math:`P_{aq}` = (1 + 10\ :sup:`-6`) × :math:`P_{gas}`, with :math:`P_{gas}` given by Eq. :math:numref:`eq:eos7r.5`, while for transitions to single-phase gas conditions, pressure is initialized as (1 - 10\ :sup:`-6`) × :math:`P_{gas}`.
For single-phase gas conditions we monitor vapor pressure :math:`P_{vap} = P_{gas} - P_{air} - P_{Rn1} - P_{Rn2}`; a transition to two-phase conditions occurs when :math:`P_{vap}` > :math:`P_{gas}`.


Selections
----------

Brine and radionuclide properties are specified in the TOUGH3 input file by means of a data block **SELEC**, as follows.
Note that the current version of TOUGH3 does not include the dispersion module T2DM.

.. list-table:: Record **SELEC.1**.
    :name: tab:eos7r.selec.1
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``IE(1)``
        - I5
        - set equal to 6 to read six additional records with data for brine and radionuclides, and for hydrodynamic dispersion. The 7 input variables following ``IE(1)`` are for the dispersion module T2DM only and can be left blank if T2DM is not used.
    *   - ``NGBINP(1)``
        - I5
        - number of grid blocks in X (must always be equal to 1).
    *   - ``NGBINP(2)``
        - I5
        - number of grid blocks in Y.
    *   - ``NGBINP(3)``
        - I5
        - number of grid blocks in Z.
    *   - ``NFBL``
        - I5
        - number of the first ("left") column of grid blocks within the flow domain (defaults to 1 if zero or blank).
    *   - ``NFBR``
        - I5
        - number of the last ("right") column of grid blocks within the flow domain (defaults to ``NGBINP(2)`` if zero or blank).
    *   - ``NFBT``
        - I5
        - number of the first ("top") row of grid blocks within the flow domain (defaults to 1 if zero or blank).
    *   - ``NFBB``
        - I5
        - number of the last ("bottom") row of grid blocks within the flow domain (defaults to ``NGBINP(3)`` if zero or blank).

.. list-table:: Record **SELEC.2**.
    :name: tab:eos7r.selec.2
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
    :name: tab:eos7r.selec.3
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - :math:`\nu_1`, :math:`\nu_2`, :math:`\nu_3`
        - 3E10.4
        - coefficients for salinity correction of aqueous phase viscosity, following :cite:label:`herbert1988coupled`.

          .. math::
              :label: eq:eos7r.6

              f(X_b) = 1 + \nu_1 X_b + \nu_2 X_b^2 + \nu_3 X_b^3

          with default values of :math:`\nu_1` = 0.4819, :math:`\nu_2` = -0.2774, and :math:`\nu_3` = 0.7814.
          Different values for the coefficients may be specified by the user.

.. list-table:: Record **SELEC.4**.
    :name: tab:eos7r.selec.4
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``ALPHAT``
        - E10.4
        - transverse dispersivity (m).
    *   - ``ALPHAL``
        - E10.4
        - longitudinal dispersivity (m).

.. list-table:: Record **SELEC.5**.
    :name: tab:eos7r.selec.5
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``FDDIAG(NP,NK)``
        - E10.4
        - ``NP`` = 1, 2; ``NK`` = 1, 2, 5 molecular diffusivities in units of m\ :sup:`2`/s; first the three gas phase diffusivities for water, brine, and air; then the three aqueous phase diffusivities for water, brine, and air. If a data block **DIFFU** is present, it will override the diffusivity specifications made in **SELEC**.

.. list-table:: Record **SELEC.6**.
    :name: tab:eos7r.selec.6
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``XHALF(3)``
        - E10.4
        - half-life of parent radionuclide (Rn1, component 3) (seconds).
    *   - ``XMW(3)``
        - E10.4
        - molecular weight of Rn1 (g/mol).
    *   - ``FDDIAG(NP,3)``
        - E10.4
        - molecular diffusivity of Rn1 in the gas phase in m\ :sup:`2`/s; followed by molecular diffusivity of Rn1 in the aqueous phase. If a data block **DIFFU** is present, it will override the diffusivity specifications made in **SELEC**.
    *   - 
        - 20X
        - (void)
    *   - ``HCRN(1)``
        - E10.4
        - inverse Henry's constant :math:`K_h^{-1}` (see Eq. :math:numref:`eq:eos7r.4`) for parent radionuclide Rn1 (Pa\ :sup:`-1`). (The inverse Henry's constant can be thought of as an aqueous phase solubility).

.. list-table:: Record **SELEC.7**.
    :name: tab:eos7r.selec.7
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``XHALF(4)``
        - E10.4
        - half-life of parent radionuclide (Rn2, component 4) (seconds).
    *   - ``XMW(4)``
        - E10.4
        - molecular weight of Rn2 (g/mol).
    *   - ``FDDIAG(NP,4)``
        - E10.4
        - molecular diffusivity of Rn2 in the gas phase in m\ :sup:`2`/s; followed by molecular diffusivity of Rn2 in the aqueous phase. If a data block **DIFFU** is present, it will override the diffusivity specifications made in **SELEC**.
    *   - 
        - 20X
        - (void)
    *   - ``HCRN(1)``
        - E10.4
        - inverse Henry's constant :math:`K_h^{-1}` (see Eq. :math:numref:`eq:eos7r.4`) for daughter radionuclide Rn2 (Pa\ :sup:`-1`). (The inverse Henry's constant can be thought of as an aqueous phase solubility).
