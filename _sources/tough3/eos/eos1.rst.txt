.. _eos1:

EOS1
====

This is the most basic EOS module, providing a description of pure water in its liquid, vapor, and two-phase states.
All water properties (density, specific enthalpy, viscosity, saturated vapor pressure) are calculated from the steam table equations as given by the :cite:label:`ifc1967formulation`.
The formulation includes subregion 1 (subcooled water below T=350˚C), subregion 2 (superheated steam), and subregion 6 (saturation line up to T=350˚C). 
In these regions, density and internal energy are represented within experimental accuracy. 
Viscosity of liquid water and steam are represented to within 2.5% by correlations given in the same reference.
For details of the formulation, its accuracy and range of validity, refer to the original publication.
Vapor pressure lowering from capillary and adsorption effects is neglected; thus, in two-phase conditions vapor pressure is equal to saturated vapor pressure of bulk liquid.


Specifications
--------------

A summary of EOS1 specifications and parameters is given in :numref:`tab:eos1`.
The default parameter settings are (``NK``, ``NEQ``, ``NPH``, ``NB``) = (1, 2, 2, 6) for solving mass and energy balances for a single water component.
The option ``NEQ`` = 1 is available for running single-phase flow problems that involve only liquid water, or only superheated steam, under constant temperature conditions.
EOS1 also has a capability for representing two waters of identical physical properties, which contain different trace constituents.
This option can be invoked by specifying (``NK``, ``NEQ``, ``NPH``, ``NB``) = (2, 3, 2, 6) in data block **MULTI**.
With this option, two water mass balances will be set up, allowing separate tracking of the two components.
For example, one could specify the water initially present in the flow system as "water 1", while water being injected is specified as "water 2".
When the two waters option is chosen, molecular diffusion can also be modeled by setting parameter ``NB`` equal to 8.

The primary variables are (:math:`P`, :math:`T``) for single-phase points, (:math:`P_g`, :math:`S_g`) for two-phase points.
For the convenience of the user it is possible to initialize two-phase points as (:math:`T`, :math:`S_g`); when the numerical value of the first primary variable is less than 374.15, this will automatically be taken to indicate that this represents temperature rather than pressure, and will cause variables to be converted internally from (:math:`T`, :math:`S_g`) to (:math:`P_{sat}(T)`, :math:`S_g`) prior to execution.
When the two waters option is used, primary variables are (:math:`P`, :math:`T`, :math:`X`) for single-phase points, and (:math:`P_g`, :math:`S_g`, :math:`X`) for two-phase points, where :math:`X` is the mass fraction of "water 2" present.
All thermophysical properties (density, specific enthalpy, viscosity) are assumed independent of the component mixture; i.e., independent of mass fraction :math:`X`. This approximation is applicable for problems in which the identity of different waters is distinguished by the presence of different trace constituents, which occur in concentrations low enough to not appreciably affect the thermophysical properties.

.. list-table:: Summary of EOS1.
    :name: tab:eos1
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: "water 2" (optional)
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (1, 2, 2, 6) one water component, nonisothermal (default)
          | (1, 1, 2, 6) only liquid, or only vapor; isothermal
          | (2, 3, 2, 6) two-waters, nonisothermal*
          | Molecular diffusion can be modeled by setting ``NK`` = 2, ``NB`` = 8
    *   - Primary variables
        - | Single-phase conditions:
          | (:math:`P`, :math:`T`, :math:`[X]`): (pressure, temperature, [mass fraction of water 2]†)
          | Two-phase conditions:
          | (:math:`P_g`, :math:`S_g`, :math:`[X]`): (gas phase pressure, gas saturation, [mass fraction of water 2]†)


.. note::

    | \* two waters cannot be run in isothermal mode, because in this case temperature is not the last primary variable.
    | † optional, for ``NK`` = 2 only.

The phase diagnostic procedures are as follows.
When initializing a problem, each grid block has two primary variables (:math:`X1`, :math:`X2`).
The meaning of :math:`X2` depends on its numerical value: for :math:`X2` > 1.5, :math:`X2` is taken to be temperature in ˚C, otherwise it is gas saturation.
Although physically saturation is restricted to the range :math:`0 \le S \le 1`, it is necessary to allow saturations to exceed 1 during the Newton-Raphson iteration.
If :math:`X2` is temperature, this indicates that single-phase conditions are present; specifically, for :math:`P` (= :math:`X1`) :math:`\gt P_{sat}(T)` we have single-phase liquid, otherwise we have single-phase steam.
Subsequent to initialization, the phase condition is identified simply based on the value of :math:`S_g` as stored in the *PAR* array:

- 0: single-phase liquid
- 1: single-phase vapor
- :math:`0 \lt S_g \lt 1`: two-phase


Phase change is recognized as follows.
For single-phase points the temperature (second primary variable) is monitored, and the corresponding saturation pressure is compared with actual fluid pressure :math:`P`.
For a vapor (liquid) point to remain vapor (liquid), we require that :math:`P \lt P_{sat}` (:math:`P \gt P_{sat}`); if this requirement is violated, a transition to two-phase conditions takes place.
The primary variables are then switched to (:math:`P_g`, :math:`S_g`), and these are initialized as :math:`P_g = P_{sat}(T)`, :math:`S_g` = 0.999999 if the point was in the vapor region, and :math:`S_g` = 10\ :sup:`-6` if it was in the liquid region.
For two-phase points :math:`S_g` is monitored; we require that :math:`0 \lt S_g \lt 1` for a point to remain two-phase.
If :math:`S_g \lt 0` this indicates disappearance of the gas phase; the primary variables are then switched to (:math:`P`, :math:`T`), and the point is initialized as single-phase liquid, with :math:`T` taken from the last Newton-Raphson iteration, and :math:`P` = 1.000001 × :math:`P_{sat}(T)`.
For :math:`S_g \gt 1` the liquid phase disappears; again the primary variables are switched to (:math:`P`, :math:`T`), and the point is initialized as single-phase vapor, with :math:`T` taken from the last Newton-Raphson iteration, and :math:`P` = 0.999999 × :math:`P_{sat}(T)`.
Note that in these phase transitions we preserve temperature rather than pressure from the last iteration.
This is preferable because in most flow problems temperature tends to be more slowly varying than pressure.
