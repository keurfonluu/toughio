Input file
==========

A TOUGH input file is defined in a single human-readable and JSONable dictionary where each parameter is defined by an explicit keyword and associated a value. For instance, to define the title of the simulation:

.. code-block::

    parameters = {
        "title": "My simulation",
    }

:mod:`toughio` provides the function :func:`toughio.read_input` to read TOUGH input files.
Simply pass the input file name to the function as follows:

.. code-block::

    import toughio
    parameters = toughio.read_input("my_input_file.inp")

Similarly, the input file can be written using the function :func:`toughio.write_input`:

.. code-block::

    import toughio
    toughio.write_input("my_input_file.inp", parameters)

Optional arguments can be passed to both :func:`toughio.read_input` and :func:`toughio.write_input`, in particular ``file_format`` that tells the function how to correctly parse the input file. The following file formats are supported:

 - ``"tough"``: TOUGH main input file
 - ``"toughreact-flow"``: TOUGHREACT flow input file (same as ``"tough"`` with additional parameters)
 - ``"toughreact-solute"``: TOUGHREACT solute input file
 - ``"toughreact-chemical"``: TOUGHREACT chemical input file
 - ``"json"``: any of the above exported to JSON format

If the file format is not provided, it will be inferred from the file name and default to ``"tough"`` if the format cannot be guessed:

 - ``"tough"``: if the file name is ``"*/INFILE"``, ``"*/MESH"``, ``"*/GENER"`` or ``"*/INCON"``
 - ``"toughreact-flow"``: if the file name is ``"*/flow.inp"``
 - ``"toughsolute-flow"``: if the file name is ``"*/solute.inp"``
 - ``"toughchemical-flow"``: if the file name is ``"*/chemical.inp"``
 - ``"json"``: if the file name is ``"**/*.json"``

Note that both :func:`toughio.read_input` and :func:`toughio.write_input` merely act as file parsing functions and do not check the validity of the parameters which is left to the discretion of the user.


TOUGH (main)
------------

A TOUGH input file is defined as follows:

.. code-block::

    {
        "title": str, list[str],
        "eos": str,
        "isothermal": bool,
        "n_component": int,
        "n_phase": int,
        "rocks": dict,
        "default": dict,
        "solver": dict,
        "options": dict,
        "extra_options": dict,
        "more_options": dict,
        "selections": dict,
        "generators": list[dict],
        "diffusion": list[list],
        "times": list[float],
        "element_history": list[str],
        "connection_history": list[str],
        "generator_history": list[str],
        "output": dict,
        "elements": dict,
        "connections": dict,
        "initial_conditions": dict,
        "meshmaker": dict,
        "chemical_properties": dict,
        "non_condensible_gas": list[str],
        "start": bool,
        "nover": bool,
    }

The equation-of-state (EOS, block MULTI) is defined by the keyword ``"eos"`` which accepts any of these values:

 - ``"eos1"``
 - ``"eos2"``
 - ``"eos3"``
 - ``"eos4"``
 - ``"eos5"``
 - ``"eos7"``
 - ``"eos8"``
 - ``"eos9"``
 - ``"ewasg"``
 - ``"eco2n"``
 - ``"eco2n_v2"``
 - ``"eco2m"``
 - ``"tmvoc"``

:func:`toughio.write_input` will use the default EOS parameters (i.e., number of components and phases).
Alternatively, the number of components and phases can be set individually by the keywords ``"n_component"`` and ``"n_phase"``, respectively. These keywords supersede the values set by ``"eos"``.
Isothermal simulations can be carried out by setting ``"isothermal"`` to ``True``. In that case, the number of equations is equal to the number of components.


Rock properties
***************

Rock properties (block ROCKS) are defined using the keyword ``"rocks"`` as a dictionary where keys refer to the names of the rocks and the values to their properties.
Domainwise initial conditions (block INDOM) can also be defined by providing the keyword ``"initial_condition"``.
For instance, for a rock called ``"rock1"``, its properties are defined as follows:

.. code-block::

    "rock1": {
        "density": float,
        "porosity": float,
        "permeability": float, list[float],
        "conductivity": float,
        "specific_heat": float,
        "compressibility": float,
        "expansivity": float,
        "conductivity_dry": float,
        "tortuosity": float,
        "klinkenberg_parameter": float,
        "distribution_coefficient_3": float,
        "distribution_coefficient_4": float,
        "initial_condition": list[float],
        "relative_permeability": {
            "id": int,
            "parameters": list[float],
        },
        "capillarity": {
            "id": int,
            "parameters": list[float],
        },
    }

Default rock parameters can be set using the keyword ``"default"``. In that case, the default rock properties are used if they are not defined for a given rock.
Default relative permeability and capillary pressure models (block RPCAP) can also be defined in ``"default"`` using the keywords ``"relative_permeability"`` and ``"capillarity"``, respectively.
Note that the default initial conditions for all grid blocks correspond to the last record of block PARAM.


Options
*******

Computational parameters are simply defined in ``"options"`` as a dictionary organized as follows:

.. code-block::

    {
        "n_iteration": int,
        "n_cycle": int,
        "n_second": int,
        "n_cycle_print": int,
        "verbosity": int,
        "temperature_dependence_gas": float,
        "effective_strength_vapor": float,
        "t_ini": float,
        "t_max": float,
        "t_steps": float, list[float],
        "t_step_max": float,
        "t_reduce_factor": float,
        "gravity": "float",
        "mesh_scale_factor": "float",
        "eps1": "float",
        "eps2": "float",
        "w_upstream": "float",
        "w_newton": "float",
        "derivative_factor": "float",
    }

Additional options can be defined in ``"extra_options"`` (MOP) and ``"more_options"`` (block MOMOP) as dictionaries as well:

.. code-block::

    {
        1: int,
        2: int,
        ...
        N: int,
    }

where ``N`` denotes the maximum number of additional options in either ``"extra_options"`` or ``"more_options"``.

For some EOS, the keyword ``"selections"`` can be used to define integer and floating point options specific to an EOS:

.. code-block::

    {
        "integers": dict,
        "floats": list[float],
    }

where ``"integers"`` is defined as above (with ``N = 16``).


Sources and sinks
*****************

Sources and sinks (generators, block GENER) are defined in ``"generators"`` as a list of dictionaries repeated for each generator.
A generator is defined as follows:

.. code-block::

    {
        "label": str,
        "name": str,
        "nseq": int,
        "nadd": int,
        "nads": int,
        "type": str,
        "times": list[float],
        "rates": float, list[float],
        "specific_enthalpy": float, list[float],
        "layer_thickness": float,
        "n_layer": int,
    }

If ``"times"`` is provided, ``"rates"`` and ``"specific_enthalpy"`` must be provided as well as lists of equal length.


Diffusion
*********

Diffusion is enabled when the keyword ``"diffusion"`` is defined as an array (i.e., list of lists) of shape ``(n_component, n_phase)``.
In that case, the number of secondary parameters in block MULTI is automatically set to 8 (6 otherwise).


History
*******

Outputs can be generated at specific time steps in ``"times"`` (block TIMES) defined as a list where each value corresponds to a time step at which an output is desired.
Time-dependent outputs at specific element, connection or generator can be requested in ``"element_history"``, ``"connection_history"`` and ``"generator_history"`` as a list where each value is the label associated to the desired elements/connections.


Output
******

For TOUGH3/iTOUGH2, outputs can be customized in ``"output"`` (block OUTPU):

.. code-block::

    {
        "format": str,
        "variables": list[dict],
    }

where the desired variables to output are defined a list of dictionaries repeated for each variable. An output variable is defined as follows:

.. code-block::

    {
        "name": str,
        "options": int, list[int],
    }


Elements
********

Elements (block ELEME) are defined by keyword ``"elements"`` as a dictionary where keys refer to the labels of the elements and the values to their parameters.
For instance, for an element called ``"AAA00"``, its parameters are defined as follows:

.. code-block::

    "AAA00": {
        "nseq": int,
        "nadd": int,
        "material": str, int,
        "volume": float,
        "heat_exchange_area": float,
        "permeability_modifier": float,
        "center": list[float],
    }


Connections
***********

