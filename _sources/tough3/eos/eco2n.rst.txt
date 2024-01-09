.. _eco2n:

ECO2N
=====

Injection of CO\ :sub:`2` into saline formations has been proposed as a means whereby emissions of heat-trapping greenhouse gases into the atmosphere may be reduced.
Such injection would induce coupled processes of multiphase fluid flow, heat transfer, chemical reactions, and mechanical deformation.
Several groups have developed simulation models for subsets of these processes.
The present report describes a fluid property module "ECO2N" for the general-purpose reservoir simulator TOUGH2 (:cite:label:`pruess1999tough2, pruess2004tough`), that can be used to model non-isothermal multiphase flow in the system H\ :sub:`2`\O - NaCl - CO\ :sub:`2`. TOUGH2/ECO2N represents fluids as
consisting of two phases: a water-rich aqueous phase, herein often referred to as "liquid", and a CO\ :sub:`2`-rich phase referred to as "gas".
In addition, solid salt may also be present.
The only chemical reactions modeled by ECO2N include equilibrium phase partitioning of water and carbon dioxide between the liquid and gaseous phases, and precipitation and dissolution of solid salt.
The partitioning of H\ :sub:`2`\O and CO\ :sub:`2` between liquid and gas phases is modeled as a function of temperature, pressure, and salinity, using the recently developed correlations of :cite:label:`spycher2003co2`.
Dissolution and precipitation of salt is treated by means of local equilibrium solubility.
Associated changes in fluid porosity and permeability may also be modeled.
All phases - gas, liquid, solid - may appear or disappear in any grid block during the course of a simulation.
Thermodynamic conditions covered include a temperature range from ambient to 100˚C (approximately), pressures up to 600 bar, and salinity from zero to fully saturated.
These parameter ranges should be adequate for most conditions encountered during disposal of CO\ :sub:`2` into deep saline aquifers.


Theoretical Background
----------------------

Fluid Phases and Thermodynamic Variables in the System Water-NaCl-CO\ :sub:`2`
******************************************************************************

In the two-component system water-CO\ :sub:`2`, at temperatures above the freezing point of water and not considering hydrate phases, three different fluid phases may be present: an aqueous phase that is mostly water but may contain some dissolved CO\ :sub:`2`, a liquid CO\ :sub:`2`-rich phase that may contain some water, and a gaseous CO\ :sub:`2`-rich phase that also may contain some water.
Altogether there may be seven different phase combinations (:numref:`fig:eco2n.1`).
If NaCl ("salt") is added as a third fluid component, the number of possible phase combinations doubles, as in each of the seven phase combinations depicted in :numref:`fig:eco2n.1` there may or may not be an additional phase consisting of solid salt.
Liquid and gaseous CO\ :sub:`2` may coexist along the saturated vapor pressure curve of CO\ :sub:`2`, which ends at the critical point (:math:`T_{crit}`, :math:`P_{crit}`) = (31.04˚C, 73.82 bar; :cite:label:`vargaftik1975tables`), see :numref:`fig:eco2n.2`.
At supercritical temperatures or pressures there is just a single CO\ :sub:`2`-rich phase.

.. figure:: ../figures/figure_eco2n_1.png
    :name: fig:eco2n.1
    :width: 50%

    Possible phase combinations in the system water-CO\ :sub:`2`. The phase designations are a - aqueous, l - liquid CO\ :sub:`2`, g - gaseous CO\ :sub:`2`. Separate liquid and gas phases exist only at subcritical conditions.

The present version of ECO2N can only represent a limited subset of the phase conditions depicted in :numref:`fig:eco2n.1`.
Thermophysical properties are accurately calculated for gaseous as well as for liquid CO\ :sub:`2`, but no distinction between gaseous and liquid CO\ :sub:`2` phases is made in the treatment of flow, and no phase change between liquid and gaseous CO\ :sub:`2` is treated.
Accordingly, of the seven phase combinations shown in :numref:`fig:eco2n.1`, ECO2N can represent the ones numbered 1 (single-phase aqueous with or without dissolved CO\ :sub:`2` and salt), 2 and 3 (a single CO\ :sub:`2`-rich phase that may be either liquid or gaseous CO\ :sub:`2`, and may include dissolved water), and 4 and 5 (two-phase conditions consisting of an aqueous and a single CO\ :sub:`2`-rich phase, with no distinction being made as to whether the CO\ :sub:`2`-rich phase is liquid or gas).
ECO2N cannot represent conditions 6 (two-phase mixture of liquid and gaseous CO\ :sub:`2`) and 7 (three-phase).
All sub- and super-critical CO\ :sub:`2` is considered as a single non-wetting phase, that will henceforth be referred to as "gas".
ECO2N may be applied to sub- as well as super-critical temperature and pressure conditions, but applications that involve sub-critical conditions are limited to systems in which there is no change of phase between liquid and gaseous CO\ :sub:`2`, and in which no mixtures of liquid and gaseous CO\ :sub:`2` occur.

.. figure:: ../figures/figure_eco2n_2.png
    :name: fig:eco2n.2
    :width: 75%

    Phase states of CO\ :sub:`2`.

Numerical modeling of the flow of brine and CO\ :sub:`2` requires a coupling of the phase behavior of water-salt-CO\ :sub:`2` mixtures with multiphase flow simulation techniques.
Among the various issues raised by such coupling is the choice of notation. There are long-established notational conventions in both fields, which may lead to conflicts and misunderstandings when they are combined.
In an effort to avoid confusion, we will briefly discuss notational issues pertaining to partitioning of CO\ :sub:`2` between an aqueous and a gaseous phase.

Phase partitioning is usually described in terms of mole fractions of the two components, which are denoted by :math:`x` and :math:`y`, respectively, where :math:`x_1` = :math:`x_{H_2O}` and :math:`x_2` = :math:`x_{CO_2}` specify mole fractions in the aqueous phase, while :math:`y_1` = :math:`y_{H_2O}` and :math:`y_2` = :math:`y_{CO_2}` give mole fractions in the gas phase (:cite:label:`prausnitz1998molecular, spycher2003co2`).
We follow this notation, except that we add the subscript "eq" to emphasize that these mole fractions pertain to equilibrium partitioning of water and CO\ :sub:`2` between co-existing aqueous and gas phases.
Accordingly, we denote the various mole fractions pertaining to equilibrium phase partitioning as :math:`x_{1, eq}`, :math:`x_{2, eq}`, :math:`y_{1, eq}`, and :math:`y_{2, eq}`, while the corresponding mass fractions are denoted using upper-case X and Y.
Mass fractions corresponding to single-phase conditions, where water and CO\ :sub:`2` concentrations are not constrained by phase equilibrium relations, are denoted by :math:`X_1` (for water) and :math:`X_2` (for CO\ :sub:`2`) in the aqueous phase, and by :math:`Y_1` and :math:`Y_2` in the gas phase.

