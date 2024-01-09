.. _governing-equations:

Governing Equations
===================

Mass-Balance Equations
----------------------

Here we describe the basic mass- and energy-balance equations solved by TOUGH3.
The equations for nonisothermal, multiphase, multicomponent flows in porous and fractured media can be written in the general form

.. math::
    :label: eq:1

    \frac{d}{dt} \int_{V_n} M^{\kappa} dV_n = \int_{\Gamma_n} \boldsymbol{\mathrm{F}}^{\kappa} \cdot \boldsymbol{\mathrm{n}} d\Gamma_n + \int_{V_n} q^{\kappa} dV_n

The integration is over an arbitrary subdomain Vn of the flow system under study, which is bounded by the closed surface :math:`\Gamma_n`.
The quantity M appearing in the accumulation term (left-hand side) represents the mass of component :math:`\kappa` (e.g., water, brine, air, CO\ :sub:`2`, tracer, radionuclides, VOC) or energy (:math:`\kappa = h`) per volume. :math:`\boldsymbol{\mathrm{F}}` denotes mass or heat flux, and :math:`q` denotes sinks and sources.
:math:`\boldsymbol{\mathrm{n}}` is a normal vector on the surface element :math:`d\Gamma_n`, pointing inward into :math:`V_n`.
Each term constituting the equations is described in detail in the following subsections.


Accumulation Terms
------------------

The general form of the mass accumulation term that includes equilibrium sorption on the solid grains is

.. math::
    :label: eq:2

    M^{\kappa} = \phi \sum_{\beta} S_{\beta} \rho_{\beta} X_{\beta}^{\kappa} + \left( 1 - \phi \right) \rho_R \rho_l X_l^{\kappa} K_d