Connections (block CONNE) are defined by keyword ``"connections"`` as a dictionary where keys refer to the labels of the connections and the values to their parameters.
For instance, for a connection called ``"AAA00AAA01"``, its parameters are defined as follows:

.. code-block::

    "AAA00AAA01": {
        "nseq": int,
        "nadd": int,
        "permeability_direction": int,
        "nodal_distances": list[float],
        "interface_area": float,
        "gravity_cosine_angle": float,
        "radiant_emittance_factor": float,
    }


Initial conditions
******************

Elementwise initial conditions (block INCON) are defined by keyword ``"initial_conditions"`` as a dictionary where keys refer to the labels of the elements and the values to their parameters.
For instance, for an element called ``"AAA00"``, its initial conditions are defined as follows:

.. code-block::

    "AAA00": {
        "porosity": float,
        "userx": list[float],
        "values": list[float],
    }


Meshmaker
*********

Meshmaker parameters (block MESHM) are simply defined in ``"meshmaker"`` as a dictionary:

.. code-block::

    {
        "type": str,
        "parameters": list[dict],
        "angle": float,
    }

The keyword ``"type"`` denotes the type of mesh to generate. The following values are accepted:

 - ``"xyz"``
 - ``"rz2d"``
 - ``"rz2dl"``

If ``"type"`` is set to ``"xyz"``, each dictionary in ``"parameters"`` is defined as follows:

.. code-block::

    {
        "type": str,
        "n_increment": int,
        "sizes": float, list[float],
    }

Otherwise, for ``"rz2d"`` and ``"rz2dl"``:

.. code-block::

    {
        "type": str,
        "radii": list[float],
        "n_increment": int,
        "size": float,
        "radius": float,
        "radius_ref": float,
        "thicknesses": list[float],
    }

The keyword ``"type"`` denotes here the type of increments to generate. The following values are accepted:

 - ``"radii"``: keyword ``"radii"`` is required
 - ``"equid"``: keywords ``"n_increment"`` and ``"size"`` are required
 - ``"logar"``: keywords ``"n_increment"`` and ``"radius"`` are required, ``"radius_ref"`` is optional
 - ``"layer"``: keyword ``"thicknesses"`` is required


TMVOC
*****

Two additional keywords can be set to define parameters specific to TMVOC.

Chemical properties (block CHEMP) are defined using the keyword ``"chemical_properties"`` as a dictionary where keys refer to the names of the chemical species and the values to their properties.
For instance, for a chemical specie called ``"my_chemical"``, its properties are defined as follows:

.. code-block::

    "my_chemical": {
        "temperature_crit": float,
        "pressure_crit": float,
        "compressibility_crit": float,
        "pitzer_factor": float,
        "dipole_moment": float,
        "boiling_point": float,
        "vapor_pressure_a": float,
        "vapor_pressure_b": float,
        "vapor_pressure_c": float,
        "vapor_pressure_d": float,
        "molecular_weight": float,
        "heat_capacity_a": float,
        "heat_capacity_b": float,
        "heat_capacity_c": float,
        "heat_capacity_d": float,
        "napl_density_ref": float,
        "napl_temperature_ref": float,
        "gas_diffusivity_ref": float,
        "gas_temperature_ref": float,
        "exponent": float,
        "napl_viscosity_a": float,
        "napl_viscosity_b": float,
        "napl_viscosity_c": float,
        "napl_viscosity_d": float,
        "volume_crit": float,
        "solubility_a": float,
        "solubility_b": float,
        "solubility_c": float,
        "solubility_d": float,
        "oc_coeff": float,
        "oc_fraction": float,
        "oc_decay": float,
    }

Non-condensible gases (block NCGAS) can be listed using keyword ``"non_condensible_gas"`` as a list where each value is the name of a non-condensible gas.


TOUGHREACT (flow.inp)
---------------------

TOUGHREACT flow input file is similar to TOUGH main input file but with additional keywords.
In particular, a new keyword ``"react"`` is used to define options specific to TOUGHREACT.

.. code-block::

    {
        "react": {
            "options": dict,
            "output": {
                "format": int,
                "shape": list[int],
            },
            "poiseuille": {
                "start": list[float],
                "end": list[float],
                "aperture": float,
            },
        },
    }