In the numerical simulation of brine-CO\ :sub:`2` flows, we will be concerned with the fundamental thermodynamic variables that characterize the brine-CO\ :sub:`2` system, and their change with time in different subdomains (grid blocks) of the flow system.
Four "primary variables" are required to define the state of water-NaCl-CO\ :sub:`2` mixtures, which according to conventional TOUGH2 useage are denoted by :math:`X_1`, :math:`X_2`, :math:`X_3`, and :math:`X_4`.
A summary of the fluid components and phases modeled by ECO2N, and the choice of primary thermodynamic variables, appears in :numref:`tab:eco2n.1`.
Different variables are used for different phase conditions, but two of the four primary variables are the same, regardless of the number and nature of phases present.
This includes the first primary variable :math:`X_1`, denoting pressure, and the fourth primary variable :math:`X_4` which is temperature.
The second primary variable pertains to salt and is denoted :math:`X_{sm}` rather than :math:`X_2` to avoid confusion with :math:`X_2`, the CO\ :sub:`2` mass fraction in the liquid phase.
Depending upon whether or not a precipitated salt phase is present, the variable :math:`X_{sm}` has different meaning.
When no solid salt is present, :math:`X_{sm}` denotes :math:`X_s`, the salt mass fraction referred to the two-component system water-salt.
When solid salt is present, :math:`X_s` is no longer an independent variable, as it is determined by the equilibrium solubility of NaCl, which is a function of temperature.
In the presence of solid salt, for reasons that are explained below, we use as second primary variable the quantity "solid saturation plus ten", :math:`X_{sm}` = :math:`S_s` + 10.
Here, :math:`S_s` is defined in analogy to fluid saturations and denotes the fraction of void space occupied by solid salt.

The physical range of both :math:`X_s` and :math:`S_s` is (0, 1); the reason for defining :math:`X_{sm}` by adding a number 10 to :math:`S_s` is to enable the presence or absence of solid salt to be recognized simply from the numerical value of the second primary variable.
As had been mentioned above, the salt concentration variable :math:`X_s` is defined with respect to the two-component system H\ :sub:`2`\O - NaCl.
This choice makes the salt concentration variable independent of CO\ :sub:`2` concentration, which simplifies the calculation of the partitioning of the H\ :sub:`2`\O and CO\ :sub:`2` components between the aqueous and gas phases (see below).
In the three-component system H\ :sub:`2`\O - NaCl - CO\ :sub:`2`, the total salt mass fraction in the aqueous phase will for given :math:`X_s` of course depend on CO\ :sub:`2` concentration.
Salt mass fraction in the two-component system H\ :sub:`2`\O - NaCl can be expressed in terms of salt molality (moles m of salt per kg of water) as follows

.. math::
    :label: eq:eco2n.1

    X_s = \frac{m M_{NaCl}}{1000 + m M_{NaCl}}

Here :math:`M_{NaCl}` = 58.448 is the molecular weight of NaCl, and the number 1000 appears in the denominator because molality is defined as moles per 1000 g of water.
For convenience we also list the inverse of Eq. :math:numref:`eq:eco2n.1`.

.. math::
    :label: eq:eco2n.2

    m = \frac{1000 \frac{X_s}{M_{NaCl}}}{1 - X_s}

The third primary variable X3 is CO\ :sub:`2` mass fraction (:math:`X_2`) for single-phase conditions (only aqueous, or only gas) and is "gas saturation plus ten" (:math:`S_g` + 10) for two-phase (aqueous and gas) conditions.
The reason for adding 10 to :math:`S_g` is analogous to the conventions adopted for the second primary variable, namely, to be able to distinguish single-phase conditions (0 ≤ :math:`X_3` ≤ 1) from two-phase conditions (10 ≤ :math:`X_3` ≤ 11).
In single-phase conditions, the CO\ :sub:`2` concentration variable :math:`X_2` is "free", i.e., it can vary continuously within certain parameter ranges, while in two-phase aqueous-gas conditions, :math:`X_2` has a fixed value :math:`X_{2, eq}` that is a function of temperature, pressure, and salinity (see below).
Accordingly, for single-phase conditions :math:`X_2` is included among the independent primary variables (= :math:`X_3`), while for two-phase conditions, :math:`X_2` becomes a "secondary" parameter that is dependent upon primary variables (:math:`T`, :math:`P`, :math:`X_s`).
"Switching" primary variables according to phase conditions present provides a very robust and stable technique for dealing with changing phase compositions.

Initialization of a simulation with TOUGH2/ECO2N would normally be made with the internally used primary variables as listed in :numref:`tab:eco2n.1`.
For convenience of the user, additional choices are available for initializing a flow problem.

.. list-table:: Summary of ECO2N.
    :name: tab:eco2n.1
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: NaCl
          | #3: CO\ :sub:`2`
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (3, 4, 3, 6) water, air, oil, nonisothermal (default)
          | (3, 3, 3, 6) water, air, oil, isothermal
          | Molecular diffusion can be modeled by setting ``NB`` = 8
    *   - Primary variables
        - | Single-phase conditions (only aqueous, or only gas)*:
          | (:math:`P`, :math:`X_{sm}`, :math:`X_3`, :math:`T`): (pressure, salt mass fraction in two-component water-salt system or solid saturation plus ten, CO\ :sub:`2` mass fraction in the aqueous phase or in the gas phase, in the three-component system water-salt-CO\ :sub:`2`, temperature)
          | Two-phase conditions (aqueous and gas)*:
          | (:math:`P`, :math:`X_{sm}` + 10, :math:`S_g`, :math:`T`): (pressure, salt mass fraction in two-component water-salt system or solid saturation plus ten, gas phase saturation, temperature)

.. note::

    \* When discussing fluid phase conditions, we refer to the potentially mobile (aqueous and gas) phases only; in all cases solid salt may precipitate or dissolve, adding another active phase to the system.


Phase Composition
^^^^^^^^^^^^^^^^^

