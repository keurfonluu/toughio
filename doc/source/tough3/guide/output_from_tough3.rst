.. _output_from_tough3:

Output from TOUGH3
==================

TOUGH3 produces a variety of printed output, most of which can be controlled by the user. 
In the initialization phase TOUGH3 writes out dimensions of problem-size dependent arrays and disk files in use to the standard output file (OUTPUT).
This is followed by documentation on block-by-block permeability modification, on settings of the ``MOP``- and ``MOP2``-parameters for choosing program options, and on the EOS-module.
During execution TOUGH3 can optionally generate a brief printout for Newtonian iterations and time steps.
The file *OUTPUT* also includes the volume- and mass-balances at each specified printout times or time step.

TOUGH3 generates a pre-defined selection of element, connection, or generation variables based on ``KDATA`` in block **PARAM** (see Table 9).
The list is not EOS-specific, except biomass, which will be included when simulating biodegradation reactions using TMVOC.
Separate output files in the selected format (either CSV for positive ``KDATA`` or TECPLOT for negative ``KDATA``) will be generated for element-, connection-, and sinks/sources-related outputs at user-specified simulation times in block **TIMES** or time step frequencies in block **PARAM**.

TOUGH3 allows the user to select the output variables to be printed using block **OUTPU**.
The user can choose any number of element-, connection-, and generation-related output variables.
A lumped set of primary variables or secondary parameters can be selected, and other information, such as grid-block or connection coordinates, index of elements, connection, or sinks/sources, and element names, can be included as well.
The list of the output variables is shown in :numref:`tab:8` in Section :ref:`tough3_input_format`. The header and unit of variables/parameters selected for printout will be generated accordingly.
An example **OUTPU** block is shown in :numref:`figure_11`; excerpts of resulting output files for element-, connection- and generation-related output variables are shown in :numref:`figure_12`, :numref:`figure_13` and :numref:`figure_14`, respectively.

.. code-block:: text
    :caption: Example CSV output file.
    
    "              ELEM","            SOURCE","               GEN"
    "                  ","                  ","               (W)"
    "TIME [sec]  0.31557600E+08"
    "             A1001","             HTR 1",  0.300000000000E+04
    "TIME [sec]  0.12559000E+09"
    "             A1001","             HTR 1",  0.300000000000E+04
    ...

.. list-table:: Standard output based on absolute value of ``KDATA``. abs(``KDATA``) = 1: a selection of element variables.
    :name: tab:kdata1
    :widths: 1 2
    :header-rows: 1
    :align: center

    *   - Output variable
        - Comment
    *   - Pressure
        -
    *   - Temperature
        - Only in nonisothermal mode
    *   - Saturation
        - Saturation of all phases
    *   - Mass fraction
        - Mass fraction of all components in all mobile phases
    *   - Relative permeability
        - Relative permeability of all mobile phases
    *   - Capillary pressure
        - Between mobile phases
    *   - Density
        - Density of all mobile phases
    *   - Porosity
        - 
    *   - Biomass
        - Biomass of all microbial populations (only for TMVOC)

.. list-table:: Standard output based on absolute value of ``KDATA``. abs(``KDATA``) = 2: in addition, a selection of connection variables.
    :name: tab:kdata2
    :widths: 1 2
    :header-rows: 1
    :align: center

    *   - Output variable
        - Comment
    *   - Heat flow
        - Only in nonisothermal mode
    *   - Total flow
        - 
    *   - Phase flow
        - Flow of all mobile phases
    *   - Diffusive flow
        - Only when ``NB`` = 8

.. list-table:: Standard output based on absolute value of ``KDATA``. abs(``KDATA``) = 3: in addition, a selection of connection variables.
    :name: tab:kdata3
    :widths: 1 2
    :header-rows: 1
    :align: center

    *   - Output variable
        - Comment
    *   - Generation rate
        - Mass (kg/s) or energy (J/s) rate depending on generation type
    *   - Flowing enthalpy
        - Only in nonisothermal mode
    *   - Fractional flow
        - Only for production
    *   - Wellbore pressure
        - Only for production wells operated on deliverability against specified bottomhole pressure

.. _figure_11:

.. code-block:: text
    :caption: Example data block OUTPU.

    OUTPU----1----*----2----*----3----*----4----*----5----*----6
    8
    PRESSURE
    SECONDARY               2    6
    SECONDARY               1    4
    MASS FRACTION           2    2
    FLOW                    1
    VELOCITY                1
    HEAT FLOW
    GENERATION RATE

.. _figure_12:

.. code-block:: text
    :caption: Element-related output variables in CSV format based on **OUTPU** block shown in :numref:`figure_11`.

    "              ELEM","            PRES_G","            PCAP_L","             DEN_G","           X_AIR_L"
    "                  ","              (PA)","              (PA)","         (KG/M**3)","               (-)"
    "TIME [sec]  0.31557600E+08"
    "             A1001",  0.145733984563E+06, -0.500000000000E+09,  0.729984424325E+00,  0.000000000000E+00
    "             A1002",  0.145733992876E+06, -0.333270877952E+08,  0.839804437107E+00,  0.000000000000E+00
    "             A1003",  0.130069098208E+06, -0.149548290610E+06,  0.755041253102E+00,  0.000000000000E+00
    "             A1004",  0.118768201640E+06, -0.375912049570E+05,  0.693490433326E+00,  0.000000000000E+00
    "             A1005",  0.109739217020E+06, -0.199789863209E+05,  0.644044319825E+00,  0.293927428376E-15
    "             A1006",  0.102044115154E+06, -0.109444612669E+05,  0.601696773695E+00,  0.274267136463E-10
    "             A1007",  0.100043502582E+06, -0.877952984850E+04,  0.676573675262E+00,  0.349785972071E-05 
    …
    "TIME [sec]  0.12559000E+09"
    "             A1001",  0.131667455445E+06, -0.500000000000E+09,  0.579679135438E+00,  0.000000000000E+00
    "             A1002",  0.131667427270E+06, -0.500000000000E+09,  0.652436733809E+00,  0.000000000000E+00
    "             A1003",  0.131667376616E+06, -0.500000000000E+09,  0.697207803100E+00,  0.000000000000E+00
    "             A1004",  0.131667303336E+06, -0.500000000000E+09,  0.731317756019E+00,  0.000000000000E+00
    "             A1005",  0.131667206441E+06, -0.500000000000E+09,  0.759680036685E+00,  0.000000000000E+00
    "             A1006",  0.125971775053E+06, -0.385373109044E+06,  0.732766156518E+00,  0.000000000000E+00
    "             A1007",  0.120105966675E+06, -0.609113801028E+05,  0.700795547905E+00,  0.000000000000E+00
    ...

.. _figure_13:

.. code-block:: text
    :caption: Connection-related output variables in CSV format based on **OUTPU** block shown in :numref:`figure_11`.

    "             ELEM1","             ELEM2","            FLOW_G","             VEL_G","              HEAT"
    "                  ","                  ","            (KG/S)","             (M/S)","               (W)"
    "TIME [sec]  0.31557600E+08"
    "             A1001","             A1002",  0.314097500713E-09,  0.442085908383E-09, -0.299974415519E+04
    "             A1002","             A1003", -0.117124968441E-02, -0.815791410995E-03, -0.299910711963E+04
    "             A1003","             A1004", -0.113996116095E-02, -0.668855689283E-03, -0.300203907460E+04
    "             A1004","             A1005", -0.111083200985E-02, -0.743130677782E-03, -0.300533553035E+04
    "             A1005","             A1006", -0.107980321381E-02, -0.905005010191E-03, -0.300885963338E+04
    "             A1006","             A1007", -0.292168383775E-03, -0.394691197242E-03, -0.301452215868E+04
    "             A1007","             A1008", -0.296897257092E-07, -0.400951136232E-07, -0.297658449442E+04
    …
    "TIME [sec]  0.12559000E+09"
    "             A1001","             A1002", -0.536396107829E-09, -0.109093702349E-08, -0.299835837082E+04
    "             A1002","             A1003", -0.246742921890E-08, -0.220645706376E-08, -0.299318958181E+04
    "             A1003","             A1004", -0.612573151962E-08, -0.338056616113E-08, -0.298393647773E+04
    "             A1004","             A1005", -0.118590967237E-07, -0.463183822453E-08, -0.296972471428E+04
    "             A1005","             A1006", -0.937133136787E-03, -0.278903292626E-03, -0.294927355061E+04
    "             A1006","             A1007", -0.111723414932E-02, -0.302832717904E-03, -0.295107682950E+04
    ...

.. _figure_14:

.. code-block:: text
    :caption: Generation-related output variables in CSV format based on **OUTPU** block shown in :numref:`figure_11`.

    "              ELEM","            SOURCE","               GEN"
    "                  ","                  ","               (W)"
    "TIME [sec]  0.31557600E+08"
    "             A1001","             HTR 1",  0.300000000000E+04
    "TIME [sec]  0.12559000E+09"
    "             A1001","             HTR 1",  0.300000000000E+04
    ...

By default, outputs are printed to both the default standard output file (OUTPUT) and the CSV format files.
Users may opt out printing output variables to the standard output file, particularly for large-scale simulations, to avoid creating a very big file.
TOUGH3 also offers an option to generate a file in a format suitable for TECPLOT.
The output variables written to the standard output file can be extracted for visualization using a reformatting program (such as EXT, a free post-processing program downloadable from the TOUGH website, which parses the standard output file along with spatial information provided in the *MESH* file and then generates a plot file in a format suitable for visualization, for instance, using TECPLOT).
It should be noted that EXT calculates the components of flow vectors at the centers of grid blocks; in the current version of the **OUTPU** feature, flow rates and velocities are simply printed for each connection.

Time series of some parameters for plotting can optionally be written to files in the CSV file format using blocks **FOFT** (for elements), **COFT** (for connections), and **GOFT** (for sinks and sources).
TOUGH3 will generate separate files for each element, connection, and sink/source.
While TOUGH3 has several input options to select the parameters to be written out, users desiring different parameters than what is coded in *FGTAB* should modify that subroutine.
