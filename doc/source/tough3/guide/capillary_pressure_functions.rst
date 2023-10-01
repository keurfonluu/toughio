.. _capillary_pressure_functions:

Capillary Pressure Functions
============================

TOUGH3 provides several capillary pressure functions for two-phase or three-phase flow problems.
The original TOUGH2 two-phase functions have been retained (from ``ICP`` = 1 to ``ICP`` = 8).
The modified Brooks-Corey and van Genuchten models and two versions of the hysteresis model are implemented (``ICP`` = 10, 11, 12, and 13).
The three-phase functions from TMVOC and ECO2M start at IRP = 31.
If one of the two-phase functions is chosen, the gas-NAPL (for TMVOC) or gaseous CO\ :sub:`2`-liquid CO\ :sub:`2` (for ECO2M) capillary pressure will be assumed to be zero.
The notation used below is:

- :math:`P_{cgn} = P_n - P_g =` gas-NAPL capillary pressure for TMVOC, which is equivalent to :math:`P_{cgl} = P_l - P_g =` gaseous CO\ :sub:`2`-liquid CO\ :sub:`2` capillary pressure for ECO2M
- :math:`P_{cgl} = P_l - P_g =` gas-aqueous capillary pressure for TMVOC, which is equivalent to :math:`P_{cga} = P_a - P_g =` gaseous CO\ :sub:`2`-aqueous capillary pressure for ECO2M
- :math:`P_{cnl} = P_{cgl} - P_{cgn}` for TMVOC, and similarly :math:`P_{cla} = P_{cga} - P_{cgl}` for ECO2M
- :math:`S_l`, :math:`S_g`, and :math:`S_n` are the saturations of aqueous, gas (or gaseous CO\ :sub:`2`) and NAPL (or liquid CO\ :sub:`2`) phases, respectively


Linear Function (ICP=1)
-----------------------