The partitioning of H\ :sub:`2`\O and CO\ :sub:`2` among co-existing aqueous and gas phases is calculated from a slightly modified version of the correlations developed in (:cite:label:`spycher2005co2`).
These correlations were derived from the requirement that chemical potentials of all components must be equal in different phases.
For two-phase conditions, they predict the equilibrium composition of liquid (aqueous) and gas (CO\ :sub:`2`-rich) phases as functions of temperature, pressure, and salinity, and are valid in the temperature range 12˚C ≤ :math:`T` ≤ 110˚C, for pressures up to 600 bar, and salinity up to saturated NaCl brines.
In the indicated parameter range, mutual solubilities of H\ :sub:`2`\O and CO\ :sub:`2` are calculated with an accuracy typically within experimental uncertainties.
The modification made in ECO2N is that CO\ :sub:`2` molar volumes are calculated using a tabular EOS based on Altunin's correlation (:cite:label:`altunin1975thermophysical`), instead of the Redlich-Kwong equation of state used in (:cite:label:`spycher2005co2`). 
This was done to maintain consistency with the temperature and pressure conditions for phase change between liquid and gaseous conditions used elsewhere in ECO2N.
Altunin's correlations yield slightly different molar volumes than the Redlich-Kwong EOS whose parameters were fitted by :cite:label:`spycher2005co2` to obtain the best overall match between observed and predicted CO\ :sub:`2` concentrations in the aqueous phase.
The (small) differences in Altunin's molar volumes cause predictions for the mutual solubility of water and CO\ :sub:`2` to be somewhat different also. However, the differences are generally small, see :numref:`fig:eco2n.3` to :numref:`fig:eco2n.5`.

.. figure:: ../figures/figure_eco2n_3.png
    :name: fig:eco2n.3
    :width: 75%

    Dissolved CO\ :sub:`2` mass fractions in two-phase system at :math:`T` = 30˚C for pure water (0m) and 4-molal NaCl brine. Lines represent the original correlation of :cite:label:`spycher2005co2` that uses a Redlich-Kwong EOS for molar volume of CO\ :sub:`2`. Symbols represent data calculated by ECO2N in which the molar volume of CO\ :sub:`2` is obtained from the correlations of :cite:label:`altunin1975thermophysical`.

.. figure:: ../figures/figure_eco2n_4.png
    :name: fig:eco2n.4
    :width: 75%

    H\ :sub:`2`\O mass fractions in gas in two-phase system at :math:`T` = 30˚C for pure water (0m) and 4-molal NaCl brine. Lines represent the original correlation of :cite:label:`spycher2005co2` that uses a Redlich-Kwong EOS for molar volume of CO\ :sub:`2`. Symbols represent data calculated by ECO2N in which the molar volume of CO\ :sub:`2` is obtained from the correlations of :cite:label:`altunin1975thermophysical`.

.. figure:: ../figures/figure_eco2n_5.png
    :name: fig:eco2n.5
    :width: 75%

    Concentration of water in gas and CO\ :sub:`2` in the liquid (aqueous) phase at (:math:`T`, :math:`P`) = (45˚C, 216.18 bar), for salinities ranging from zero to fully saturated. Lines were calculated from the correlation of :cite:label:`spycher2005co2` that uses a Redlich-Kwong EOS for molar volume of CO\ :sub:`2`. Symbols represent data calculated by ECO2N from a modified correlation in which the molar volume of CO\ :sub:`2` is obtained from the correlations of :cite:label:`altunin1975thermophysical`.

For conditions of interest to geologic dispoal of CO\ :sub:`2`, equilibrium between aqueous and gas phases corresponds to a dissolved CO\ :sub:`2` mass fraction in the aqueous phase, :math:`X_{2, eq}`, on the order of a few percent, while the mass fraction of water in the gas phase, :math:`Y_{1, eq}`, is a fraction of a percent, so that gas phase CO\ :sub:`2` mass fraction :math:`Y_{2, eq}` = 1 - :math:`Y_{1, eq}` is larger than 0.99.
The relationship between CO\ :sub:`2` mass fraction :math:`X_3` and phase composition of the fluid mixture is as follows (see :numref:`fig:eco2n.6`):

- :math:`X_3` < :math:`X_{2, eq}` corresponds to single-phase liquid conditions;
- :math:`X_3` > :math:`X_{2, eq}` corresponds to single-phase gas;
- intermediate values :math:`X_{2, eq}` ≤ :math:`X_3` ≤ :math:`Y_{2, eq}` correspond to two-phase conditions with different proportions of aqueous and gas phases.

Dissolved NaCl concentrations may for typical sequestration conditions range as high as 6.25 molal.
This corresponds to mass fractions of up to :math:`X_{sm}` = 26.7% in the two-component system water-salt.
Phase conditions as a function of :math:`X_{sm}` are as follows:

- :math:`X_{sm}` ≤ :math:`XEQ` corresponds to dissolved salt only;
- :math:`X_{sm}` > :math:`XEQ` corresponds to conditions of a saturated NaCl brine and solid salt.

.. figure:: ../figures/figure_eco2n_6.png
    :name: fig:eco2n.6
    :width: 75%

    CO\ :sub:`2` phase partitioning in the system H\ :sub:`2`\O - NaCl - CO\ :sub:`2`. The CO\ :sub:`2` mass fraction in brine-CO\ :sub:`2` mixtures can vary in the range from 0 (no CO\ :sub:`2`) to 1 (no brine). :math:`X_{2, eq}` and :math:`Y_{2, eq}` denote, respectively, the CO\ :sub:`2` mass fractions in aqueous and gas phases corresponding to equilibrium phase partitioning in two-phase conditions. Mass fractions less than :math:`X_{2, eq}` correspond to conditions in which only an aqueous phase is present, while mass fractions larger than :math:`Y_{2, eq}` correspond to single-phase gas conditions. Mass fractions intermediate between :math:`X_{2, eq}` and :math:`Y_{2, eq}` correspond to two-phase conditions with different proportions of aqueous and gas phases.


Phase Change
^^^^^^^^^^^^

In single-phase (aqueous or gas) conditions, the third primary variable X3 is the CO\ :sub:`2` mass fraction in that phase.
In single-phase aqueous conditions, we must have :math:`X_3` ≤ :math:`X_{2, eq}`, while in single-phase gas conditions, we must have :math:`X_3` ≥ :math:`Y_{2, eq}`.
The possibility of phase change is evaluated during a simulation by monitoring :math:`X_3` in each grid block.
The criteria for phase change from single-phase to two-phase conditions may be written as follow:

