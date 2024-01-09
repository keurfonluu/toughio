.. _eos9:

EOS9
====

This module considers variably saturated flow of a single aqueous phase, which consists entirely of a single water component, and neglects phase change effects.
The gas phase is treated as a passive bystander at constant pressure, and conditions are assumed to be isothermal.
Thus, no mass balance equation for gas and no heat balance is needed, and only a single water mass balance equation is solved for each grid block.
This is very efficient numerically, making EOS9 the module of choice for problems for which the underlying approximations are applicable.

Liquid flow in EOS9 is described as follows:

.. math::
    :label: eq:eos9.1

    \frac{\partial}{\partial t} \phi \S_l \rho_l = \nabla \cdot \left( k \frac{k_{rl}}{\mu_l} \rho_l \nabla \left( P_l + \rho_l g z \right) \right)

where :math:`\phi` is porosity, :math:`S_l` is water saturation, :math:`\rho_l` is water density, :math:`k` is absolute permeability, :math:`k_{rl}` is relative permeability to the aqueous phase, :math:`\mu_l` is water viscosity, :math:`P_l` is water pressure, :math:`g` is acceleration of gravity, and :math:`z` is defined positive upward.
Neglecting variations in liquid phase density and viscosity, as is appropriate for (nearly) isothermal conditions, Eq. :math:numref:`eq:eos9.1` simplifies to Richards' equation (:cite:label:`richards1931capillary`).

.. math::
    :label: eq:eos9.2

    \frac{\partial \theta}{\partial t} = \nabla \cdot \left( K \nabla h \right)

where :math:`\theta = \phi S_l` is specific volumetric moisture content, :math:`K = k k_{rl} \frac{\rho_l g}{\mu_l}` is hydraulic conductivity, and :math:`h = z + \frac{P_l}{\rho_l g}` is the hydraulic head.
EOS9 can describe flow under partially saturated (0 < :math:numref:`S_l` < 1) as well as fully saturated conditions, and phase changes between the two.


Specifications
--------------

With only a single mass balance equation per grid block, there is only a single primary thermodynamic variable.
This is taken to be pressure for single-phase (saturated) conditions, and is water saturation for unsaturated conditions.
A distinction between the two is made simply on the basis of the numerical value of the first (and only) primary variable, :math:`X1`.
If :math:`X1` < 1, this indicates that If :math:`X1` represents water saturation and conditions are unsaturated; if If :math:`X1` is larger than a user-specified gas phase reference pressure (default :math:`P_{gas}` = 1.013 x 10\ :sup:`5` Pa), it is taken to be water pressure, and saturated conditions prevail.
When phase changes between saturated and unsaturated conditions occur, the primary variable is switched, as follows.
The numerical value of :math:`X1` and its change during the Newton-Raphson iteration process is monitored.
If :math:`X1` changes from being smaller than 1 to larger than 1, this indicates attainment of fully saturated conditions.
In that case :math:`X1` is switched to pressure, and is initialized at a pressure slightly in excess of gas phase reference pressure as :math:`X1 = P_{gas}(1 + \varepsilon)`, with :math:`\varepsilon` = 10\ :sup:`-6`.
If :math:`X1` changes from being larger than :math:`P_{gas}` to smaller than :math:`P_{gas}`, this indicates a transition from fully to partially saturated conditions.
:math:`X1` is then switched to saturation, and is initialized as :math:`X1 = 1 - \varepsilon`.
Actually, a transition from fully to partially saturated conditions is made only when :math:`X1` drops below :math:`P_{gas}(1 - \varepsilon)`; test calculations have shown that such a (small) finite-size window for phase change improves numerical stability and efficiency.

In EOS9, the thermophysical properties of water are taken at default reference conditions of :math:`P` = 1.013 x 10\ :sup:`5` Pa, :math:`T` = 15˚C.
These defaults can be overwritten in a flexible manner by specifying appropriate data in a fictitious **ROCKS** domain "``REFCO``", as follows

.. list-table:: Domain "``REFCO``".
    :name: tab:eos9.1
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``DROK``
        - E10.4
        - reference pressure
    *   - ``POR``
        - E10.4
        - reference temperature
    *   - ``PER(1)``
        - E10.4
        - liquid density
    *   - ``PER(2)``
        - E10.4
        - liquid viscosity
    *   - ``PER(3)``
        - E10.4
        - liquid compressibility