where ``"options"`` represents the block REACT and is comparable to ``"more_options"`` (i.e., dictionary with integers as keys).
Note that ``"output"`` and ``"poiseuille"`` represent the blocks OUTPT and POISE, while ``"wdata"`` is written in block PARAM.


Rock properties
****************

Additional properties are available in ``"rocks"``. For a rock called ``"rock1"``, the new properties are defined as follows:

.. code-block::

    "rock1": {
        "porosity_crit": float,
        "tortuosity_exponent": float,
        "react_tp": {
            "id": int,
            "parameters": list[float],
        },
        "react_hcplaw": {
            "id": int,
            "parameters": list[float],
        },
    }


Options
*******

An additional keyword ``"react_wdata"`` can be used in ``"options"`` to write out flow data at selected elements.

.. code-block::

    {
        "wdata": list[str],
    }


Sources and sinks
*****************

Two additional parameters can be defined in ``"generators"`` for each generator to set up time-dependent thermal conductivity:

.. code-block::

    {
        "conductivity_times": list[float],
        "conductivity_factors": list[float],
    }

The two lists must have the same length.


Initial conditions
******************

An additional keyword ``"permeability"`` can be used in ``"initial_conditions"`` to define elementwise permeability.
The permeability of an element called ``"AAA00"`` is defined as follows:

.. code-block::

    "AAA00": {
        "permeability": list[float],
    }


TOUGHREACT (solute.inp)
-----------------------

A TOUGHREACT solute input file is defined as follows:

.. code-block::

    {
        "title": str,
        "options": dict,
        "flags": dict,
        "files": dict,
        "output": dict,
        "default": dict,
        "zones": dict,
    }

The functions :func:`toughio.read_input` and :func:`toughio.write_input` require ``MOPR(10)`` and ``MOPR(11)`` (defined in flow.inp) to correctly parse the file.


Options
*******

Options are simply defined in ``"options"`` as a dictionary organized as follows:

.. code-block::

    {
        "sl_min": float,
        "rcour": float,
        "ionic_strength_max": float,
        "mineral_gas_factor": float,
        "w_time": float,
        "w_upstream": float,
        "aqueous_diffusion_coefficient": float,
        "molecular_diffusion_coefficient": float,
        "n_iteration_tr": int,
        "eps_tr": float,
        "n_iteration_ch": int,
        "eps_ch": float,
        "eps_mb": float,
        "eps_dc": float,
        "eps_dr": float,
        "n_cycle_print": int,
    }

If ``MOPR(10) == 2``, additional keywords can be set to define convergence bounds:

.. code-block::

    {
        "n_iteration_1": int,
        "n_iteration_2": int,
        "n_iteration_3": int,
        "n_iteration_4": int,
        "t_increase_factor_1": float,
        "t_increase_factor_2": float,
        "t_increase_factor_3": float,
        "t_reduce_factor_1": float,
        "t_reduce_factor_2": float,
        "t_reduce_factor_3": float,
    }


Flags
*****

Flag options (i.e., chosen among a finite number of integer values) are defined using the keyword ``"flags"`` as a dictionary:

.. code-block::

    {
        "iteration_scheme": int,
        "reactive_surface_area": int,
        "solver": int,
        "n_subiteration": int,
        "gas_transport": int,
        "verbosity": int,
        "feedback": int,
        "coupling": int,
        "aqueous_concentration_unit": int,
        "mineral_unit": int,
        "gas_concentration_unit": int,
    }


Files
*****

Simulation input and output files are defined in ``"files"`` as a dictionary organized as follows:

.. code-block::

    {
        "thermodynamic_input": str,
        "iteration_output": str,
        "plot_output": str,
        "solid_output": str,
        "gas_output": str,
        "time_output": str,
    }


Output
******

The list of names or indices of the chemical species for which to output results can be provided using keyword ``"output"`` as a dictionary:

.. code-block::

    {
        "elements": list[str], list[int],
        "components": list[str], list[int],
        "minerals": list[str], list[int],
        "aqueous_species": list[str], list[int],
        "surface_complexes": list[str], list[int],
        "exchange_species": list[str], list[int],
    }


Zones
*****