- single-phase aqueous conditions: a transition to two-phase conditions (evolution of a gas phase) will occur when :math:`X_3` > :math:`X_{2, eq}`;
- single-phase gas conditions: a transition to two-phase conditions (evolution of an aqueous phase) will occur when :math:`X_3` < :math:`Y_{2, eq}` = 1 - :math:`Y_{1, eq}`.

When two-phase conditions evolve in a previously single-phase grid block, the third primary variable is switched to :math:`X_3` = :math:`S_g` + 10.
If the transition occurred from single-phase liquid conditions, the starting value of :math:`S_g` is chosen as 10\ :sup:`-6`; if the transition occurred from single-phase gas, the starting value is chosen as 1 - 10\ :sup:`-6`.

In two-phase conditions, the third primary variable is :math:`X_3` = :math:`S_g` + 10.
For two-phase conditions to persist, :math:`X_3` must remain in the range (10, 11 - :math:`S_s`).
Transitions to single-phase conditions are recognized as follows:

- if :math:`X_3` < 10 (i.e., :math:`S_g` < 0): gas phase disappears; make a transition to single-phase liquid conditions;
- if :math:`X_3` > 11 - :math:`S_s` (i.e., :math:`S_g` > 1 - :math:`S_s`): liquid phase disappears; make a transition to single-phase gas conditions.

Phase change involving (dis-)appearance of solid salt is recognized as follows.
When no solid salt is present, the second primary variable :math:`X_{sm}` is the concentration (mass fraction referred to total water plus salt) of dissolved salt in the aqueous phase.
The possibility of precipitation starting is evaluated by comparing :math:`X_{sm}` with :math:`XEQ`, the equilibrium solubility of NaCl at prevailing temperature.
If :math:`X_{sm}` ≤ :math:`XEQ` no precipitation occurs, whereas for :math:`X_{sm}` > :math:`XEQ` precipitation starts.
In the latter case, variable :math:`X_{sm}` is switched to :math:`S_s` + 10, where solid saturation :math:`S_s` is initialized with a small non-zero value (10\ :sup:`-6`).
If a solid phase is present, the variable :math:`X_{sm}` = :math:`S_s` + 10 is monitored.
Solid phase disappears if :math:`X_{sm}` < 10, in which case primary variable :math:`X_{sm}` is switched to salt concentration, and is initialized as slightly below saturation, :math:`X_{sm}` = :math:`XEQ` - 10\ :sup:`-6`.


Conversion of Units
^^^^^^^^^^^^^^^^^^^

The :cite:label:`spycher2005co2` model for phase partitioning in the system H\ :sub:`2`\O-NaCl-CO\ :sub:`2` is formulated in molar quantities (mole fractions and molalities), while TOUGH2/ECO2N describes phase compositions in terms of mass fractions.
This section presents the equations and parameters needed for conversion between the two sets of units.
The conversion between various concentration variables (mole fractions, molalities, mass fractions) does not depend upon whether or not concentrations correspond to equilibrium between liquid and gas phases; accordingly, the
relations given below are valid regardless of the magnitude of concentrations.

Let us consider an aqueous phase with dissolved NaCl and CO\ :sub:`2`. For a solution that is m-molal in NaCl and n-molal in CO\ :sub:`2`, total mass per kg of water is

.. math::
    :label: eq:eco2n.3

    M = 1000 (g H_2 O) + m M_{NaCl} (g NaCl) + n M_{CO_2} (g CO_2)

where :math:`M_{NaCl}` and M_{CO_2} are the molecular weights of NaCl and CO\ :sub:`2`, respectively (see :numref:`tab:eco2n.2`).
Assuming NaCl to be completely dissociated, the total moles per kg of water are

.. math::
    :label: eq:eco2n.4

    m_T = \frac{1000}{M_{H_2 O}} + 2m + n

The :cite:label:`spycher2005co2` correlations provide CO\ :sub:`2` mole fraction :math:`x_2` in the aqueous phase and H\ :sub:`2`\O mole fraction :math:`y_1` in the gas phase as functions of temperature, pressure, and salt concentration (molality).
For a CO\ :sub:`2` mole fraction x2 we have :math:`n` = :math:`x_2 m_T` from which, using Eq. :math:numref:`eq:eco2n.4`, we obtain

.. math::
    :label: eq:eco2n.5

    n = \frac{x_2 \left( 2 m + \frac{1000}{M_{H_2 O}} \right)}{1 - x_2}

CO\ :sub:`2` mass fraction :math:`X_2` in the aqueous phase is obtained by dividing the CO\ :sub:`2` mass in :math:`n` moles by the total mass

.. math::
    :label: eq:eco2n.6

    X_2 = \frac{n M_{CO_2}}{1000 + m M_{NaCl} + n M_{CO_2}}

Water mass fraction :math:`Y_1` in the CO\ :sub:`2`-rich phase is simply

.. math::
    :label: eq:eco2n.7

    Y_1 = \frac{y1 M_{H_2 O}}{y1 M_{H_2 O} + \left( 1 - y_1 \right) M_{CO_2}}

The molecular weights of the various species are listed in :numref:`tab:eco2n.2` (:cite:label:`evans1982atomic`).

.. list-table:: Molecular weights in the system H\ :sub:`2`\O-NaCl-CO\ :sub:`2`.
    :name: tab:eco2n.2
    :header-rows: 1
    :align: center

    *   - Species
        - Mol. weight
    *   - H\ :sub:`2`\O
        - 18.016
    *   - Na
        - 22.991
    *   - Cl
        - 35.457
    *   - NaCl
        - 58.448
    *   - CO\ :sub:`2`
        - 44.0


Thermophysical Properties of Water-NaCl-CO\ :sub:`2` Mixtures
*************************************************************

Thermophysical properties needed to model the flow of water-salt-CO\ :sub:`2` mixtures in porous media include density, viscosity, and specific enthalpy of the fluid phases as functions of temperature, pressure, and composition, and partitioning of components among the fluid phases.
Many of the needed parameters are obtained from the same correlations as were used in the EWASG property module of TOUGH2 (:cite:label:`battistelli1997simulator`).
EWASG was developed for geothermal applications, and consequently considered conditions of elevated temperatures > 100˚C, and modest CO\ :sub:`2` partial pressures of order 1-10 bar.
The present ECO2N module targets the opposite end of the temperature and pressure range, namely, modest temperatures below 110˚C, and high CO\ :sub:`2` pressures up to several hundred bar.

