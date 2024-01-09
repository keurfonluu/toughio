.. _eos8:

EOS8
====

EOS8 is an enhanced version of :ref:`eos3`, and is developed from :ref:`eos3` by adding a third non-volatile, insoluble component, called "oil", which can only exist in a separate, immiscible phase.
This module provides a very basic and simple capability for modeling three fluid phases, including gaseous, aqueous, and oleic phases.
EOS8 can represent what in petroleum engineering is often referred to as a "dead oil", meaning a non-aqueous phase liquid that has no volatile or soluble components, so that it is present only in the non-aqueous phase.
The thermophysical property description related to the third (oil) phase is intentionally kept very simple and, although EOS8 may be applicable to some flow problems of practical interest as is, it should be considered a development platform rather than a realistic description of three-phase fluid systems.

The relative permeabilities of the gas and aqueous phases are considered functions of their respective phase saturations only, :math:`k_{rg} = k_{rg}(Sg)`, :math:`k_{rl} = k_{rl}(S_{aq})`, and are specified through input data in the usual manner.
The oil phase is considered of intermediate wettability, and its relative permeability is described in a schematic fashion that is intended to serve as a template for users.

.. math::
    :label: eq:eos8.1

    k_{ro} = \frac{S_o - S_{or}}{1 - S_{or}}

Here, :math:`S_{or}` is the residual oil saturation.
Oil phase capillary pressure is neglected.
Viscosity, density, and specific enthalpy of the oil phase are described as functions of pressure and temperature through low-order polynomials, with user-specified parameters entered through data block **SELEC**.
More specifically, viscosity is written as

.. math::
    :label: eq:eos8.2

    \mu_{oil} = a + b \left( P - P_1 \right) + c \left( P - P_2 \right)^2 + d \left( T - T_1 \right) + e \left( T - T_2 \right)^2

Oil density is

.. math::
    :label: eq:eos8.3

    \rho_{oil} = \rho_0 + C \left( P - P_0 \right) - E \left( T - T_0 \right)

where :math:`\rho_0` is oil density at reference pressure and temperature conditions of (:math:`P_0`, :math:`T_0`).
Specific enthalpy of oil is assumed proportional to temperature (normalized to :math:`h_{oil}` = 0 at :math:`T` = 0˚C).

.. math::
    :label: eq:eos8.4

    h_{oil} = \zeta T

All parameters appearing in the oil phase property description in Eqs. :math:numref:`eq:eos8.2`, :math:numref:`eq:eos8.3`, and :math:numref:`eq:eos8.4` are to be provided by the user through data block **SELEC**.
The property correlations are implemented through arithmetic statement functions at the top of EOS8 in a manner that should be transparent to users.
Users may also refer detailed comment statements in the EOS8 source code for instructions of preparing EOS8 input data.


Specifications
--------------

A summary of EOS8 specifications and parameters is given in :numref:`tab:eos8`.
The default parameter settings are (``NK``, ``NEQ``, ``NPH``, ``NB``) = (3, 3, 3, 6).
The choice of primary thermodynamic variables is (:math:`P`, :math:`X`, :math:`S_o`, :math:`T`) for single-phase, (:math:`P_g`, :math:`S_g` + 10, :math:`S_o`, :math:`T`) for two-phase conditions.
With EOS8 the user can optionally run just two phases (aqueous-gas, without the oil phase), in which case the aqueous-gas process descriptions reduce to those of :ref:`eos3`.

.. list-table:: Summary of EOS8.
    :name: tab:eos8
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: brine
          | #3: oil
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (3, 3, 3, 6) water, air, oil, isothermal (default)
          | (3, 4, 3, 6) water, air, oil, nonisothermal
          | (2, 2, 2, 6) water, air, no oil, isothermal
          | (2, 3, 2, 6) water, air, no oil, nonisothermal
    *   - Primary variables
        - | Single-phase conditions:
          | (:math:`P`, :math:`X`, :math:`S_o`, :math:`T`): (pressure, air mass fraction, oil phase saturation, temperature)
          | Two-phase conditions:
          | (:math:`P_g`, :math:`S_g` + 10, :math:`S_o`, :math:`T`): (gas phase pressure, gas saturation plus ten, oil phase saturation, temperature)


Selections
----------

The parameters used in the oil phase property description are specified in the TOUGH3 input file by means of a data block **SELEC**, as follows

.. list-table:: Record **SELEC.1**.
    :name: tab:eos8.selec.1
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``IE(1)``
        - I5
        - set equal to 6 to read six additional records with data for brine and radionuclides, and for hydrodynamic dispersion.

.. list-table:: Record **SELEC.2**.
    :name: tab:eos8.selec.2
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - 
        - X
        - (void)

.. list-table:: Record **SELEC.3**.
    :name: tab:eos8.selec.3
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - 
        - X
        - (void)

.. list-table:: Record **SELEC.4**.
    :name: tab:eos8.selec.4
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - :math:`S_{or}`
        - E10.4
        - irreducible saturation of oil phase.
    *   - :math:`a`
        - E10.4
        - constant portion in Eq. :math:numref:`eq:eos8.2` for oil phase viscosity.

.. list-table:: Record **SELEC.5**.
    :name: tab:eos8.selec.5
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - :math:`a`, :math:`P_1`, :math:`c`, :math:`P_2`, :math:`d`, :math:`T_1`, :math:`e`, :math:`T_2`
        - 8E10.4
        - coefficients for oil phase viscosity in Eq. :math:numref:`eq:eos8.2`.

.. list-table:: Record **SELEC.6**.
    :name: tab:eos8.selec.6
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - :math:`\rho_0`, :math:`C`, :math:`P_0`, :math:`E`, :math:`T_0`
        - 5E10.4
        - coefficients for oil density in Eq. :math:numref:`eq:eos8.3`.

.. list-table:: Record **SELEC.7**.
    :name: tab:eos8.selec.7
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - :math:`\zeta`
        - 10.4
        - coefficients for oil specific enthalpy in Eq. :math:numref:`eq:eos8.4`.