.. math::

    P_{cap} = 
        \begin{cases}
            -CP(1) & \text{for $S_l \le CP(2$} \\
            0 & \text{for $S_l \ge CP(3)$} \\
            -CP(1) \frac{CP(3) - S_l}{CP(3) - CP(2)} & \text{for $CP(2) \lt S_l \lt CP(3)$} \\
        \end{cases}

Restrictions: :math:`CP(3) \gt CP(2)`

If :math:`CP(4) \ne 0`:

.. math::

    P_{cgn} = P_{cap} (= P_{cgl})

.. math::

    P_{cap} (P_{cgl}) = 0


Function of Pickens et al. (ICP=2)
----------------------------------

After :cite:label:`pickens1979finite`.

.. math::

    P_{cap} = -P_0 \left( \log \left( \frac{A}{B} \left(\ 1 + \sqrt{1 - \frac{B^2}{A^2}} \right) \right) \right)^{\frac{1}{x}}

with

.. math::

    A = \frac{\left( 1 + \frac{S_l}{S_{l0}} \right) \left( S_{l0} - S_{lr} \right)}{S_{l0} + S_{lr}}

.. math::

    B = 1 - \frac{S_l}{S_{l0}}

Parameters:

- :math:`CP(1) = P_0`
- :math:`CP(2) = S_{lr}`
- :math:`CP(3) = S_{l0}`
- :math:`CP(4) = x`

Restrictions:

- :math:`0 \lt CP(2) \lt 1 \le CP(3)`
- :math:`CP(4) \ne 0`


TRUST Capillary Pressure (ICP=3)
--------------------------------

After :cite:label:`narasimhan1978numerical`.

.. math::

    P_{cap} =
        \begin{cases}
            -P_e - P_0 \left( \frac{1 - S_l}{S_l - S_{lr}} \right)^{\frac{1}{\eta}} & \text{for $S_l \gt S_{lr}$} \\
            -P_{max} & \text{for $S_l \lt S_{lr}$} \\
        \end{cases}

Parameters:

- :math:`CP(1) = P_0`
- :math:`CP(2) = S_{lr}`
- :math:`CP(3) = \eta`
- :math:`CP(4) = P_e`
- :math:`CP(5) = P_{max}`

Restrictions:

- :math:`CP(2) \ge 0`
- :math:`CP(3) \ne 0`


Milly's Functions (ICP=4)
-------------------------

.. math::

    P_{cap} = -98.783 \times 10^A

with

.. math::
    
    A = 2.26 \left( \frac{0.371}{S_l - S_{lr}} - 1 \right)^{\frac{1}{4}}

Parameters:

- :math:`CP(1) = S_{lr}`

Restrictions:

- :math:`CP(1) \ge 0`


Leverett's Function (ICP=6)
---------------------------

After :cite:label:`leverett1941capillary` and :cite:label:`udell1985heat`.

.. math::

    P_{cap} = -P_0 \sigma (T) f (S_l)

with

.. math::

    \sigma(T) = \text{surface tension of water (supplied internally in TOUGH3)}

.. math::

    S^\ast = \frac{S_l - S_{lr}}{1 - S_{lr}}

Parameters:

- :math:`CP(1) = P_0`
- :math:`CP(2) = S_{lr}`

Restrictions:

- :math:`0 \le CP(2) \lt 1`

If :math:`CP(3) \ne 0`

.. math::

    P_{cgn} = P_{cap} (= P_{cgl})

.. math::

    P_{cap} (P_{cgl}) = 0


van Genuchten Function (ICP=7)
------------------------------

.. math::

    P_{cap} = -P_0 \left( \left( S^\ast \right)^{-\frac{1}{\lambda}} - 1 \right)^{1 - \lambda}

subject to the restriction

.. math::

    -P_{max} \le P_{cap} \le 0

Here,

.. math::

    S^\ast = \frac{S_l - S_{lr}}{S_{ls} - S_{lr}}

Parameters:

- :math:`CP(1) = \lambda = 1 - \frac{1}{n}`
- :math:`CP(2) = S_{lr}` (should be chosen smaller than the corresponding parameter in the relative permeability function)
- :math:`CP(3) = \frac{1}{P_0} = \frac{\alpha}{\rho_w g}` (proportional to :math:`\sqrt{k}`)
- :math:`CP(4) = P_{max}`
- :math:`CP(5) = S_{ls}`

.. note::

    Parameter :math:`\lambda` is :math:`m` in van Genuchten's notation, with :math:`m = 1 - \frac{1}{n}`; parameter :math:`n` is often written as :math:`\beta`.
    
    In :cite:label:`van1980closed`'s derivation, the parameter :math:`S_{lr}` for irreducible water saturation is the same in the relative permeability and capillary pressure functions.
    As a consequence, for :math:`S_l \rightarrow S_{lr}`, we have :math:`k_{rl} \rightarrow 0` and :math:`P_{cap} \rightarrow -\infty`, which is unphysical because it implies that the radii of capillary menisci go to zero as liquid phase is becoming immobile (discontinuous).
    In reality, no special capillary pressure effects are expected when liquid phase becomes discontinuous.
    Accordingly, we recommend to always choose a smaller :math:`S_{lr}` for the capillary pressure as compared to the relative permeability function.


No Capillary Pressure (ICP=8)
-----------------------------

For all saturations:

.. math::

    P_{cap} \equiv 0

No parameters.


Modified Brooks-Corey Model (ICP=10)
------------------------------------

A modified version of the Brooks-Corey model (:cite:label:`brooks1965hydraulic`) has been implemented.
In order to prevent the capillary pressure from decreasing towards negative infinity as the effective saturation approaches zero, a linear function is used for saturations :math:`S_l` below a certain value :math:`\left( S_{lrc} + \varepsilon \right)`, where :math:`\varepsilon` is a small number.
The slope of the linear extrapolation is identical with the slope of the capillary pressure curve at :math:`S_l = S_{lrc} + \varepsilon`.
Alternatively, the capillary pressure is prevented from becoming more negative than :math:`-P_{max}`.
The modified Brooks-Corey model is invoked by setting both ``IRP`` and ``ICP`` to 10.

.. math::

    P_{cap} = 
        \begin{cases}
            -P_e \left( S_{ec} \right)^{-\frac{1}{\lambda}} & \text{for $S_l \gt S_{lrc} + \varepsilon$} \\
            -P_e \left( \frac{\varepsilon}{1 - S_{lrc}} \right)^{-\frac{1}{\lambda}} + \frac{P_e}{\lambda} \frac{1}{1 - S_{lrc}} \left( \frac{\varepsilon}{1 - S_{lrc}} \right)^{-\frac{1 + \lambda}{\lambda}} \left( S_l - S_{lrc} - \varepsilon \right) & \text{for $S_l \lt S_{lrc} + \varepsilon$} \\
        \end{cases}

where

.. math::

    P_{cap} \le -P_{max}

.. math::

    S_{ec} = \frac{S_l - S_{lrc}}{1 - S_{lrc}}

Parameters:

- :math:`CP(1) = \lambda`, pore size distribution index
- :math:`CP(2) = P_e`, gas entry pressure (Pa)
    
    - If ``USERX(2, N)`` is positive, :math:`P_e = USERX(2, N)`
    - If ``USERX(2, N)`` is negative, :math:`P_e = -USERX(2, N) \cdot CP(2)`
    - | If :math:`CP(2)` is negative and ``USERX(1, N)`` is non-zero, apply Leverett's rule:\
      | :math:`P_e = -CP(2) \sqrt{\frac{USERX(1, N)}{PER(NMAT)}}`

- :math:`CP(3) = P_{max}` or :math:`\varepsilon`

    - If :math:`CP(3) = 0`, :math:`P_{max} = 10^{50}`, :math:`\varepsilon = -1`
    - If :math:`0 \lt CP(3) \lt 1`, use linear model for :math:`S_l \lt S_{lrc} + \varepsilon`
    - If :math:`CP(3) \ge 1`, :math:`P_{max} = CP(3)`, :math:`\varepsilon = -1`
  
- :math:`CP(6) = S_{lrc}`


Modified van Genuchten Model
----------------------------

The van Genuchten model (:cite:label:`luckner1989consistent`) has been modified to prevent the capillary pressure from decreasing towards negative infinity as the effective saturation approaches zero.
The approach is identical to that in ``ICP`` = 10, except that two extensions (linear and log-linear) are available.
The modified van Genuchten model is invoked by setting both ``IRP`` and ``ICP`` to 11.

.. math::

    P_{cap} = 
        \begin{cases}
            -\frac{1}{\alpha} \left( \left( S_{ec} \right)^{\frac{\gamma - 1}{m}} - 1 \right)^{\frac{1}{n}} & \text{for $S_l \ge S_{lrc} + \varepsilon$} \\
            -\frac{1}{\alpha} \left( S_{ec\ast}^{\frac{\gamma - 1}{m}} - 1 \right)^{\frac{1}{n}} - \beta \left( S_l - S_{lrc} - \varepsilon \right) & \text{for $S_l \lt S_{lrc} + \varepsilon$} \\
        \end{cases}

with linear extension: :math:`\beta = -\frac{1 - \gamma}{\alpha n m} \frac{1}{1 - S_{lrc}} \left( S_{ec\ast}^{\frac{\gamma - 1}{m}} - 1 \right)^{\frac{1}{n} - 1} S_{ec\ast}^{\frac{\gamma - 1 - m}{m}}`

.. math::

    P_{cap} = -\frac{1}{\alpha} \left( S_{ec\ast}^{\frac{\gamma - 1}{m}} - 1 \right)^{\frac{1}{n}} \cdot 10^{\beta \left( S_l - S_{lrc} - \varepsilon \right)} \quad \text{for $S_l \lt S_{lrc} + \varepsilon$}

with log-linear extension: :math:`\beta = -\log_{10} (e) \left( \frac{1 - m}{m} \frac{\gamma - 1}{\varepsilon} \frac{1}{S_{ec\ast}^{\frac{1 - \gamma}{m}} - 1} \right)`

.. math::

    P_{cap} \ge -P_{max}

where

.. math::

    S_{ec} = \frac{S_l - S_{lrc}}{1 - S_{lrc}}

.. math::

    S_{ec\ast} = \frac{\varepsilon}{1 - S_{lrc}}

Parameters:

- :math:`CP(1) = n`, parameter related to pore size distribution index (see also :math:`CP(4)`)
- :math:`CP(2) = \frac{1}{\alpha}`, parameter related to gas entry pressure (Pa)

    - If ``USERX(4, N)`` is positive, :math:`\frac{1}{\alpha_i} = USERX(4, N)`
    - If ``USERX(4, N)`` is negative, :math:`\frac{1}{\alpha_i} = USERX(4, N) \cdot CP(2)`
    - | If :math:`CP(2)` is negative, apply Leverett scaling rule:
      | :math:`\frac{1}{\alpha_i} = \lvert CP(2) \rvert \sqrt{\frac{k_i}{PER(NMAT)}}`
      | where

      .. math::

        k_i = 
            \begin{cases}
                USERX(1, N) & \text{for $USERX(1, N) \gt 0$} \\
                USERX(1, N) \cdot PER(NMAT) & \text{for $USERX(1, N) \lt 0$} \\
            \end{cases}

- :math:`CP(3) = P_{max}` or :math:`\varepsilon`

    - If :math:`CP(3) = 0`, :math:`P_{max} = 10^{50}`, :math:`\varepsilon = -1`
    - If :math:`0 \lt CP(3) \lt 1`, :math:`\varepsilon = CP(3)` and use linear extension
    - If :math:`CP(3) \ge 1`, :math:`P_{max} = CP(3)`, :math:`\varepsilon = -1`
    - If :math:`-1 \lt CP(3) \lt 0`, :math:`\varepsilon = \lvert CP(3) \rvert` and use log-linear extension

- :math:`CP(4) = m`, if zero then :math:`m = 1 - \frac{1}{CP(1)}`, else :math:`m = CP(4)` and :math:`n = \frac{1}{1 - m}`
- :math:`CP(5) = T_{ref}`, if negative, :math:`\lvert CP(5) \rvert` is reference temperature to account for temperature dependence of capillary pressure due to changes in surface tension
- :math:`CP(6) = \gamma`
- :math:`CP(7) = S_{lrc}`, if zero, then :math:`S_{lrc} = RP(1) = S_{lrk}`


Regular Hysteresis (ICP=12)
---------------------------

The hysteretic form of the van Genuchten model (:cite:label:`parker1987model, lenhard1987model`) has been implemented.
Details of the implementation are described in :cite:label:`doughty2013user`.
The hysteretic model is invoked by setting both ``IRP`` and ``ICP`` to 12.

.. math::

    P_{cap} = -P_0^p \left( \left( \frac{S_l - S_{lmin} }{1 - S_{gr}^{\Delta} - S_{lmin}} \right)^{-\frac{1}{m^p}} - 1 \right)^{1 - m^p}

where

.. math::

    S_{gr}^{\Delta} = \frac{1}{\frac{1}{1 - S_l^{\Delta}} + \frac{1}{S_{grmax}} - \frac{1}{1 - S_{lr}}}

Parameters:

- :math:`CP(1) = m^d`, van Genuchten :math:`m` for drainage branch :math:`P_{cap}^d (S_l)`
- :math:`CP(2) = S_{lmin}`, saturation at which original van Genuchten :math:`P_{cap}` goes to infinity. Must have :math:`S_{lmin} \lt S_{lr}`, where :math:`S_{lr}` is the relative permeability parameter :math:`RP(2)`
- :math:`CP(3) = P_0^d`, capillary strength parameter for drainage branch :math:`P_{cap}^d (S_l)` (Pa)
- :math:`CP(4) = P_{max}`, maximum capillary pressure (Pa) obtained using original van Genuchten :math:`P_{cap}`. Inverting the original van Genuchten function for :math:`P_{max}` determines :math:`S_m`, the transition point between the original van Genuchten function and an extension that stays finite as :math:`S_l` goes to zero. For functional form of extension, see description of :math:`CP(13)` below.
- :math:`CP(5) =` scale factor for pressures for unit conversion (1 for pressure in Pa)
- :math:`CP(6) = m^w`, van Genuchten :math:`m` for imbibition branch  :math:`P_{cap}^w (S_l)`. Default value is :math:`CP(1)` (recommended unless compelling reason otherwise)
- :math:`CP(7) = P_0^w`, capillary strength parameter for imbibition branch :math:`P_{cap}^w (S_l)` (Pa). Default value is :math:`CP(3)` (recommended unless compelling reason otherwise)
- :math:`CP(8) =` parameter indicating whether to invoke non-zero :math:`P_{cap}` extension for :math:`S_l \gt S_l^\ast = 1 - S_{gr}^{\Delta}`

    - =0: no extension; :math:`P_{cap} = 0` for :math:`S_l \gt S_l^\ast`
    - >0: power-law extension for :math:`S_l^\ast \lt S_l \lt 1`, with :math:`P_{cap} = 0` when :math:`S_l = 1`. A non-zero :math:`CP(8)` is the fraction of :math:`S_l^\ast` at which the :math:`P_{cap}` curve departs from the original van Genuchten function. Recommended range of values: 0.97-0.99

- :math:`CP(9) =` flag indicating how to treat negative radicand, which can arise for :math:`S_l \gt S_l^{\Delta 23}` for second-order scanning drainage curves (``ICURV`` = 3), where :math:`S_l^{\Delta 23}` is the turning-point saturation between first-order scanning imbibition (``ICURV`` = 2) and second-order scanning drainage. None of the options below have proved to be robust under all circumstances. If difficulties arise because :math:`S_l \gt S_l^{\Delta 23}` for ``ICURV`` = 3, also consider using ``IEHYS(3)`` > 0 or :math:`CP(10)` < 0, which should minimize the occurrence of :math:`S_l \gt S_l^{\Delta 23}` for ``ICURV`` = 3.

    - 0: :math:`radicand = \max(0, radicand)` regardless of :math:`S_l` value
    - 1: if :math:`S_l \gt S_l^{\Delta 23}`, radicand takes value of radicant at :math:`S_l = S_l^{\Delta 23}`
    - 2: if :math:`S_l \gt S_l^{\Delta 23}`, use first-order scanning imbibition curve (``ICURV`` = 2)

- :math:`CP(10) =` threshold value of :math:`\lvert \Delta S \rvert` (absolute value of saturation change since previous time step) for enabling a branch switch (default is 10\ :sup:`-6`; set to any negative number to do a branch switch no matter how small :math:`\lvert \Delta S \rvert` is; set to a value greater than 1 to never do a branch switch). See also ``IEHYS(3)``
- :math:`CP(11) =` threshold value of :math:`S_{gr}^{\Delta}`. If value of :math:`S_{gr}^{\Delta}` calculated from :math:`S_l^{\Delta}` is less than :math:`CP(11)`, use :math:`S_{gr}^{\Delta} = 0`. Recommended value 0.01-0.03; default is 0.02
- :math:`CP(12) =` flag to turn off hysteresis for :math:`P_{cap}` (no effect on :math:`k_{rl}` and :math:`k_{rg}`; to turn off hysteresis entirely, set :math:`S_{grmax}` in :math:`RP(3)`).

    - 0: hysteresis is on for :math:`P_{cap}`
    - 1: hysteresis is off for :math:`P_{cap}` (switch branches of :math:`P_{cap}` as usual, but set :math:`S_{gr} = 0` in :math:`P_{cap}` calculation. Make sure other parameters of :math:`P_{cap}^d` and :math:`P_{cap}^w` are the same: :math:`CP(1) = CP(6)` and :math:`CP(3) = CP(7)`)

- :math:`CP(13) =` parameter to determine functional form of :math:`P_{cap}` extension for :math:`S_l \lt S_{lmin}` (i.e., :math:`P_{cap} \gt P_{max}`).

    - =0: exponential extension
    - >0: power-law extension with zero slope at :math:`S_l = 0` and :math:`P_{cap} (0) = CP(13)`. Recommended value: 2 to 5 times :math:`CP(4) = P_{max}`. Should not be less than or equal to :math:`CP(4)`.


Simple Hysteresis (ICP=13)
--------------------------

An approximate hysteretic formulation based on the simple hysteresis theory of :cite:label:`patterson2012simple` has been implemented.
The simple hysteresis model is invoked by setting both ``IRP`` and ``ICP`` to 13.
Currently, this option is only available when ECO2N is being used.

The capillary pressure is the :cite:label:`van1980closed` function

.. math::

    P_{cap} = -P_0 \left( \bar{S}_{wn}^{-\frac{1}{m}} - 1 \right)^{1 - m}

where

.. math::

    \bar{S}_{wn} = \frac{S_w - S_{wr}}{1 - S_{wr} - S_{nr}}

and :math:`S_{wr}` and :math:`S_{nr}` are the residual saturations of the wetting phase and the non-wetting phase, respectively, and :math:`S_{nr}` is a variable calculated as described in Section :ref:`relative_permeabilty_functions` for ``IRP`` = 13.
If :math:`\bar{S}_{wn}` is greater than or equal to one, then the capillary pressure is set to zero.
For :math:`S_w \lt S_{wr} + \varepsilon`, :math:`P_{cap}` is a linear extension that smoothly connects to the :cite:label:`van1980closed` function and is capped by :math:`P_{max}`.

Parameters:

- :math:`CP(1) = m`
- :math:`CP(2) = S_{wr}`
- :math:`CP(3) = \frac{1}{P_0}` (Pa\ :sup:`-1`)
- :math:`CP(4)`

    - =0: :math:`P_{max} = 10^{50}`, :math:`\varepsilon = 10^{-5}`
    - >1: :math:`P_{max} = CP(4)`, :math:`\varepsilon = 10^{-5}`
    - <1: :math:`P_{max} = 10^{50}`, :math:`\varepsilon = CP(4)`

- :math:`CP(5) = S_{ls}` (recommend 1)
- :math:`CP(6) = 0` unless Active Fracture Model is invoked (untested)
- :math:`CP(7)`

    - <0: :math:`= -f_{snr}` in linear trapping model
    - >0: :math:`S_{nrmax}` in Land trapping model


.. _icp31:

Three-Phase Functions of Parker et al. (ICP=31)
-----------------------------------------------

After :cite:label:`parker1987parametric`.

.. math::

    P_{cgn} = -\frac{\rho_l g}{\alpha_{gn}} \left( \left( \bar{S}_n \right)^{-\frac{1}{m}} - 1 \right)^{\frac{1}{n}}

.. math::

    P_{cgl} = -\frac{\rho_l g}{\alpha_{nl}} \left( \left( \bar{S}_l \right)^{-\frac{1}{m}} - 1 \right)^{\frac{1}{n}} - \frac{\rho_l g}{\alpha_{gn}} \left( \left( \bar{S}_n \right)^{-\frac{1}{m}} - 1 \right)^{\frac{1}{n}}

with

.. math::

    m = 1 - \frac{1}{n}

.. math::

    \bar{S}_l = \frac{S_l - S_m}{1 - S_m}

.. math::
    
    \bar{S}_n = \frac{S_l + S_n - S_m}{1 - S_m}

Parameters:

- :math:`CP(1) = S_m`
- :math:`CP(2) = n`
- :math:`CP(3) = \alpha_{gn}`
- :math:`CP(4) = \alpha_{nl}`

These functions have been modified so that the capillary pressures remain finite at low aqueous saturations.
This is done by calculating the slope of the capillary pressure functions at :math:`\bar{S}_l` and :math:`\bar{S}_n` = 0.1. If :math:`\bar{S}_l` or :math:`\bar{S}_n` is less than 0.1, the capillary pressures are calculated as linear functions in this region with slopes equal to those calculated at scaled saturations of 0.1.


ICP=32
------

Same as :ref:`icp31`, except that the strength coefficients are directly provided as inputs, rather than being calculated from the parameters :math:`\alpha_{gn}` and :math:`\alpha_{nl}`.
The capillary pressure functions are then

.. math::

    P_{cgn} = -P_{cgn, 0} \left( \left( \bar{S}_n \right)^{-\frac{1}{m}} - 1 \right)^{\frac{1}{n}}

.. math::

    P_{cgl} = -P_{cnl, 0} \left( \left( \bar{S}_l \right)^{-\frac{1}{m}} - 1 \right)^{\frac{1}{n}} - P_{cgn, 0} \left( \left( \bar{S}_n \right)^{-\frac{1}{m}} - 1 \right)^{\frac{1}{n}}

Parameters:

- :math:`CP(1) = S_m`
- :math:`CP(2) = n`
- :math:`CP(3) = P_{cgn, 0}`
- :math:`CP(4) = P_{cnl, 0}`


ICP=33
------

Same as :ref:`icp31`, except that the capillary pressures are modified for small gas saturations to reduce the derivative.

If :math:`S_l + S_n \gt 0.99`

.. math::

    P_{cgn} = P_{cgn} \frac{1 - S_l - S_n}{0.01}

If :math:`S_l \gt 0.99`

.. math::

    P_{cnl} = P_{cnl} \frac{1 - S_l}{0.01}


ICP=34
------

Same as :ref:`icp31`, except that the capillary pressures are smoothened out for small gas saturations.

If :math:`S_l + S_n \gt 0.99`

.. math::

    P_{cgn} = P_{cgn} \left( -10^6 \left( S_l + S_n - 0.99 \right)^3 + 1 \right)

If :math:`S_l \gt 0.99`

.. math::

    P_{cnl} = P_{cnl} \left( -10^6 \left( S_l - 0.99 \right)^3 + 1 \right)


Custom
------

Additional capillary pressure functions can be programmed into subroutine *PCAP* in a fashion completely analogous to that for relative permeabilities (see Section :ref:`Custom Relative Permeability Functions <relative_permeabilty_custom>`).