Water properties in TOUGH2/ECO2N are calculated, as in other members of the TOUGH family of codes, from the steam table equations as given by the International Formulation Committee (:cite:label:`ifc1967formulation`).
Properties of pure CO\ :sub:`2` are obtained from correlations developed by :cite:label:`altunin1975thermophysical`.
We began using Altunin's correlations in 1999 when a computer program implementingthem was conveniently made available to us by Victor Malkovsky of the Institute of Geology of Ore Deposits, Petrography, Mineralogy and Geochemistry (IGEM) of the Russian Academy of Sciences, Moscow.
Altunin's correlations were subsequently extensively cross-checked against experimental data and alternative PVT formulations, such as :cite:label:`span1996new`.
They were found to be very accurate (:cite:`garcia2003fluid`), so there is no need to change to a different formulation.

Altunin's correlations are not used directly in the code, but are used ahead of a TOUGH2/ECO2N simulation to tabulate density, viscosity, and specific enthalpy of pure CO\ :sub:`2` on a regular grid of (:math:`T`, :math:`P`)-values.
These tabular data are provided to the ECO2N module in a file called
"CO2TAB", and property values are obtained during the simulation by means of bivariate interpolation.
:numref:`fig:eco2n.7` shows the manner in which CO\ :sub:`2` properties are tabulated, intentionally showing a coarse (:math:`T`, :math:`P`)-grid so that pertinent features of the tabulation may be better seen.
(For actual calculations, we use finer grid spacings; the CO2TAB data file distributed with ECO2N covers the range 3.04 ˚C ≤ :math:`T` ≤ 103.04 ˚C with :math:`\Delta T` = 2˚C and 1 bar ≤ :math:`P` ≤ 600 bar with :math:`\Delta T` ≤ 4 bar in most cases.
The ECO2N distribution includes a utility program for generating CO2TAB files if users desire a different (:math:`T`, :math:`P`)-range or different increments).
As shown in :numref:`fig:eco2n.7`, the tabulation is made in such a way that for sub-critical conditions the saturation line is given by diagonals of the interpolation quadrangles.
On the saturation line, two sets of data are provided, for liquid and gaseous CO\ :sub:`2`, respectively, and in quadrangles that include points on both sides of the saturation line, points on the "wrong" side are excluded from the interpolation.
This scheme provides for an efficient and accurate determination of thermophysical properties of CO\ :sub:`2`.

.. figure:: ../figures/figure_eco2n_7.png
    :name: fig:eco2n.7
    :width: 75%

    Schematic of the temperature-pressure tabulation of CO\ :sub:`2` properties. The saturation line (dashed) is given by the diagonals of interpolation rectangles.

An earlier version of ECO2N explicitly associated partial pressures of water (vapor) and CO\ :sub:`2` with the gas phase, and calculated CO\ :sub:`2` dissolution in the aqueous phase from the CO\ :sub:`2` partial pressure, using an extended version of Henry's law (:cite:label:`pruess2002intercomparison`).
The present version uses a methodology for calculating mutual solubilities of water and CO\ :sub:`2` (:cite:label:`spycher2005co2`) that is much more accurate, but has a drawback insofar as no partial pressures are associated with the individual fluid components.
This makes it less straightforward to calculate thermophysical properties of the gas phase in terms of individual fluid components.
We are primarily interested in the behavior of water-salt-CO\ :sub:`2` mixtures at moderate temperatures, :math:`T` < 100˚C, say, where water vapor pressure is a negligibly small fraction of total pressure.
Under these conditions the amount of water present in the CO\ :sub:`2`-rich phase, henceforth referred to as "gas", is small.
Accordingly, we approximate density, viscosity, and specific enthalpy of the gas phase by the corresponding properties of pure CO\ :sub:`2`, without water present.


Density
^^^^^^^

Brine density :math:`\rho_b` for the binary system water-salt is calculated as in :cite:label:`battistelli1997simulator` from the correlations of :cite:label:`haas1976physical` and :cite:label:`andersen1992accurate`.
The calculation starts from aqueous phase density without salinity at vapor-saturated conditions, which is obtained from the correlations given by the International Formulation Committee (:cite:label:`ifc1967formulation`).
Corrections are then applied to account for effects of salinity and pressure.
The density of aqueous phase with dissolved CO\ :sub:`2` is calculated assuming additivity of the volumes of brine and dissolved CO\ :sub:`2`.

.. math::
    :label: eq:eco2n.8

    \frac{1}{\rho_{aq}} = \frac{1 - X_2}{\rho_b} + \frac{X_2}{\rho_{CO_2}}

where :math:`X_2` is the mass fraction of CO\ :sub:`2` in the aqueous phase.
Partial density of dissolved CO\ :sub:`2`, :math:`\rho_{CO_2}`, is calculated as a function of temperature from the correlation for molar volume of dissolved CO\ :sub:`2` at infinite dilution developed by :cite:label:`garcia2001density`.

.. math::
    :label: eq:eco2n.9

    V_{\phi} = a + b T + c T^2 + d T^3

In Eq. :math:numref:`eq:eco2n.9`, molar volume of CO\ :sub:`2` is in units of cm\ :sup:`3` per gram-mole, temperature :math:`T` is in ˚C, and :math:`a`, :math:`b`, :math:`c`, and :math:`d` are fit parameters given in :numref:`tab:eco2n.3`.

.. list-table:: Parameters for molar volume of dissolved CO\ :sub:`2` :math:numref:`eq:eco2n.9`.
    :name: tab:eco2n.3
    :header-rows: 1
    :align: center

    *   - Parameter
        - Value
    *   - a
        - 37.51
    *   - b
        - -9.585 × 10\ :sup:`-2`
    *   - c
        - 8.740 × 10\ :sup:`-4`
    *   - d
        - -5.044 × 10\ :sup:`-7`

Partial density of dissolved CO\ :sub:`2` in units of kg/m\ :sup:`3` is then

.. math::
    :label: eq:eco2n.10

    \rho_{CO_2} = \frac{M_{CO_2}}{V_{\phi}} \times 10^{-3}

where :math:`M_{CO_2}` = 44.0 is the molecular weight of CO\ :sub:`2`.

