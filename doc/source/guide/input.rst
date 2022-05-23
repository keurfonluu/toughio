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
        "chemical_properties": dict,
        "non_condensible_gas": list[str],
        "times": list[int],
        "element_history": list[str],
        "connection_history": list[str],
        "generator_history": list[str],
        "output": dict,
        "elements": dict,
        "connections": dict,
        "initial_conditions": dict,
        "meshmaker": dict,
        "start": bool,
        "nover": bool,
    }


TOUGHREACT (flow.inp)
---------------------

TOUGHREACT flow input file is similar to TOUGH main input file but with the following additional parameters:

.. code-block::

    {

    }


TOUGHREACT (solute.inp)
-----------------------

.. code-block::

    {
        "title": str,
    }


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