Indices of chemical property zones are defined using the keyword ``"zones"`` as a dictionary where keys refer to the labels of the elements and the values to the zone indices associated.
For instance, for an element called ``"AAA00"``, its indices are defined as follows:

.. code-block::

    "AAA00": {
        "initial_water": int,
        "injection_water": int,
        "mineral": int,
        "initial_gas": int,
        "adsorption": int,
        "cation_exchange": int,
        "permeability_porosity": int,
        "linear_kd": int,
        "injection_gas": int,
        "element": int,  # Optional
        "sedimentation_velocity": float,
    }

If ``MOPR(11) == 2``, keyword ``"element"`` can be optionally used to set the water composition of this element to be recirculated as an injection water into the element specified by ``"injection_water"``.
If ``MOPR(11) == 1``, keyword ``"sedimentation_velocity"`` must be set.

Default zone indices are defined in a similar dictionary in ``"default"``.


TOUGHREACT (chemical.inp)
-------------------------

A TOUGHREACT chemical input file is defined as follows:

.. code-block::

    {
        "title": str,
        "primary_species": list[dict],
        "aqueous_kinetic": list[dict],
        "aqueous_species": list[str],
        "minerals": list[dict],
        "gaseous_species": list[dict],
        "surface_complexes": list[str],
        "kd_decay": list[dict],
        "exchanged_species": list[dict],
        "exchange_sites_id": int,
        "zones": {
            "initial_waters": list[dict],
            "injection_waters": list[dict],
            "minerals": list[dict],
            "initial_gases": list[list[dict]],
            "injection_gases": list[list[dict]],
            "permeability_porosity": list[dict],
            "adsorption": list[dict],
            "linear_kd": list[list[dict]],
            "cation_exchange": list[list[float]],
        },
    }

Sections that are not required may be skipped (i.e., not defined). Similarly, within all sections, some parameters depend on other parameters and can be ignored as well. If a keyword is indeed required yet undefined, default values will be used (0 for integers, 0.0 for floats, ``"''"`` for strings), and a warning will be prompted in the console.


Primary species
***************

Primary species are defined by keyword ``"primary_species"`` as a list of dictionaries repeated for each primary specie. A specie is defined as follows:

.. code-block::

    {
        "name": str,
        "transport": int,
    }


Aqueous kinetics
****************

Aqueous kinetics are defined by keyword ``"aqueous_kinetics"`` as a list of dictionaries for each kinetic reaction. A reaction is defined as follows:

.. code-block::

    {
        "id": int,
        "n_mechanism": int,
        "species": [
            {
                "name": str,
                "stoichiometric_coeff": float,
            }
            # Repeat for each specie
        ],
        "product": [
            {
                "specie": str,
                "flag": int,
                "power": float,
            }
            # Repeat for each specie
        ],
        "monod": [
            {
                "specie": str,
                "flag": int,
                "half_saturation": float,
            }
            # Repeat for each specie
        ],
        "inhibition": [
            {
                "specie": str,
                "flag": int,
                "constant": float,
            }
            # Repeat for each specie
        ],
        "reaction_affinity": {
            "id": int,
            "cf": float,
            "logK": float,
        },
    }


Secondary aqueous species
*************************

Secondary aqueous species are defined by keyword ``"aqueous_species"`` as a list of strings repeated for each aqueous specie. Each string is the name of a secondary aqueous specie.


Minerals
********

Minerals are defined by keyword ``"minerals"`` as a list of dictionaries repeated for each mineral. A mineral is defined as follows:

.. code-block::

    {
        "name": str,
        "type": int,
        "kinetic_constraint": int,
        "solid_solution": int,
        "precipitation_dry": int,
        "gap": float,
        "temp1": float,
        "temp2": float,
        "dissolution": {
            "k25": float,
            "rate_ph_dependence": int,
            "eta": float,
            "theta": float,
            "activation_energy": float,
            "a": float,
            "b": float,
            "c": float,
            "ph1": float,
            "slope1": float,
            "ph2": float,
            "slope2": float,
        },
        "precipitation": {
            "k25": float,
            "rate_ph_dependence": int,
            "eta": float,
            "theta": float,
            "activation_energy": float,
            "a": float,
            "b": float,
            "c": float,
            "volume_fraction_ini": float,
            "id": int,
            "extra_mechanisms": [
                {
                    "ki": float,
                    "activation_energy": float,
                    "species": [
                        {
                            "name": str,
                            "power": float,
                        }
                        # Repeat for each specie
                    ]
                }
                # Repeat for each mechanism
            ],
        },
    }


