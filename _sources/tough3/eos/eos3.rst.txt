.. _eos3:

EOS3
====

This module is an adaptation of the EOS module of the TOUGH simulator, and implements the same thermophysical properties model (:cite:label:`pruess1987tough`).
All water properties are represented by the steam table equations as given by the :cite:label:`ifc1967formulation`.
Air is approximated as an ideal gas, and additivity is assumed for air and vapor partial pressures in the gas phase, :math:`P_g = P_a + P_v`.
The viscosity of air-vapor mixtures is computed from a formulation given by :cite:label:`hirschfelder1964molecular`.
The solubility of air in liquid water is represented by Henry's law, as follows.

.. math::
    :label: eq:eos3.1

    P_a = K_h x_{aq}^a

where :math:`K_h` is Henry's constant and :math:`x_{aq}^a` is air mole fraction in the aqueous phase.
Henry's constant for air dissolution in water is a slowly varying function of temperature, varying from 6.7 x 10:\ :sup:`9` Pa at 20˚C to 1.0 x 10\ :sup:`10` Pa at 60˚C and 1.1 x 10\ :sup:`10` Pa at 100˚C (:cite:label:`loomis1928solubilities`).
Because air solubility is small, this kind of variation is not expected to cause significant effects, and a constant :math:`P_a` = 10\ :sup:`10` Pa was adopted.


Specifications
--------------

A summary of EOS3 specifications and parameters is given in :numref:`tab:eos3`.
The default parameter settings are (``NK``, ``NEQ``, ``NPH``, ``NB``) = (2, 3, 2, 6).
The option ``NEQ`` = 2 is available for constant temperature conditions.
The choice of primary thermodynamic variables is (:math:`P`, :math:`X`, :math:`T`) for single-phase, (:math:`P_g`, :math:`S_g` + 10, :math:`T`) for two-phase conditions.
The rationale for the seemingly bizarre choice of :math:`S_g` + 10 as a primary variable is as follows.
As an option, we wish to be able to run isothermal two-phase flow problems with the specification ``NEQ`` = ``NK``, so that the then superfluous heat balance equation needs not be engaged.
This requires that temperature :math:`T` be the third primary variable.
The logical choice of primary variables would then appear to be (:math:`P`, :math:`X`, :math:`T`) for single-phase and (:math:`P_g`, :math:`S_g`, :math:`T`) for two-phase conditions. 
However, both :math:`X` and :math:`S_g` vary over the range (0, 1), so that this would not allow a distinction of single-phase from two-phase conditions solely from the numerical range of primary variables.
By taking the second primary variable for two-phase conditions to be :math:`X2` = 10 + :math:`S_g`, the range of that variable is shifted to the interval (10, 11), and a distinction between single and two-phase conditions can be easily made.
As a convenience to users, we retain the capability to optionally initialize flow problems with TOUGH-style primary variables by setting ``MOP(19)`` = 1.
In TOUGH we have (:math:`P`, :math:`T`, :math:`X`) for single-phase conditions, (:math:`P_g`, :math:`S_g`, :math:`T`) for two-phase conditions.

.. list-table:: Summary of EOS3.
    :name: tab:eos3
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: air
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (2, 3, 2, 6) water and air, nonisothermal (default)
          | (2, 2, 2, 6) water and air, isothermal
          | Molecular diffusion can be modeled by setting ``NB`` = 8
    *   - Primary variables*
        - | Single-phase conditions:
          | (:math:`P`, :math:`X`, :math:`T`): (pressure, air mass fraction, temperature)
          | Two-phase conditions:
          | (:math:`P_g`, :math:`S_g` + 10, :math:`T`): (gas phase pressure, gas saturation plus 10, temperature)

.. note::

    \* By setting ``MOP(19)`` = 1, initialization can be made with TOUGH-style variables (:math:`P`, :math:`T`, :math:`X`) for single-phase, (:math:`P_g`, :math:`S_g`, :math:`T`) for two-phase.
