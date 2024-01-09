.. _eos4:

EOS4
====

This module is an adaptation of the :ref:`eos3` module, and implements vapor pressure lowering effects.
Vapor pressure :math:`P_v` is expressed by Kelvin's equation,
Eq. :math:numref:`eq:eos4.1` (:cite:label:`edlefsen1943thermodynamics`); it is a function not only of temperature, but depends also on capillary pressure, which in turn is a function of saturation.

.. math::
    :label: eq:eos4.1

    P_v (T, S_l) = f_{VPL} (T, S_l) P_{sat} (T)

where

.. math::
    :label: eq:eos4.2

    f_{VPL} = \exp \left( \frac{M_w P_{cl}(S_l)}{\rho_l R \left( T + 273.15 \right)} \right)

is the vapor pressure lowering factor.
:math:`P_{sat}` is the saturated vapor pressure of bulk aqueous phase, :math:`T` is temperature, :math:`S_l` is the liquid (water) saturation, :math:`P_{cl}` is the capillary pressure (i.e., the difference between aqueous and gas phase pressures), :math:`M_w` is the molecular weight of water, :math:`rho_l` is the liquid density, and :math:`R` is the universal gas constant.


Specifications
--------------

A summary of EOS4 specifications and parameters is given in :numref:`tab:eos4`.
The default parameter settings are (``NK``, ``NEQ``, ``NPH``, ``NB``) = (2, 3, 2, 6).
The option for single-component mode of water only, no air (``NK`` = 1) is available for nonisothermal conditions (``NEQ`` = 2).
The specification of thermophysical properties in this EOS differs from :ref:`eos3` in that provision is made for vapor pressure lowering effects.
The primary variables are (:math:`P`, :math:`T`, :math:`P_a`) for single-phase conditions and (:math:`P_g`, :math:`S_g`, :math:`P_a`) for two-phase conditions, where :math:`P_a` is the partial pressure of air.
Note that in two-phase conditions temperature is not among the primary variables.
It is implicitly determined from the relationship :math:`P_g - P_a = P_v`, with :math:`P_v = P_v(T, S_l)` as given in Eq. :math:numref:`eq:eos4.1`.

It would be possible to use other sets of primary variables; in particular, temperature could be used also in two-phase conditions.
Our test calculations for a number of examples indicated, however, that the choice (:math:`P_g`, :math:`S_g`, :math:`P_a`) usually leads to better convergence behavior than the choice (:math:`P_g`, :math:`S_g`, :math:`T`).
The reason for the numerically inferior behavior of the latter set is in the air mass balance.
With the variables (:math:`P_g`, :math:`S_g`, :math:`T`), the amount of air present in a grid block becomes controlled by the difference between total gas pressure :math:`P_g` and effective vapor pressure :math:`P_v = P_{sat}(T) f_{VPL}(T, S_l)` (Eq. :math:numref:`eq:eos4.1`), which can be subject to very severe numerical cancellation.
From the applications viewpoint, however, initialization of a flow problem with the set (:math:`P_g`, :math:`S_g`, :math:`T`) may be much more physical and convenient.
EOS4 allows the initialization of two-phase points as (:math:`P_g`, :math:`S_g`, :math:`T`); this capability can be selected by specifying ``MOP(19)`` = 1.
When using ``MOP(19)`` = 1, the second primary variable upon initialization can also be relative humidity :math:`RH`, expressed as a fraction (0 < :math:`RH` ≤ 1); this choice is made by entering the second primary variable as a negative number, which will serve as a flag to indicate that it means (negative of) relative humidity, and will be internally converted to saturation in the initialization phase.
The conversion consists of iteratively solving Kelvin's equation for given :math:`RH = f_{VPL}(T, S_l)` for :math:`S_l`.
Users need to beware that relative humidity specifications must be within the range that is feasible for the capillary pressure functions used.
If maximum capillary pressures are not strong enough to accommodate a chosen value of :math:`RH`, a diagnostic will be printed and execution will terminate.

.. list-table:: Summary of EOS4.
    :name: tab:eos4
    :widths: 1 3
    :align: center

    *   - Components
        - | #1: water
          | #2: air
    *   - Parameter choices
        - | (``NK``, ``NEQ``, ``NPH``, ``NB``) =
          | (2, 3, 2, 6) water and air, nonisothermal (default)
          | (1, 2, 2, 6) water only (no air), nonisothermal
          | ``MOP(20)`` = 1 optionally suppresses vapor pressure lowering effects
          | Molecular diffusion can be modeled by setting ``NB`` = 8
    *   - Primary variables*†
        - | Single-phase conditions:
          | (:math:`P_g`, :math:`S_g`, :math:`P_a`): (pressure, temperature, air partial pressure)
          | Two-phase conditions:
          | :math:`P_g`, :math:`S_g`, :math:`P_a`: (gas phase pressure, gas saturation, air partial pressure)

.. note::

    | \* By setting ``MOP(19)`` = 1, initialization of two-phase conditions can be made with (:math:`P_g`, :math:`S_g`, :math:`T`), or with (:math:`P_g`, :math:`-RH`, :math:`T`), where :math:`RH` is relative humidity (0 < :math:`RH` ≤ 1).
    | † By setting ``MOP(19)`` = 2, initialization can be made with EOS3-style variables (:math:`P`, :math:`X`, :math:`T`) for single-phase (:math:`X` is air mass fraction), (:math:`P_g`, :math:`S_g` + 10, :math:`T`) for two-phase.

As a further convenience to users, the choice ``MOP(19)`` = 2 allows EOS4 to be initialized with :ref:`eos3` variables of (:math:`P`, :math:`X`, :math:`T`) for single-phase, (:math:`P_g`, :math:`S_g` + 10, :math:`T`) for two-phase.
This way continuation runs with EOS4 can be made from :ref:`eos3`-generated conditions.
Note that, when using ``MOP(19)`` ≠ 0 options, data block or file INCON must terminate on a blank record.
If ``+++`` is encountered in *INCON*, it is assumed that primary variables are provided in agreement with internal usage; ``MOP(19)`` is then reset to zero and an informative message is printed.

Vapor pressure lowering effects raise new issues because they make it possible for a liquid phase to exist under conditions where vapor partial pressure and gas phase total pressure are less than the saturation pressure.
What is the appropriate pressure at which liquid phase density, enthalpy and viscosity are to be evaluated?
We believe that a physically plausible choice is to take :math:`P_1 = \max(P_g, P_{sat})`, and this has been implemented in EOS4.
The implementation faces a difficulty, however, because temperature is not among the primary variables in two-phase conditions, so that :math:`P_{sat}` is only implicitly known; moreover, vapor pressure lowering effects are functionally dependent on liquid phase density, which is also a function of temperature.
This leads to a potentially unstable situation with regard to the choice of liquid phase pressure under conditions where :math:`P_g \approx P_{sat}`, which happens to be a common occurrence in boiling regions. In order to avoid this problem we evaluate liquid water density in the Kelvin equation for vapor pressure lowering (Eq. :math:numref:`eq:eos4.1`) always at :math:`P_l = P_{sat}`, which will be an excellent approximation due to the small compressibility of liquid water.
In all accumulation and flow terms the density of liquid water is evaluated at :math:`P_l = \max(P_g, P_{sat})`.
Vapor pressure lowering can be optionally suppressed by setting ``MOP(20)`` = 1.