Gaseous species
***************

Gaseous species are defined by keyword ``"gaseous_species"`` as a list of dictionaries repeated for each gaseous specie. A specie is defined as follows:

.. code-block::

    {
        "name": str,
        "fugacity": int,
    }


Surface complexes
*****************

Surface complexes are defined by keyword ``"surface_complexes"`` as a list of strings repeated for each surface complex. Each string is the name of a surface complex.


Primary and gas species with Kd and decay
*****************************************

Primary aqueous and gas species with Kd and decay are defined by keyword ``"kd_decay"`` as a list of dictionaries repeated for each specie. A specie is defined as follows:

.. code-block::

    {
        "name": str,
        "decay_constant": float,
        "a": float,
        "b": float,
    }


Exchanged species
*****************

Exchangeable species are defined by keyword ``"exchanged_species"`` as a list of dictionaries repeated for each specie. A specie is defined as follows:

.. code-block::

    {
        "name": str,
        "reference": bool,
        "type": int,
        "site_coeffs": list,
    }

An additional keyword ``"exchange_sites_id"`` is used to define the model for the dependence of exchange sites on water saturation.


Initial and injection water zones
*********************************

Initial and injection water zones are defined in ``"zones"`` by keyword ``"initial_waters"`` and ``"injection_waters"``, respectively, as a list of lists repeated for each zone. Each zone is defined by a list of dictionaries for each specie:

.. code-block::
    
    {
        "temperature": float,
        "pressure": float,
        "rock": str,
        "species": [
            {
                "name": str,
                "flag": int,
                "guess": float,
                "ctot": float
                "log_fugacity": float,
                "nameq": str,
            }
            # Repeat for each specie
        ],
    }


Initial mineral zones
*********************

Initial mineral zones are defined in ``"zones"`` by keyword ``"minerals"`` as a list of lists repeated for each zone. Each zone is defined by a list of dictionaries for each specie:

.. code-block::

    {
        "rock": str,
        "species": [
            {
                "name": str,
                "volume_fraction_ini": float
                "flag": int,
                "radius": float,
                "area_ini": float,
                "area_unit": int,
            }
            # Repeat for each specie
        ],
    }


Initial and injection gas zones
*******************************

Initial and injection gas zones are defined in ``"zones"`` by keyword ``"initial_gases"`` and ``"injection_gases"``, respectively, as a list of lists repeated for each zone. Each zone is defined by a list of dictionaries for each specie:

.. code-block::

    {
        "name": str
        "partial_pressure": float,  # If initial gas
        "mole_fraction": float,  # If injection gas
    }


Permeability-porosity law zones
*******************************

Permeability-porosity law zones are defined in ``"zones"`` by keyword ``"permeability_porosity"`` as a list of lists repeated for each zone. Each zone is defined by a list of dictionaries for each specie:

.. code-block::

    {
        "id": int,
        "a": float,
        "b": float,
    }


Surface adsorption zones
************************

Surface adsorption zones are defined in ``"zones"`` by keyword ``"surface_adsorption"`` as a list of lists repeated for each zone. Each zone is defined by a list of dictionaries for each specie:

.. code-block::

    {
        "flag": int,
        "species": [
            {
                "name": str,
                "area_unit": int,
                "area": float,
            }
            # Repeat for each specie
        ],
    }


Linear Kd zones
***************

Linear Kd zones are defined in ``"zones"`` by keyword ``"linear_kd"`` as a list of lists repeated for each zone. Each zone is defined by a list of dictionaries for each specie:

.. code-block::

    {
        "name": str,
        "solid_density": float,
        "value": float,
    }


Cation exchange zones
*********************

Cation exchange zones are defined in ``"zones"`` by keyword ``"cation_exchange"`` as a list of lists repeated for each zone. Each zone is defined by a list of cation exchange capacity values for each exchange site.