Dissolved CO\ :sub:`2` amounts at most to a few percent of total aqueous density. Accordingly, dissolved CO\ :sub:`2` is always dilute, regardless of total fluid pressure.
It is then permissible to neglect the pressure dependence of partial density of dissolved CO\ :sub:`2`, and to use the density corresponding to infinite dilution.

As had been mentioned above, the density of the CO\ :sub:`2`-rich (gas) phase is obtained by neglecting effects of water, and approximating the density by that of pure CO\ :sub:`2` at the same temperature and pressure conditions.
Density is obtained through bivariate interpolation from a tabulation of CO\ :sub:`2` densities as function of temperature and pressure, that is based on the correlations developed by :cite:label:`altunin1975thermophysical`.


Viscosity
^^^^^^^^^

Brine viscosity is obtained as in EWASG from a correlation presented by :cite:label:`phillips1981technical`, that reproduces experimental data in the temperature range from 10-350˚C for salinities up to 5 molal and pressures up to 500 bar within 2%.
No allowance is made for dependence of brine viscosity on the concentration of dissolved CO\ :sub:`2`.
Viscosity of the CO\ :sub:`2`-rich phase is approximated as being equal to pure CO\ :sub:`2`, and is obtained through tabular interpolation from the correlations of :cite:label:`altunin1975thermophysical`.


Specific Enthalpy
^^^^^^^^^^^^^^^^^

Specific enthalpy of brine is calculated from the correlations developed by :cite:label:`lorenz2000analytische`, which are valid for all salt concentrations in the temperature range from 25˚C ≤ :math:`T` ≤ 300˚C.
The enthalpy of aqueous phase with dissolved CO\ :sub:`2` is obtained by adding the enthalpies of the CO\ :sub:`2` and brine (pseudo-) components, and accounting for the enthalpy of dissolution of CO\ :sub:`2`.

.. math::
    :label: eq:eco2n.11

    h_{aq} = \left( 1 - X_2 \right) h_b + X_2 h_{CO_2, aq}

:math:`h_{CO_2, aq} = h_{CO_2} + h_{dis}` is the specific enthalpy of aqueous (dissolved) CO\ :sub:`2`, which includes heat of dissolution effects that are a function of temperature and salinity.
For gas-like (low pressure) CO\ :sub:`2`, the specific enthalpy of dissolved CO\ :sub:`2` is

.. math::
    :label: eq:eco2n.12

    h_{CO_2, aq} (T, P, X_s) = h_{CO_2, g} (T, P) + h_{dis, g} (T, X_s)

where :math:`h_{dis, g}` is obtained as in :cite:label:`battistelli1997simulator` from an equation due to :cite:label:`himmelblau1959partial`.
For geologic sequestration we are primarily interested in liquid-like (high-pressure) CO\ :sub:`2`, for which the specific enthalpy of dissolved CO\ :sub:`2` may be written

.. math::
    :label: eq:eco2n.13

    h_{CO_2, aq} (T, P, X_s) = h_{CO_2, l} (T, P) + h_{dis, l} (T, X_s)

Here :math:`h_{dis, l}` is the specific heat of dissolution for liquid-like CO\ :sub:`2`.
Along the CO\ :sub:`2` saturation line, liquid and gaseous CO\ :sub:`2` phases may co-exist, and the expressions Eqs. :math:numref:`eq:eco2n.12` and :math:numref:`eq:eco2n.13` must be equal there.
We obtain

.. math::
    :label: eq:eco2n.14

    h_{dis, l} (T, X_s) = h_{dis, g} (T, X_s) + h_{CO_2, gl} (T)

where :math:`h_{CO_2, gl} (T) = h_{CO_2, g} (T, P_s) - h_{CO_2, l} (T, P_s)` is the specific enthalpy of vaporization of CO\ :sub:`2`, and :math:`P_s = P_s (T)` is the saturated vapor pressure of CO\ :sub:`2` at temperature :math:`T`.
Depending upon whether CO\ :sub:`2` is in gas or liquid conditions, we use Eq. :math:numref:`eq:eco2n.12` or :math:numref:`eq:eco2n.13` in Eq. :math:numref:`eq:eco2n.11` to calculate the specific enthalpy of dissolved CO\ :sub:`2`.
At the temperatures of interest here, :math:`h_{dis, g}` is a negative quantity, so that dissolution of low-pressure CO\ :sub:`2` is accompanied by an increase in temperature.
:math:`h_{CO_2, gl}` is a positive quantity, which will reduce or cancel out the heat-of-dissolution effects.
This indicates that dissolution of liquid CO\ :sub:`2` will produce less temperature increase than dissolution of gaseous CO\ :sub:`2`, and may even cause a temperature decline if :math:`h_{CO_2, gl}` is sufficiently large.

Application of Eq. :math:numref:`eq:eco2n.11` is straightforward for single-phase gas and two-phase conditions, where :math:`h_{CO_2}` is obtained as a function of temperature and pressure through bivariate interpolation from a tabulation of Altunin's correlation (:cite:label:`altunin1975thermophysical`).
A complication arises in evaluating :math:`h_{CO_2}` for single-phase aqueous conditions.
We make the assumption that :math:`h_{CO_2} (P, X_s, X_2, T)` for single-phase liquid is identical to the value in a two-phase system with the same composition of the aqueous phase.
To determine :math:`h_{CO_2}`, it is then necessary to invert the :cite:label:`spycher2005co2` phase partitioning relation :math:`X_2 = X_2 (P, T, X_s)`, in order to obtain the pressure :math:`P` in a two-phase aqueous-gas system that would correspond to a dissolved CO\ :sub:`2` mass fraction :math:`X_2` in the aqueous phase, :math:`P = P(X_2, X_s, T)`.
The inversion is accomplished by Newtonian iteration, using a starting guess :math:`P_0` for :math:`P` that is obtained from Henry's law.
Specific enthalpy of gaseous CO\ :sub:`2` in the two-phase system is then calculated as :math:`h_{CO_2} = h_{CO_2} (T, P)`, and specific enthalpy of dissolved CO\ :sub:`2` is :math:`h_{CO_2} + h_{dis}`.


Description
-----------

Initialization Choices
**********************

