EOS
===

TOUGH3 currently includes all equation-of-state (EOS) modules of the Version 2 of TOUGH2, as well as ECO2N (:cite:label:`pruess2005eco2n,pan2015eco2n`), ECO2M (:cite:label:`pruess2011eco2m`), EOS7C (:cite:label:`oldenburg2004eos7c`), EOS7CA (:cite:label:`oldenburg2015eos7ca`), and TMVOC (:cite:label:`pruess2002tmvoc`).

.. list-table:: Fluid property modules for TOUGH3.
    :name: tab:1
    :widths: 1 3
    :header-rows: 1
    :align: center

    *   - Module
        - Capabilities
    *   - :ref:`eos1`
        - water, water with tracer
    *   - :ref:`eos2`
        - water, CO\ :sub:`2`
    *   - :ref:`eos3`
        - water, air
    *   - :ref:`eos4`
        - water, air, with vapor pressure lowering
    *   - :ref:`eos5`
        - water, hydrogen
    *   - :ref:`eos7`
        - water, brine, air
    *   - :ref:`eos7r`
        - water, brine, air, parent-daughter radionuclides
    *   - EOS7C
        - water, brine, CO\ :sub:`2` (or N\ :sub:`2`), gas tracer, CH\ :sub:`4`
    *   - EOS7CA
        - water, brine, non-condensible gas, gas tracer, air
    *   - :ref:`eos8`
        - water, "dead" oil, non-condensible gas
    *   - :ref:`eos9`
        - variably-saturated isothermal flow according to Richard's equation
    *   - :ref:`ewasg`
        - water, salt (NaCl), non-condensible gas
    *   - TMVOC
        - water, water-soluble volatile organic chemicals, non-condensible gases, with biodegradation
    *   - :ref:`eco2n`
        - water, NaCl, CO\ :sub:`2`
    *   - ECO2M
        - water, NaCl, CO\ :sub:`2`, including transitions between super- and sub-critical conditions, and phase change between liquid gaseous CO\ :sub:`2`

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    eos1
    eos2
    eos3
    eos4
    eos5
    eos7
    eos7r
    eos8
    eos9
    ewasg
    eco2n
