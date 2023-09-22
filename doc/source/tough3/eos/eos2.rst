.. _eos2:

EOS2
====

This is an updated version of the fluid property module originally developed by :cite:label:`o1985fluid` for describing fluids in gas-rich geothermal reservoirs, which may contain CO\ :sub:`2` mass fractions ranging from a few percent to occasionally 80% or more (:cite:label:`atkinson1980behavior`).
EOS2 accounts for non-ideal behavior of gaseous CO\ :sub:`2`, and dissolution of CO\ :sub:`2` in the aqueous phase with heat of solution effects.
According to Henry's law, the partial pressure of a non-condensible gas (NCG) in the gas phase is proportional to the mole fraction of dissolved NCG in the aqueous phase

.. math::
    :label: eq:eos2.1

    P_{NCG} = K_h x_{aq}^{NCG}

The Henry's law coefficient :math:`K_h` for dissolution of CO\ :sub:`2` in water is strongly dependent on temperature.
The correlation used in the previous release of EOS2 had been developed by :cite:label:`o1985fluid` for the elevated temperature conditions encountered in geothermal reservoirs.
It is accurate to within a few percent of experimental data in the temperature range of 40˚C ≤ :math:`T` ≤ 330˚C, but becomes rather inaccurate at lower temperatures and even goes to negative values for :math:`T` < 30˚C (see :numref:`fig:eos2.1`).
Subroutine *HENRY* in EOS2 was replaced with a new routine that uses the correlation developed by :cite:label:`battistelli1997simulator`, which is accurate for 0˚C ≤ :math:`T` ≤ 350˚C.
The Battistelli et al. formulation agrees well with another correlation that was developed by S. White (1996, private communication).

.. figure:: ../figures/figure_eos2_1.png
    :name: fig:eos2.1

    Henry's law coefficients for dissolution of CO\ :sub:`2` in water.

The viscosity of vapor - CO\ :sub:`2` mixtures is described with a formulation due to :cite:label:`pritchett1981baca`; other thermophysical property correlations are based on the model of :cite:label:`sutton1977boiling`.


Specifications
--------------

A summary of EOS2 specifications and parameters is given in :numref:`tab:eos2`.
A more detailed description and application to geothermal reservoir problems are given in the paper by :cite:label:`o1985fluid`.
EOS2 has the parameter settings of (``NK``, ``NEQ``, ``NPH``, ``NB``) = (2, 3, 2, 6) for solving mass and energy balances for water and CO\ :sub:`2`.
Molecular diffusion can also be modeled by setting parameter ``NB`` equal to 8.

.. list-table:: Summary of EOS2.
    :name: tab:eos2
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: CO\ :sub:`2`
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (2, 3, 2, 6)
          | Molecular diffusion can be modeled by setting ``NB`` = 8
    *   - Primary variables
        - | Single-phase conditions:
          | (:math:`P`, :math:`T`, :math:`P_{CO_2}`): (pressure, temperature, CO\ :sub:`2` partial pressure)
          | Two-phase conditions:
          | (:math:`P_g`, :math:`S_g`, :math:`P_{CO_2}`): (gas phase pressure, gas saturation, CO\ :sub:`2` partial pressure)