Flow problems in TOUGH2/ECO2N will generally be initialized with the primary
thermodynamic variables as used in the code, but some additional choices are available for the convenience of users.
The internally used variables are (:math:`P`, :math:`X_{sm}`, :math:`X_3`, :math:`T`) for grid blocks in single-phase (liquid or gas) conditions and (:math:`P`, :math:`X_{sm}`, :math:`S_g` + 10, :math:`T`) for two-phase (liquid and gas) grid blocks (see :numref:`tab:eco2n.1`).
Here :math:`X_3` is the mass fraction of CO\ :sub:`2` in the fluid.
As had been discussed above, for conditions of interest to geologic sequestration of CO\ :sub:`2`, :math:`X_3` is restricted to small values 0 ≤ :math:`X_3` ≤ :math:`X_{2, eq}` (a few percent) for single-phase liquid conditions, or to values near 1 (:math:`Y_{2, eq}` ≤ :math:`X_3` ≤ 1, with :math:`Y_{2, eq}` > 0.99 typically) for single-phase gas (:numref:`fig:eco2n.6`).
Intermediate values :math:`X_{2, eq}` < :math:`X_3` < :math:`Y_{2, eq}` correspond to two-phase conditions, and thus should be initialized by specifying :math:`S_g` + 10 as third primary variable.
As a convenience to users, ECO2N allows initial conditions to be specified in the full range 0 ≤ :math:`X_3` ≤ 1.
During the initialization phase of a simulation, a check is made whether :math:`X_3` is in fact within the range of mass fractions that correspond to single-phase (liquid or gas) conditions.
If this is found not to be the case, the conditions are recognized as being two-phase, and the corresponding gas saturation is calculated from the phase equilibrium constraint.

.. math::
    :label: eq:eco2n.15

    X_3 \left( S_l \rho_l + S_g \rho_g \right) = S_l \rho_l X_{2, eq} + S_g \rho_g Y_{2, eq}

Using :math:`S_l = 1 - S_g - S_s`, with Ss the "solid saturation" (fraction of pore space occupied by solid salt), we obtain

.. math::
    :label: eq:eco2n.16

    S_g = A \left( 1 - S_s \right)

and the third primary variable is reset internally to :math:`X_3` = :math:`S_g` + 10.
Here the parameter :math:`A` is given by

.. math::
    :label: eq:eco2n.17

    A = \frac{\left( X_3 - X_{2, eq} \right) \rho_l}{\left( X_3 - X_{2, eq} \right) \rho_l + \left( Y_{2, eq} - X_3 \right) \rho_g}

Users may think of specifying single-phase liquid (aqueous) conditions by setting :math:`X_3` = 10 (corresponding to :math:`S_g` = 0), and single-phase gas conditions by setting :math:`X_3` = 11 - :math:`S_s` (corresponding to :math:`Sl` = 0).
Strictly speaking this is not permissible, because two-phase initialization requires that both :math:`S_g` > 0 and :math:`S_l` > 0.
Single-phase states should instead be initialized by specifying primary
variable :math:`X_3` as CO\ :sub:`2` mass fraction.
However, as a user convenience, ECO2N accepts initialization of single-phase liquid conditions by specifying :math:`X_3` = 10 (:math:`S_g` = 0).
Such specification will be converted internally to two-phase in the initialization phase by adding a small number (10\ :sup:`-11`) to the third
primary variable, changing conditions to two-phase with a small gas saturation :math:`S_g` = 10\ :sup:`-11`.

Salt concentration or saturation of solid salt, if present, is characterized in ECO2N by means of the second primary variable :math:`X_{sm}`.
When no solid phase is present, :math:`X_{sm}` denotes :math:`X_s`, the mass fraction of NaCl referred to the two-component system water-NaCl.
This is restricted to the range 0 ≤ :math:`X_{sm}` ≤ :math:`XEQ`, where :math:`XEQ = XEQ(T)` is the solubility of salt.
For :math:`X_{sm}` > 10 this variable means :math:`S_s` + 10, solid saturation plus 10.
Users also have the option to specify salt concentration by means of molality :math:`m` by assigning :math:`X_{sm} = -m`.
Such specification will in the initialization phase be internally converted to :math:`X_s` by using Eq. :math:numref:`eq:eco2n.1`.
When salt concentration (as a fraction of total H\ :sub:`2`\O + NaCl mass) exceeds :math:`XEQ`, this corresponds to conditions in which solid salt will be present in addition to dissolved salt in the aqueous phase.
Such states should be initialized with a second primary variable :math:`X_{sm}` = :math:`S_s` + 10.
However, ECO2N accepts initialization with :math:`X_{sm}` > :math:`XEQ`, recognizes this as corresponding to presence of solid salt, and converts the second primary variable internally to the appropriate solid saturation that will result in total salt mass fraction in the binary system water-salt being equal to :math:`X_{sm}`.
The conversion starts from the following equation.

.. math::
    :label: eq:eco2n.18

    X_{sm} = \frac{XEQ \times S_l \rho_l \left( 1 - X_2 \right) + S_s \rho_s}{S_l \rho_l \left( 1 - X_2 \right) + S_s \rho_s}

where the numerator gives the total salt mass per unit volume, in liquid and solid phases, while the denominator gives the total mass of salt plus water.
Substituting :math:`S_l = 1 - S_g - S_s`, this can be solved for :math:`S_s` to yield

.. math::
    :label: eq:eco2n.19

    S_s = \frac{B \left( 1 - S_g \right)}{1 + B}

where the parameter :math:`B` is given by

.. math::
    :label: eq:eco2n.20

    B = \frac{\left( X_{sm} - XEQ \right) \rho_l \left( 1 - X_2 \right)}{\rho_s \left( 1 - X_{sm} \right)}

The most general conditions arise when both the second and third primary variables are initialized as mass fractions, nominally corresponding to single-phase fluid conditions with no solid phase present, but both mass fractions being in the range corresponding to two-phase fluid conditions
with precipitated salt.
Under these conditions, Eqs. :math:numref:`eq:eco2n.16` and :math:numref:`eq:eco2n.19` are solved simultaneously in ECO2N for :math:`S_s` and :math:`S_g`, yielding

.. math::
    :label: eq:eco2n.21

    S_g = \frac{A}{1 + B - A \times B}

.. math::
    :label: eq:eco2n.22

    S_s = \frac{B \times \left( 1 - A \right)}{1 + B - A \times B}

Then both second and third primary variables are converted to phase saturations, :math:`S_s` + 10 and :math:`S_g` + 10, respectively.


Permeability Change from Precipitation and Dissolution of Salt
**************************************************************