where :math:`\phi` is porosity, :math:`S_{\beta}` is the saturation of phase :math:`\beta` (e.g., :math:`\beta` = gas, aqueous, non-aqueous phase liquid), :math:`\rho_{\beta}` is the density of phase :math:`\beta`, and :math:`X_{\beta}^{\kappa}`` is the mass fraction of component :math:`\kappa` in phase :math:`\beta`.
:math:`\rho_R` is the rock grain density, and :math:`K_d` is the aqueous (liquid) phase distribution coefficient.
The total mass of component :math:`\kappa` is obtained by summing over the fluid phases :math:`\beta`.
The heat accumulation term in a multiphase system is

.. math::
    :label: eq:3

    M^h = \left( 1 - \phi \right) \rho_R C_R T + \phi \sum_{\beta} S_{\beta} \rho_{\beta} u_{\beta}

where :math:`C_R` is the specific heat of the rock grains, :math:`T` is temperature, and :math:`u_{\beta}` is the specific internal energy of phase :math:`\beta`.


Flux Terms
----------

Advective mass flux is a sum of phase fluxes,

.. math::
    :label: eq:4

    \boldsymbol{\mathrm{F}}^{\kappa} \vert_{adv} = \sum_{\beta} X_{\beta}^{\kappa} \boldsymbol{\mathrm{F}}_{\beta}

where individual phase fluxes are given by a multiphase version of Darcy's law:

.. math::
    :label: eq:5

    \boldsymbol{\mathrm{F}}_{\beta} = \rho_{\beta} \boldsymbol{\mathrm{u}}_{\beta} = -k \frac{k_{r \beta} \rho_{\beta}}{\mu_{\beta}} \left( \nabla P_{\beta} - \rho_{\beta} \boldsymbol{\mathrm{g}} \right)

Here, :math:`u_{\beta}` is the Darcy velocity (volume flux) of phase :math:`\beta`, :math:`k` is absolute permeability, :math:`k_{r \beta}` is relative permeability to phase :math:`\beta`, :math:`\mu_{\beta}` is dynamic viscosity, and

.. math::
    :label: eq:6

    P_{\beta} = P + P_{c \beta}

is the fluid pressure in phase :math:`\beta`, which is the sum of the pressure :math:`P` of a reference phase (usually taken to be the gas phase) and the capillary pressure :math:`P_{c \beta}` (:math:`\le 0`).
:math:`\boldsymbol{\mathrm{g}}` is the vector of gravitational acceleration.
Vapor pressure lowering due to capillary and phase adsorption effects can be considered, and is modeled by Kelvin's equation (:cite:label:`edlefsen1943thermodynamics`),

.. math::
    :label: eq:7

    P_v \left( T, S_l \right) = f_{VPL} \left( T, S_l \right) P_{sat} \left( T \right)

where

.. math::
    :label: eq:8

    f_{VPL} = \exp \left( \frac{M_w P_{cl}\left( S_l \right)}{\rho_l R \left( T + 273.15 \right)} \right)

is the vapor pressure lowering factor.
:math:`P_v` is the vapor pressure, :math:`P_{sat}` is the saturated vapor pressure of bulk aqueous phase, :math:`P_{cl}` is the capillary pressure (i.e., the difference between aqueous and gas phase pressures), :math:`M_w` is the molecular weight of water, and :math:`R` is the universal gas constant.

Absolute permeability of the gas phase increases at low pressures according to the relation given by :cite:label:`klinkenberg1941permeability`

.. math::
    :label: eq:9

    k = k_{\infty} \left( 1 + \frac{b}{P} \right)

where :math:`k_{\infty}` is the permeability at "infinite" pressure, and :math:`b` is the Klinkenberg parameter.

In addition to Darcy flow, mass transport can also occur by diffusion.
Diffusive flux is modeled as follows:

.. math::
    :label: eq:10

    \boldsymbol{\mathrm{f}}_{\beta}^{\kappa} = -\phi \tau_0 \tau_{\beta} \rho_{\beta} d_{\beta}^{\kappa} \nabla X_{\beta}^{\kappa}

here :math:`d_{\beta}^{\kappa}` is the molecular diffusion coefficient for component :math:`\kappa` in phase :math:`\beta`, and :math:`\tau_0 \tau_{\beta}` is the tortuosity, which includes a porous medium dependent factor :math:`\tau_0` and a coefficient that depends on phase saturation :math:`S_{\beta}`, :math:`\tau_{\beta} = \tau_{\beta} \left( S_{\beta} \right)`.
For general two-phase conditions, the total diffusive flux is then given by

.. math::
    :label: eq:11

    \boldsymbol{\mathrm{f}}^{\kappa} = -\Sigma_l^{\kappa} \nabla X_l^{\kappa} - \Sigma_g^{\kappa} \nabla X_g^{\kappa}

where :math:`\Sigma_{\beta}^{\kappa} = \phi \tau_0 \tau_{\beta} \rho_{\beta} d_{\beta}^{\kappa}` is an effective diffusion coefficient in phase :math:`\beta`.
We have used this pragmatic approach because it is not possible to formulate a model for multiphase diffusion that would be accurate under all circumstances.
The basic Fick law works well for diffusion of tracer solutes that are present at low concentrations in a single-phase aqueous solution at rest with respect to the porous medium [1]_.

Several models are available to describe the dependence of tortuosity on porous medium properties and phase saturation.
For the relative permeability model, tortuosity will be taken as :math:`\tau_0 \tau_{\beta} \left( S_{\beta} \right) = \tau_0 k_{r \beta} \left( S_{\beta} \right)` with the user-specified porous medium dependent factor :math:`\tau_0`.
The :cite:label:`millington1961permeability` model, which has frequently been used for soils, yields non-zero tortuosity coefficients as long as phase saturation is non-zero [2]_.

.. math::
    :label: eq:12

    \tau_0 \tau_{\beta} = \phi^{1/3} S_{\beta}^{10/3}

For the constant diffusivity formulation, :math:`\tau_0 \tau_{\beta} = S_{\beta}` will be used.
This alternative corresponds to the formulation for gas diffusion in the original version of TOUGH2.
In the absence of phase partitioning and adsorptive effects, it amounts to effective diffusivity being approximately equal to :math:`d_{\beta}^{\kappa}`, independent of saturation. This can be seen by noting that the accumulation term in the phase :math:`\beta` contribution to the mass balance equation for component :math:`\kappa` is given by :math:`\phi S_{\beta} \rho_{\beta} X_{\beta}^{\kappa}`, approximately canceling out the :math:`\phi S_{\beta} \rho_{\beta}` coefficient in the diffusive flux.

TOUGH3 can model the pressure and temperature dependence of gas phase diffusion coefficients by the following equation (:cite:label:`vargaftik1975tables, walker1981studies`).

.. math::
    :label: eq:13

    d_g^{\kappa} \left( P, T \right) = d_g^{\kappa} \left( P_0, T_0 \right) \frac{P_0}{P} \left( \frac{T + 273.15}{273.15} \right)^{\theta}

At standard conditions of :math:`P_0` = 1 atm = 1.01325 bar and :math:`T_0` = 0˚C, the diffusion coefficient for vapor-air mixtures has a value of 2.13 x 10\ :sup:`-5` m\ :sup:`2`/s; parameter :math:`\theta` for the temperature dependence is 1.80.
Presently there are no provisions for inputting different values for the parameter :math:`\theta` of temperature dependence for different gas phase components.
Diffusion coefficients for the non-gaseous phases are taken as constants, with no provisions for temperature dependence of these parameters.

Heat flux includes conductive, convective, and radiative components:

.. math::
    :label: eq:14

    \boldsymbol{\mathrm{F}}^h = -\lambda \nabla T + \sum_{\beta} h_{\beta} \boldsymbol{\mathrm{F}}_{\beta} + f_{\sigma} \sigma_0 \nabla T^4

where :math:`\lambda` is the effective thermal conductivity, and :math:`h_{\beta}` is the specific enthalpy in phase :math:`\beta`, :math:`f_{\sigma}` is the radiant emittance factor, and :math:`\sigma_0` is the Stefan-Boltzmann constant.

.. [1] Many subtleties and complications can arise when multiple components diffuse in a multiphase flow system. Effective diffusivities in general may depend on all concentration variables, leading to nonlinear behavior especially when some components are present in significant (non-tracer) concentrations. Additional nonlinear effects arise from the dependence of tortuosity on phase saturations, and from coupling between advective and diffusive transport. For gases, the Fickian model has serious limitations even at low concentrations, which prompted the development of the "dusty gas" model that entails a strong coupling between advective and diffusive transport (:cite:label:`mason1983gas, webb1998review`) and accounts for molecular streaming effects (Knudsen diffusion) that become very important when the mean free path of gas molecules is comparable to pore sizes. Further complications arise for components that are both soluble and volatile, in which case diffusion in aqueous and gaseous phases may be strongly coupled via phase partitioning effects. An extreme case is the well-known enhancement of vapor diffusion in partially saturated media, which is attributed to pore-level phase change effects (:cite:label:`cass1984enhancement, webb1998review, webb1998enhanced`). These alternative models are not implemented in TOUGH3.

.. [2] It stands to reason that diffusive flux should vanish when a phase becomes discontinuous at low saturations, suggesting that saturation-dependent tortuosity should be related to relative permeability, i.e., :math:`\tau_{\beta} \left( S_{\beta} \right) \approx k_{r \beta} \left( S_{\beta} \right)`. However, for components that partition between liquid and gas phases, a more complex behavior may be expected. For example, consider the case of a volatile and water-soluble compound diffusing under conditions of low gas saturation where the gas phase is discontinuous. In this case we have :math:`k_{rg} \left( S_g \right) = 0` (because :math:`S_g \lt S_{gr}`), and :math:`k_rl \left( S_l = 1 - S_g \right) < 1`, so that a model equating saturation-dependent tortuosity to relative permeability would predict weaker diffusion than in single-phase liquid conditions. For compounds with "significant" volatility this would be unrealistic, as diffusion through isolated gas pockets would tend to enhance overall diffusion relative to single-phase liquid conditions.


Sink and Source Terms
---------------------

Sinks and sources are introduced by specifying the mass production (:math:`q \lt 0`) or injection (:math:`q \gt 0`) rates of fluids as well as heat flow.
Any of the mass components may be injected in an element at a constant or time-dependent mass rate, and the specific enthalpy of the injected fluid may be specified as well.Heat sources/sinks (with no mass injection) may be either constant or time dependent.

In the case of fluid production, a total mass production rate needs to be specified.
The phase composition of the produced fluid may be determined by the relative phase mobilities in the source element.
Alternatively, the produced phase composition may be specified to be the same as the phase composition in the producing element.
In either case, the mass fractions of the components in the produced phases are determined by the corresponding component mass fractions in the producing element.

TOUGH3 also includes different options for considering wellbore flow effects: a well on deliverability against specified bottomhole or wellhead pressure, or coupled wellbore flow.
Details are discussed below.


Deliverability Model
********************

Production wells may operate on deliverability against a prescribed flowing bottomhole pressure, :math:`P_{wb}`, with a productivity index PI (:cite:label:`coats1977geothermal`).
With this option, the mass production rate of phase :math:`\beta` from a grid block with phase pressure :math:`P_{\beta} \gt P_{wb}` is

.. math::
    :label: eq:15

    q_{\beta} = \frac{k_{r \beta}}{\mu_{\beta}} \rho_{\beta} \cdot PI \cdot \left( P_{\beta} - P_{wb} \right)

For steady radial flow, the productivity index of layer l is given by (Coats, 1977; Thomas, 1982)

.. math::
    :label: eq:16

    (PI)_l = \frac{2 \pi \left( k \Delta z_l \right)}{\log \left( r_e / r_w \right) + s - 1/2}

Here, :math:`\Delta z_l` denotes the layer thickness, :math:`\left( k \Delta z_l \right)` is the permeability-thickness product in layer :math:`l`, :math:`r_e` is the grid block radius, :math:`r_w` is the well radius, and :math:`s` is the skin factor. If the well is producing from a grid block which does not have cylindrical shape, an approximate PI can be computed by using an 
effective radius

.. math::
    :label: eq:17

    r_e = \sqrt{A / \pi}

where :math:`A` is the grid block area; e.g., :math:`A = \Delta x \cdot \Delta y` for an areal Cartesian grid.
More accurate expressions for specific well patterns and grid block shapes have been given in the literature (e.g., :cite:label:`peaceman2000fundamentals, coats1982effects`).

The rate of production for mass component :math:`\kappa` is

.. math::
    :label: eq:18

    \hat{q}^{\kappa} = \sum_{\beta} X_{\beta}^{\kappa} q_{\beta}

For wells that are screened in more than one layer (element), the flowing wellbore pressure :math:`P_{wb}` can be corrected to approximately account for gravity effects according to the depth-dependent flowing density in the wellbore.
Assuming that the open interval extends from layer :math:`l = ` at the 
bottom to :math:`l = L`` at the top, the flowing wellbore pressure in layer :math:`l`, :math:`P_{wb, l}`, is obtained from the wellbore pressure in layer :math:`l + 1`` immediately above it by means of the following recursion formula

.. math::
    :label: eq:19

    P_{wb, l} = P_{wb, l + 1} + \frac{g}{2} \left( \rho_l^f \Delta z_l + \rho_{l + 1}^f \Delta z_{l + 1}\right)

Here, :math:`g` is acceleration of gravity, and :math:`\rho_l^f` is the flowing density in the tubing opposite layer :math:`l`.
Flowing densities are computed using a procedure given by Coats (private communication, 1982). 
If wellbore pressure were zero, we would obtain the following volumetric production rate of phase :math:`\beta` from layer :math:`l`.

.. math::
    :label: eq:20

    r_{l, \beta} = \left( \frac{k_{r \beta}}{\mu_{\beta}} \right)_l \left( PI \right)_l P_{l, \beta}

The total volumetric flow rate of phase :math:`\beta` opposite layer :math:`l` is, for zero wellbore pressure

.. math::
    :label: eq:21

    r_{l, \beta}^T = \sum_{m=1}^l r_{m, \beta}

From this, we obtain an approximate expression for flowing density opposite layer :math:`l` which can be used in Eq. :math:numref:`eq:19`.

.. math::
    :label: eq:22

    \rho_l^f = \frac{\sum_{\beta} \rho_{l, \beta} r_{l, \beta}^T}{\sum_{\beta} r_{l, \beta}^T}

During fluid production or injection, the rate of heat removal or injection is determined by

.. math::
    :label: eq:23

    \hat{q}^h = \sum_{\beta} q_{\beta} h_{\beta}

where :math:`h_{\beta}` is the specific enthalpy of phase :math:`\beta`.


Coupled Wellbore Flow
*********************

Geothermal production wells typically operate at (nearly) constant wellhead pressures. 
However, as flow rate and flowing enthalpy change with time, wellbore pressure gradients and flowing bottomhole pressures will also change.
TOUGH3 cannot directly describe production from geothermal wells by solving equations for flow in the reservoir and flow in the wellbore in a fully coupled manner [3]_.
TOUGH3 uses an alternative approach (:cite:label:`murray1993toward`) in which the wellbore and reservoir simulations are performed separately.
This can be accomplished by running a wellbore flow simulator prior to the reservoir simulation for a range of flow rates :math:`q` and 
flowing enthalpies :math:`h` in order to generate a table of flowing bottomhole pressures :math:`P_{wb}`.

.. math::
    :label: eq:24

    P_{wb} = P_{wb} \left( q, h; P_{wh}, z, r_w \right)

In addition to the functional dependence on :math:`q` and :math:`h`, flowing bottomhole pressure is dependent on a number of well parameters.
These include wellhead pressure :math`P_{wh}`, feed zone depth :math:`z`, wellbore radius :math:`r_w`, friction factors, and possibly others.
By interpolating on these tabular data, Eq. :math:numref:`eq:24` can 
be directly inserted into the well source term, Eq. :math:numref:`eq:15`.
Reservoir flow equations that include a quasi-steady approximation to wellbore flow can then be solved with little added computational expense compared to the case where no wellbore flow effects are considered.
Advantages of representing wellbore flow effects through tabular data include increased robustness and computational efficiency.
It also makes it possible to use different wellbore simulators and two-phase flow correlations without any programming changes in the reservoir simulation code.

We have incorporated a tabular interpolation scheme for dynamic changes of flowing bottomhole pressure into TOUGH3.
Flowing enthalpy at the feed zone is known from phase mobilities and enthalpies calculated by the reservoir simulator.
The unknown well flow rate and flowing bottomhole pressure are obtained by Newton-Raphson iteration on

.. math::
    :label: eq:25

    R \left( q \right) = q - \left( \sum \frac{k_{r \beta}}{\mu_{\beta}} \rho_{\beta} \right) \cdot PI \cdot \left( P - P_{wb} \left( q, h \right )\right) = 0

The iterative solution of Eq. :math:numref:`eq:25` was embedded in the outer (Newtonian) iteration performed by TOUGH3 on the coupled mass and heat balance equations.
Additional computational work in comparison to conventional simulations with constant downhole pressure is insignificant.

The coupled wellbore flow capability as coded in TOUGH3 is limited to wells with a single feed zone and can only handle wellbore pressure effects from changing flow rates and enthalpies.
Effects from changing fluid composition, as, e.g., variable non-condensible gas content, are not modeled at present.

.. [3] The fully coupled approach was taken by :cite:label:`hadgu1995coupled` who coupled the reservoir simulator TOUGH (:cite:label:`pruess1987tough`) with the wellbore simulator WFSA (:cite:label:`hadgu1990multi`). T2Well (:cite:label:`pan2014t2well`) is also a coupled wellbore-reservoir simulator, which extends TOUGH2 to calculate the flow in both the wellbore and the reservoir simultaneously by introducing a special wellbore sub-domain. T2Well uses the drift-flux model and related conservation equations for describing transient two-phase nonisothermal flow in the wellbore sub-domain. T2Well will be implemented in TOUGH3 at a future date.


Semi-Analytical Conductive Heat Exchange
----------------------------------------

TOUGH3 provides options for modeling linear or radial conductive heat exchange with geologic formations where no fluid exchange is considered, using semi-analytical methods.
This is a much more efficient alternative to the approach that simply extends the computational grid into those formations and assigns small or vanishing permeability to them.
Even to achieve modest accuracy, the number of grid blocks in the heat flow domain could easily become comparable to, or even larger than, the number of grid blocks in the fluid flow domain, leading to a very inefficient calculation.
The semi-analytical methods require no grid blocks outside of the fluid flow domain, and permit better accuracy for short- and long-term heat exchange.
Note that radial and linear semi-analytical heat exchange cannot be combined in the current version of TOUGH3.


Linear Heat Exchange between a Reservoir and Confining Beds
***********************************************************

TOUGH3 uses the method of :cite:label:`vinsome1980simple`, which gives excellent 
accuracy for heat exchange between reservoir fluids and confining beds [4]_ such as may arise in geothermal injection and production operations.
Observing that the process of heat conduction tends to dampen out temperature variations, Vinsome and Westerveld suggested that caprock or baserock temperatures would vary smoothly even for strong and rapid temperature changes at the boundary of the conduction zone.
Arguing that heat conduction perpendicular to the conductive boundary is more important than parallel to it, they proposed to represent the temperature profile in a semi-infinite conductive layer by means of a simple trial function, as follows:

.. math::
    :label: eq:26

    T \left( x, t \right) - T_i = \left( T_f - T_i + px + qx^2 \right) \exp \left( -\frac{x}{d}\right)

Here, :math:`x` is the distance from the boundary, :math:`T_i` is initial temperature in the cap- or base-rock (assumed uniform), :math:`T_f` is the time-varying temperature at the cap- or base-rock boundary, :math:`p` and :math:`q` are time-varying fit parameters, and :math:`d` is the penetration depth for heat conduction, given by

.. math::
    :label: eq:27

    d = \frac{\sqrt{\Theta t}}{2}

where :math:`\Theta = \lambda / \rho C` is the thermal diffusivity, :math:`\lambda` the thermal conductivity, :math:`\rho` the density of the medium, and :math:`C` the specific heat.
In the context of a finite-difference simulation of nonisothermal flow, each 
grid block in the top and bottom layers of the computational grid will have an associated temperature profile in the adjacent impermeable rock as given by Eq. :math:numref:`eq:26`.
The coefficients :math:`p` and :math:`q` will be different for each grid block; they are determined concurrently with the flow simulation from the physical constraints of (1) continuity of heat flux across the boundary, and (2) energy conservation for the reservoir/confining layer system.

.. [4] This method is developed for calculating heat losses from the reservoir to caprock or baserock and predicting the temperature profile in a semi-infinite, homogeneous, conductive half-space confining bed.


Radial Heat Exchange between Fluids in a Wellbore and the Surrounding Formation
*******************************************************************************

Radial, conductive heat exchange between fluids in a discretized wellbore and the formation is calculated using a semi-analytical, time-convolution method.
Note that the time-dependent temperature evolution in the fully-discretized wellbore is calculated numerically.
At each time step, radial heat transfer with the formation is calculated by superposition of analytical solutions of heat flow that are dependent on the temperature differences between subsequent time steps.

:cite:label:`carlslaw1959conduction` provided an approximate solution for heat conduction between a cylinder and surrounding media where the temperature of the cylinder is maintained constant.
If the initial temperature difference between the two domains is :math:`\Delta T = T_w - T_f` (where :math:`T_w` and :math:`T_f` are the temperatures in the well and the formation, respectively), the heat flux :math:`q` from the wellbore to the formation can be calculated das the product of a heat transfer function and the temperature using Eq. :math:numref:`eq:28` for small values of the dimensionless time :math:`t_d = \alpha t / r_0^2`, where :math:`\alpha` is the thermal diffusivity and :math:`r_0` is the wellbore radius (m), and Eq. :math:numref:`eq:29` for large values of :math:`t_d`:

.. math::
    :label: eq:28

    q = f_1 \left( t_d \right) \cdot \Delta T = \frac{\lambda \Delta T}{r_0} \left( \left( \pi t_d \right)^{-0.5} + \frac{1}{2} - \frac{1}{4} \left( \frac{t_d}{\pi} \right)^{0.5} + \frac{1}{8} t_d - ... \right)

.. math::
    :label: eq:29

    q = f_2 \left( t_d \right) \cdot \Delta T = \frac{2 \lambda \Delta T}{r_0} \left( \frac{1}{\log \left( 4 t_d \right) - 2 \gamma} - \frac{\gamma}{\left( \log \left( 4 t_d \right) - 2 \gamma \right)^2} - ... \right)

Here, :math:`\lambda` is the thermal conductivity (W m\ :sup:`-1` K\ :sup:`-1`), and :math:`\gamma` is the Euler constant (0.57722).
The heat transfer functions :math:`f_1` and :math:`f_2` express the amount of heat flux with time due a unit temperature difference.
As shown in :cite:label:`zhang2011time`, the heat transfer functions :math:`f_1` and :math:`f_2` are approximately the same at the dimensionless time :math:`t_d` = 2.8.
Therefore, :math:`t_d` = 2.8 is considered the critical dimensionless time to switch from :math:`f_1` to :math:`f_2`.

During fluid injection and production, and as a result of the heat exchange processes, temperature changes continuously over time at any point within the wellbore and at the wellbore-formation interface.
Based on superposition, the radial heat flux across each wellbore element to the surrounding formation is a time-convolution result of varying temperature. The discretized form at each time step can be expressed as

.. math::
    :label: eq:30

    q_{total} = \sum_{i=1}^{d-1} f \left( t_d - t_i \right) \cdot \Delta T \left( t_i \right)

Here, :math:`t_d` represents the current time after :math:`d` time steps, and :math:`t_i` represents the time after :math:`i` time steps; the function :math:`f` is :math:`f_1` if :math:`t_d - t_i \le 2.8`, and :math:`f_2` if :math:`t_d - t_i \gt 2.8`.
The temperature difference :math:`\Delta T \left( t_i \right)` is the temperature in the well at time step :math:`i`, minus the formation temperature at the interface at the previous time step, i.e., :math:`\Delta T \left( t_i \right) = T_w \left( t_i \right) - T_f \left( t_{i - 1} \right)`.