Note that assignment of thermophysical data through a specially-named domain was set up just as a convenient way of providing floating-point parameters to the code.
No volume elements (grid blocks) should be attached to domain "``REFCO``", as the data in general will not correspond to reasonable hydrogeologic parameters.
The above mentioned defaults will be overwritten for any parameters for which a non-zero entry is provided in "``REFCO``".
This allows the generation of these parameters internally for user-defined (:math:`P`, :math:`T`); it also allows for directly assigning user-desired values as, e.g., :math:`\rho_{liq}` = 1000 kg/m\ :sup:`3`, :math:`\mu_{liq}` = 10\ :sup:`-3` Pa s (:math:`equiv` 1 centipoise), etc.
A summary of EOS9 specifications appears in :numref:`tab:eos9.2`.

.. list-table:: Summary of EOS9.
    :name: tab:eos9.2
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (1, 1, 1, 6) water, isothermal (default, no other choices available)
    *   - Primary variables*†
        - | Saturated conditions:
          | (:math:`P_{liq}`): (water pressure: :math:`P_{liq}` ≥ :math:`P_{gas}`)
          | Unsaturated conditions:
          | (:math:`S_{liq}`): (water saturation: 0 < :math:`S_{liq}` < 1)

.. note::

    | \* The first primary variable may be initialized as :math:`X1` < 0, in which case it will be taken to denote capillary pressure, and will be converted internally to :math:`S_{liq}` in the initialization phase.
    | † Reference gas phase pressure, flow system temperature, and (optionally) thermophysical parameters of water density, viscosity, and compressibility may be specified through a fictitious ROCKS domain "``REFCO``".

In addition to specifying the primary thermodynamic variable on a default, domain, or grid block basis, EOS9 offers alternative ways of initializing flow problems.
The primary variable may be entered as a negative number upon initialization, in which case it will be taken to denote capillary pressure, and will be internally converted to :math:`S_l` in the initialization phase.
EOS9 can also initialize a flow problem with gravity-capillary equilibrium, relative to a user-specified reference elevation :math:`z_{ref}` of the water table.
This type of initialization will be engaged if the user enters a non-zero number in slot ``CWET`` in **ROCKS** domain "``REFCO``", in which case ``CWET`` will be taken to denote the water table elevation :math:`z_{ref}`, in units of meters.
Water pressure at :math:`z_{ref}` is taken equal to reference gas pressure, :math:`P_l(z_{ref}) = P_{gas}`, and is initialized as a function of grid block elevation according to :math:`P(z) = P_{gas} + \left( z_{ref} - z \right) \rho g`.
By convention, the z-axis is assumed to point upward.
In order to use this facility, the z-coordinates (grid block elevations) must be specified in the **ELEME**-data, which will be done automatically if internal *MESH* generation is used.

In the assignment of gravity-capillary equilibrium as just discussed, water saturations at "sufficiently" high elevations above the water table may end up being smaller than the irreducible water saturation :math:`S_{lr}` specified in the relative permeability function, which may or may not be consistent with the physical behavior of the flow system.
Users may optionally enforce that :math:`S_l` = :math:`S_{lr}` in regions where the capillary pressure function would dictate that :math:`S_{lr}` < :math:`S_{lr}`.
This is accomplished by entering an appropriate parameter in slot ``SPHT`` of **ROCKS** domain "``REFCO``", and works as follows.
The irreducible saturation :math:`S_{lr}` will be taken to be parameter ``RP(int(SPHT))`` of the relative permeability function.
As an example, for the ``IRP`` = 7 relative permeability function, irreducible water saturation is the parameter ``RP(2)``; therefore, for ``IRP`` = 7 the user should specify ``SPHT`` = 2.0 in "``REFCO``" to use this facility.

EOS9 differs from all of the other EOS modules in that, having only a single primary thermodynamic variable, the first (and here only) primary variable does not necessarily denote pressure.
This necessitates certain other coding adjustments.
For EOS9, the flow terms is assembled differently in subroutine *MULTI*, and the slot #6 of the PAR-array, which normally holds just the capillary pressure, represents total water pressure :math:`P_l = P_{gas} + P_{cap}`.