ECO2N offers several choices for the functional dependence of relative change in permeability, :math:`\frac{k}{k_0}`, on relative change in active flow porosity.

.. math::
    :label: eq:eco2n.23

    \frac{k}{k_0} = f \left( \frac{\phi_f}{\phi_0} \right) \equiv f \left( 1 - S_s \right)

The simplest model that can capture the converging-diverging nature of natural pore channels consists of alternating segments of capillary tubes with larger and smaller radii, respectively; see :numref:`fig:eco2n.8`.
While in straight capillary tube models permeability remains finite as long as porosity is non-zero, in models of tubes with different radii in series, permeability is reduced to zero at a finite porosity.

.. subfigure:: AB
    :name: fig:eco2n.8
    :layout-sm: A|B
    :subcaptions: above
    :gap: 32px

    .. image:: ../figures/pore_conceptual_model.png
        :alt: Conceptual model

    .. image:: ../figures/pore_tubes_in_series.png
        :alt: Tubes-in-series

    Model for converging-diverging pore channels.

From the tubes-in-series model shown in :numref:`fig:eco2n.8`, the following relationship can be derived (:cite:label:`verma1988thermohydrological`)

.. math::
    :label: eq:eco2n.24

    \frac{k}{k_0} = \theta^2 \frac{1 - \Gamma + \frac{\Gamma}{\omega^2}}{1 - \Gamma + \Gamma \left( \frac{\theta}{\theta + \omega - 1} \right)^2}

Here

.. math::
    :label: eq:eco2n.25

    \theta = \frac{1 - S_s - \phi_r}{1 - \phi_r}

depends on the fraction :math:`1 - S_s` of original pore space that remains available to fluids, and on a parameter :math:`\phi_r`, which denotes the fraction of original porosity at which permeability is reduced to zero.
:math:`\Gamma` is the fractional length of the pore bodies, and the parameter :math:`\omega` is given by

.. math::
    :label: eq:eco2n.26

    \omega = 1 + \frac{\frac{1}{\Gamma}}{\frac{1}{\phi_r} - 1}

Therefore, Eq. :math:numref:`eq:eco2n.24` has only two independent geometric parameters that need to be specified, :math:`\phi_r` and :math:`\Gamma`.
As an example, :numref:`fig:eco2n.9` shows the permeability reduction factor from Eq. :math:numref:`eq:eco2n.24`, plotted against :math:`\frac{\phi}{\phi_0} \equiv \left( 1 - S_s \right)`, for parameters of :math:`\phi_r` = :math:`\Gamma` = 0.8.

.. figure:: ../figures/porosity_permeability.png
    :name: fig:eco2n.9
    :width: 75%
    
    Porosity-permeability relationship for tubes-in-series model, after :cite:label:`verma1988thermohydrological`.

For parallel-plate fracture segments of different aperture in series, a relationship similar to Eq. :math:numref:`eq:eco2n.24` is obtained, the only difference being that the exponent 2 is replaced everywhere by 3 (:cite:label:`verma1988thermohydrological`).
If only straight capillary tubes of uniform radius are considered, we have :math:`\phi_r` = 0, :math:`\Gamma` = 0, and Eq. :math:numref:`eq:ewasg.2` simplifies to

.. math::
    :label: eq:eco2n.27

    \frac{k}{k_0} = \left( 1 - S_s \right)^2


Selections
----------

Various options for ECO2N can be selected through parameter specifications in data block **SELEC**.
Default choices corresponding to various selection parameters set equal to zero provide the most comprehensive thermophysical property model.
Certain functional dependencies can be turned off or replaced by simpler and less accurate models, see below.
These options are offered to enable users to identify the role of different effects in a flow problem, and to facilitate comparison with other simulation programs that may not include full dependencies of thermophysical properties.

.. list-table:: Record **SELEC.1**.
    :name: tab:eco2n.selec.1
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``IE(1)``
        - I5
        -  set equal to 1, to read one additional data record (a larger value with more data records is acceptable, but only one additional record will be used by ECO2N).
    *   - ``IE(11)``
        - I5
        - | selects dependence of permeability on the fraction :math:`\frac{\phi_f}{\phi_0} = \left( 1 - S_s \right)` of original pore space that remains available to fluids:
          | 0: permeability does not vary with :math:`\phi_f`.
          | 1: :math:`\frac{k}{k_0} = \left( 1 - S_s \right)^{\gamma}`, with :math:`\gamma` = ``FE(1)``.
          | 2: fractures in series, i.e., Eq. :math:numref:`eq:eco2n.24` with exponent 2 everywhere replaced by 3.
          | 3: tubes-in-series, i.e., Eq. :math:numref:`eq:eco2n.24`.
    *   - ``IE(12)``
        - I5
        - | allows choice of model for water solubility in CO\ :sub:`2`:
          | 0: after Spycher and Pruess (2005).
          | 1: evaporation model; i.e., water density in the CO\ :sub:`2`-rich phase is calculated as density of saturated water vapor at prevailing temperature and salinity.
    *   - ``IE(13)``
        - I5
        - |  allows choice of dependence of brine density on dissolved CO\ :sub:`2`:
          | 0: brine density varies with dissolved CO\ :sub:`2` concentration, according to García's (2001) correlation for temperature dependence of molar volume of dissolved CO\ :sub:`2`.
          | 1: brine density is independent of CO\ :sub:`2` concentration.
    *   - ``IE(14)``
        - I5
        - | allows choice of treatment of thermophysical properties as a function of salinity:
          | 0: full dependence.
          | 1: no salinity dependence of thermophysical properties (except for brine enthalpy; salt solubility constraints are maintained).
    *   - ``IE(15)``
        - I5
        - | allows choice of correlation for brine enthalpy at saturated vapor pressure:
          | 0: after Lorenz et al. (2000).
          | 1: after Michaelides (1981).
          | 2: after Miller (1978).

.. list-table:: Record **SELEC.2**.
    :name: tab:eco2n.selec.2
    :widths: 1 1 6
    :header-rows: 1
    :align: center

    *   - Parameter
        - Format
        - Description
    *   - ``FE(1)``
        - E10.4
        - parameter :math:`\gamma` (for ``IE(11)`` = 1); parameter :math:`\phi_r` (for ``IE(11)`` = 2, 3).
    *   - ``FE(2)``
        - E10.4
        - parameter :math:`\Gamma` (for ``IE(11)`` = 2, 3).
