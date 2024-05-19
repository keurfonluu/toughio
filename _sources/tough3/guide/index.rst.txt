User Guide
==========

The TOUGH3 simulator is developed for applications involving subsurface flow problems.
TOUGH3 solves mass and energy balance equations that describe fluid and heat flow in general multiphase, multicomponent, and multidimensional systems.
It fully accounts for the movement of gaseous, aqueous, and non-aqueous phases, the transport of latent and sensible heat, and the 
transition of components between the available phases, which may appear and disappear depending on the changing thermodynamic state of the system.
Advective fluid flow in each phase occurs under pressure, viscous, and gravity forces according to the multiphase extension of 
Darcy's law, which includes relative permeability and capillary pressure effects.
In addition, diffusive mass transport can occur in all phases.
The code includes Klinkenberg effects in the gas phase and vapor pressure lowering due to capillary and phase adsorption effects.
Heat flow occurs by conduction and convection, as well as radiative heat transfer according to the Stefan-Boltzmann equation.
Local equilibrium of all phases is assumed to describe the thermodynamic conditions.
TOUGH3 can simulate the injection or production of fluids and heat, and also includes different options for considering wellbore flow effects.
Effects of sorption onto the solid grains, radionuclide transport, or biodegradation can be simulated as well for certain EOS modules.

TOUGH3 uses an integral finite difference method (IFDM) for space discretization.
The IFDM (:cite:label:`narasimhan1976integrated`) avoids any reference to a global system of coordinates, and thus offers the advantage of being applicable to regular or irregular discretizations in one, two, and three dimensions.
The IFDM also makes it possible, by means of simple preprocessing of geometric data, to implement double-porosity, dual-permeability, or multiple interacting continua (MINC) methods for fractured media (:cite:label:`pruess1982fluid, pruess1985practical, pruess1983gminc`).
No particular price needs to be paid for this flexibility; indeed, for systems of regular grid blocks referring to a global coordinate system, the IFDM is completely equivalent to conventional finite differences.
Time is discretized fully implicitly as a first-order backward finite difference.
The implicit time-stepping and the 100% upstream weighting of flux terms at interfaces are necessary to avoid impractical time step limitations in flow problems involving phase (dis-)appearances, and to achieve unconditional stability (:cite:label:`peaceman2000fundamentals`).
The resulting strongly coupled, nonlinear algebraic equations are solved simultaneously using Newton-Raphson iterations for each time step, which involves the calculation of a Jacobian matrix and the solution of a set of linear equations.
Time steps are automatically adjusted during a simulation run, depending on the convergence rate of the iteration process.
Newton-Raphson increment weighting can also be adjusted if the iterations oscillate. 

TOUGH3 can simulate various fluid mixtures by means of separate EOS modules, which internally calculate the thermophysical properties of specific fluid mixtures, e.g., fluid density, viscosity, and enthalpy. Due to this flexibility to handle a variety of flow systems, TOUGH3 can be used for diverse application areas, such as geothermal reservoir engineering, geological carbon sequestration, natural gas reservoirs, nuclear waste isolation, environmental assessment and remediation, and flow and transport in variably saturated media and aquifers, among other applications that involve nonisothermal multiphase flows.

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    governing_equations
    numerical_methods
    initial_and_boundary_conditions
    preparation_of_input_data
    output_from_tough3
    relative_permeability_functions
    capillary_pressure_functions
