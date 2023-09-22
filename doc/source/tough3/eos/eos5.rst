.. _eos5:

EOS5
====

The EOS5 fluid property module is developed to study the behavior of groundwater systems in which hydrogen releases take place.
For instance, in a number of waste disposal projects, corrosive metals are to be emplaced in geologic formations beneath the water table.
These will evolve a mixture of gases, with hydrogen being the chief constituent.
EOS5 is a close "cousin" of :ref:`eos3`, the main difference being that the air component is replaced by hydrogen, with considerably different thermophysical properties (see :numref:`tab:eos5.1` to :numref:`tab:eos5.3`).
The assignment and handling of primary thermodynamic variables in EOS5 is identical to :ref:`eos3` (see :numref:`tab:eos5.4`).
The main differences in the assignment of secondary parameters are as follows.
Density of gaseous hydrogen is computed from the ideal gas law.
Viscosity and water solubility of hydrogen are interpolated from the data given in Table 1.
For temperatures in excess of 25˚C, the solubility at 25˚C is used.

.. list-table:: Density of hydrogen at :math:`P` = 1 bar.
    :name: tab:eos5.1
    :header-rows: 1
    :align: center

    *   - Temperature
        - Experimental*
        - Ideal gas law†
    *   - 280 K
        - 0.086546 kg/m\ :sup:`3`
        - 0.08660 kg/m\ :sup:`3`
    *   - 300 K
        - 0.080776 kg/m\ :sup:`3`
        - 0.08082 kg/m\ :sup:`3`

.. list-table:: Viscosity* of hydrogen.
    :name: tab:eos5.2
    :header-rows: 1
    :align: center

    *   - Pressure
        - :math:`T` = 0˚C
        - :math:`T` = 100˚C
    *   - 1 bar
        - 8.40 x 10\ :sup:`-6` Pa·s
        - 10.33 x 10\ :sup:`-6` Pa·s
    *   - 100 bar
        - 8.57 x 10\ :sup:`-6` Pa·s
        - 10.44 x 10\ :sup:`-6` Pa·s

.. list-table:: Solubility in water at :math:`P` = 1 bar\ :sup:`§`.
    :name: tab:eos5.3
    :header-rows: 1
    :align: center

    *   - Temperature
        - Solubility
    *   - :math:`T` = 0˚C
        - 1.92 x 10\ :sup:`-6` g H\ :sub:`2`/g H\ :sub:`2`\O
    *   - :math:`T` = 25˚C
        - 1.54 x 10\ :sup:`-6` g H\ :sub:`2`/g H\ :sub:`2`\O

.. note::

    | \* from :cite:label:`vargaftik1975tables`, p. 39.
    | † universal gas constant :math:`R` = 8314.56 J/mol/˚C; molecular weight of hydrogen 2.0160 kg/mol.
    | \ :sup:`§` after :cite:label:`dean1999lange`; solubility at different pressures is computed from Henry's law.


Specifications
--------------

A summary of EOS5 specifications and parameters is given in Table :numref:`tab:eos5.4`.
The default parameter settings are (``NK``, ``NEQ``, ``NPH``, ``NB``) = (2, 3, 2, 6).
The option ``NEQ`` = 2 is available for constant temperature conditions.
The choice of primary thermodynamic variables is (:math:`P`, :math:`X`, :math:`T`) for single-phase, (:math:`P_g`, :math:`S_g` + 10, :math:`T`) for two-phase conditions.
As a convenience to users, we retain the capability to optionally initialize flow problems with TOUGH-style primary variables by setting ``MOP(19)`` = 1.
In TOUGH we have (:math:`P`, :math:`T`, :math:`X`) for single-phase conditions, (:math:`P_g`, :math:`S_g`, :math:`T`) for two-phase conditions.

.. list-table:: Summary of EOS5.
    :name: tab:eos5.4
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: hydrogen
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (2, 3, 2, 6) water and hydrogen, nonisothermal (default)
          | (2, 2, 2, 6) water and hydrogen, isothermal
          | Molecular diffusion can be modeled by setting ``NB`` = 8
    *   - Primary variables*
        - | Single-phase conditions:
          | (:math:`P`, :math:`X`, :math:`T`): (pressure, hydrogen mass fraction, temperature)
          | Two-phase conditions:
          | (:math:`P_g`, :math:`S_g` + 10, :math:`T`): (gas phase pressure, gas saturation plus 10, temperature)

.. note::

    \* By setting ``MOP(19)`` = 1, initialization can be made with TOUGH-style variables (:math:`P`, :math:`T`, :math:`X`) for single-phase, (:math:`P_g`, :math:`S_g`, :math:`T`) for two-phase.
