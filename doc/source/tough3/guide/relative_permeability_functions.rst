.. _relative_permeabilty_functions:

Relative Permeability Functions
===============================

TOUGH3 provides several relative permeability functions for two-phase or three-phase flow problems.
The original TOUGH2 two-phase functions have been retained (from ``IRP`` = 1 to ``IRP`` = 8).
The modified Brooks-Corey and van Genuchten models and two versions of the hysteresis model (regular and simple) are implemented (``IRP`` = 10, 11, 12, and 13).
The three-phase functions from TMVOC and ECO2M start at ``IRP`` = 31.
For TMVOC, if one of the two-phase functions is chosen, the NAPL relative permeability is assumed to be zero.
For ECO2M, the two-phase functions are only applicable when an aqueous phase and a single CO\ :sub:`2`-rich phase are present.
If one of the two-phase functions is chosen, the relative permeability of the CO\ :sub:`2`-rich phase will be the same function of saturation, regardless whether the CO\ :sub:`2`-rich phase is liquid or gas.
The notation used below is:

- :math:`k_{rl}`: aqueous phase relative permeability
- :math:`k_{rg}`: gas (for all two-phase EOSs and TMVOC) or gaseous CO\ :sub:`2` (for ECO2M) phase relative permeability
- :math:`k_{rn}`: NAPL (for TMVOC) or liquid CO\ :sub:`2` (for ECO2M) phase relative permeability
- :math:`S_l`, :math:`S_g`, and :math:`S_n` are the saturations of aqueous, gas (or gaseous COCO\ :sub:`2`) and NAPL (or liquid CO\ :sub:`2`) phases, respectively


Linear Functions (IRP=1)
------------------------

| :math:`k_{rl}` increases linearly from 0 to 1 in range :math:`RP(1) \le S_l \le RP(3)`
| :math:`k_{rg}` increases linearly from 0 to 1 in range :math:`RP(2) \le S_l \le RP(4)`
| Restrictions: :math:`RP(3) \gt RP(1)`, :math:`RP(4) \gt RP(2)`

If :math:`RP(5) \gt 0`, :math:`k_{rn}` increases linearly from 0 to 1 in the range :math:`RP(1) \le S_n \le RP(3)`

| If :math:`RP(5) \gt 0` and :math:`RP(6) \gt 0`, :math:`k_{rn}` increases linearly from 0 to 1 in the range :math:`RP(5) \le S_n \le RP(6)`
| Restrictions: :math:`RP(6) \lt RP(5)`


IRP=2
-----

.. math::
    
    k_{rl} = S_l^{RP(1)}

.. math::
    
    k_{rg} = 1


Corey's Curves (IRP=3)
----------------------

After :cite:label:`corey1954interrelation`.

.. math::

    k_{rl} = \hat{S}^4

.. math::

    k_{rg} = \left( 1 - \hat{S} \right)^2 \left( 1 - \hat{S}^2 \right)^2


where :math:`\hat{S} = \frac{S_l - S_{lr}}{1 - S_{lr} - S_{gr}}`.

Parameters:

- :math:`RP(1) = S_{lr}`
- :math:`RP(2) = S_{gr}`

Restrictions: :math:`RP(1) + RP(2) \lt 1`


Grant's Curves (IRP=4)
----------------------

After :cite:label:`grant1977permeability`.

.. math::

    k_{rl} = \hat{S}^4

.. math::

    k_{rg} = 1 - k_{rl}

Parameters:

- :math:`RP(1) = S_{lr}`
- :math:`RP(2) = S_{gr}`

Restrictions: :math:`RP(1) + RP(2) \lt 1`


All Phases Perfectly Mobile (IRP=5)
-----------------------------------

:math:`k_{rg} = k_{rg} = 1` for all saturations.

No parameters.


Functions of Fatt and Klikoff (IRP=6)
-------------------------------------

After :cite:label:`fatt1959effect`.

.. math::

    k_{rl} = \left( S^\ast \right)^3

.. math::

    k_{rg} = \left( 1 - S^\ast \right)^3

where :math:`S^\ast = \frac{S_l - S_{lr}}{1 - S_{lr}}`.

Parameters:

- :math:`RP(1) = S_{lr}`

Restriction: :math:`RP(1) \lt 1`


van Genuchten-Mualem Model (IRP=7)
----------------------------------

After :cite:label:`mualem1976new` and van :cite:label:`van1980closed`.

.. math::

    k_{rl} =
        \begin{cases}
            \sqrt{S^\ast} \left( 1 - \left( 1 - \left( S^\ast \right)^{\frac{1}{\lambda}} \right)^{\lambda} \right)^2 & \text{if $S_l \lt S_{ls}$} \\
            1 & \text{if $S_l \ge S_{ls}$} \\
        \end{cases}

Gas relative permeability can be chosen as one of the following two forms, the second of which is due to :cite:label:`corey1954interrelation`.

.. math::

    k_{rg} =
        \begin{cases}
            1 - k_{rl} & \text{if $S_{gr} = 0$} \\
            \left( 1 - \hat{S} \right)^2 \left( 1 - \hat{S}^2 \right) & \text{if $S_{gr} \gt 0$} \\
        \end{cases}

subject to the restriction :math:`0 \le k_{rl}`, :math:`k_{rg} \le 1`.

Here,

.. math::

    S^\ast = \frac{S_l - S_{lr}}{S_{ls} - S_{lr}}

.. math::

    \hat{S} = \frac{S_l - S_{lr}}{1 - S_{lr} - S_{gr}}

Parameters:

- :math:`RP(1) = \lambda`
- :math:`RP(2) = S_{lr}`
- :math:`RP(3) = S_{ls}`
- :math:`RP(4) = S_{gr}`

.. note::

    Parameter :math:`\lambda` is :math:`m` in van Genuchten's notation, with :math:`m = 1 - \frac{1}{n}`; parameter :math:`n` is often written as :math:`\beta`.


Functions of Verma et al. (IRP=8)
---------------------------------

After :cite:label:`verma1985study`.

.. math::

    k_{rl} = \hat{S}^3

.. math::

    k_{rg} = A + B \hat{S} + C \hat{S}^2

where :math:`\hat{S} = \frac{S_l - S_{lr}}{S_{ls} - S_{lr}}`

Parameters as measured by Verma et al. (1985) for steam-water flow in an unconsolidated sand:

Parameters:

- :math:`RP(1) = S_{lr} = 0.2`
- :math:`RP(2) = S_{ls} = 0.895`
- :math:`RP(3) = A = 1.259`
- :math:`RP(4) = B = -1.7615`
- :math:`RP(5) = C = 0.5089`


Modified Brooks-Corey Model (IRP=10)
------------------------------------

A modified version of the Brooks-Corey model (:cite:label:`luckner1989consistent`) has been implemented to prevent the capillary pressure from decreasing towards negative infinity as the effective saturation approaches zero.
The modified Brooks-Corey model is invoked by setting both ``IRP`` and ``ICP`` to 10.

.. math::

    k_{rl} = S_{ek}^{\frac{2 + \lambda}{\lambda}}

.. math::

    k_{rg} =
        \begin{cases}
            \left( 1 - S_{ek} \right)^2 \left( 1 - S_{ek}^{\frac{2 + \lambda}{\lambda}} \right) & \text{if $RP(3) = 0$} \\
            1 - k_{rl} & \text{if $RP(3) \ne 0$} \\
        \end{cases}

where

.. math::

    S_{ek} = \frac{S_l - S_{lrk}}{1 - S_{lrk} - S_{gr}}

Parameters:

- :math:`RP(1) = S_{lrk}`
- :math:`RP(2) = S_{gr}`
- :math:`RP(3) =` flag to indicate which equation is used for :math:`k_{rg}`


Modified van Genuchten Model (IRP=11)
-------------------------------------

A modified version of the van Genuchten model (:cite:label:`luckner1989consistent`) has been implemented to prevent the capillary pressure from decreasing towards negative infinity as the effective saturation approaches zero.
The modified van Genuchten model is invoked by setting both ``IRP`` and ``ICP`` to 11.

.. math::

    k_{rl} = S_{ekl}^{\gamma} S_{ekl}^{\left( 1 - \gamma \right) \eta} \left( 1 - \left( 1 - S_{ekl}^{\frac{1 - \gamma}{m}} \right)^m \right)^2

.. math::

    k_{rg} =
        \begin{cases}
            \left( 1 - S_{ekg} \right)^{\zeta} \left( 1 - S_{ekg}^{\frac{1}{m}} \right)^{2m} & \text{if $RP(3) = 0$} \\
            1 - k_{rl} & \text{if $RP(3) \ne 0$} \\
        \end{cases}

where

.. math::

    S_{ekl} = \frac{S_l - S_{lrk}}{1 - S_{lrk}}

.. math::

    S_{ekg} = \frac{S_l}{1 - S_{gr}}

Parameters:

- :math:`RP(1) = S_{lrk}`, if negative, :math:`S_{lrk} = 0` for calculating :math:`k_{rg}`, and absolute value is used for calculating :math:`k_{rl}`
- :math:`RP(2) = S_{gr}`, if negative, :math:`S_{gr} = 0` for calculating :math:`k_{rl}`, and absolute value is used for calculating :math:`k_{rg}`
- :math:`RP(3) =` flag to indicate which equation is used for :math:`k_{rg}`
- :math:`RP(4) = \eta` (default = 1/2)
- :math:`RP(5) = \varepsilon_k`, use linear function between :math:`k_{rl}` (:math:`S_e = 1 - \varepsilon_k`) and 1.0
- :math:`RP(6) = a_{fm}`, constant fracture-matrix interaction reduction factor, in combination with Active Fracture Model
- :math:`RP(7) = \zeta` (default = 1/3)


Regular Hysteresis (IRP=12)
---------------------------

The hysteretic form of the van Genuchten model (:cite:label:`parker1987model, lenhard1987model`) has been implemented.
Details of the implementation are described in :cite:label:`doughty2013user`.
The regular hysteresis model is invoked by setting both ``IRP`` and ``ICP`` to 12.

.. math::

    k_{rl} = \sqrt{\bar{S}_l} \left( 1 - \left( 1 - \frac{\bar{S}_{gt}}{1 - \bar{S}_l^{\Delta}} \right) \left( 1 - \left( \bar{S}_l + \bar{S}_{gt} \right)^{\frac{1}{m}}\right)^m - \frac{\bar{S}_{gt}}{1 - \bar{S}_l^{\Delta}} \left( 1 - \left( \bar{S}_l^{\Delta} \right)^{\frac{1}{m}} \right)^m \right)^2

.. math::

    k_{rg} = k_{rgmax} \left( 1 - \left( \bar{S}_l + \bar{S}_{gt} \right) \right)^{\gamma} \left( 1 - \left( \bar{S}_l + \bar{S}_{gt} \right)^{\frac{1}{m}} \right)^{2m}

where

.. math::

    \bar{S}_l = \frac{S_l - S_{lr}}{1 - S_{lr}}

.. math::

    \bar{S}_l^{\Delta} = \frac{S_l^{\Delta} - S_{lr}}{1 - S_{lr}}

.. math::

    \bar{S}_{gt} = \frac{S_{gr}^{\Delta} \left( S_l - S_l^{\Delta} \right)}{\left( 1 - S_{lr} \right) \left( 1 - S_l^{\Delta} - S_{gr}^{\Delta} \right)}

.. math::

    S_{gr}^{\Delta} = \frac{1}{\frac{1}{1 - S_l^{\Delta}} + \frac{1}{S_{gr, max}} - \frac{1}{1 - S_{lr}}}

:math:`S_l^{\Delta}` is the turning-point saturation, and :math:`S_{gr}^{\Delta}` is the residual gas saturation.

Parameters:

- :math:`RP(1) = m`, van Genuchten :math:`m` for liquid relative permeability (need not equal :math:`CP(1)` or :math:`CP(6)); :math:`k_{rl}` uses the same :math:`m` for drainage and imbibition.
- :math:`RP(2) = S_{lr}`, :math:`k_{rl} (S_{lr}) = 0`, :math:`k_{rg} (S_{lr}) = k_{rgmax}`. Must have :math:`S_{lr} \gt S_{lmin}` in capillary pressure (:math:`CP(2)). :math:`S_{lr}` is minimum saturation for transition to imbibition branch. For :math:`S_l \lt S_{lr}`, curve stays on primary drainage branch even if :math:`S_l` increases.
- :math:`RP(3) = S_{grmax}`, maximum possible value of :math:`S_{gr}^{\Delta}`. Note that the present version of the code requires that :math:`S_{lr} + S_{grmax} \lt 1`, otherwise there will be saturations for which neither fluid phase is mobile, which the code cannot handle. Setting :math:`S_{grmax} = 0` effectively turns off hysteresis. As a special option, a constant, non-zero value of Sgr may be employed by setting :math:`CP(10) \gt 1` and making :math:`RP(3)` negative. The code will set :math:`S_{gr}^{\Delta}` = :math:`-RP(3)` for all grid blocks at all times.
- :math:`RP(4) = \gamma`, typical values 0.33 - 0.50
- :math:`RP(5) = k_{rgmax}`
- :math:`RP(6) =` fitting parameter for :math:`k_{rg}` extension for :math:`S_l \lt S_{lr}` (only used when :math:`k_{rgmax} \lt 1`); determines type of function for extension and slope of :math:`k_{rg}` at :math:`S_l = 0`:

    - ≤0: use cubic spline for :math:`0 \lt S_l \lt S_{lr}`, with slope at :math:`S_l = 0` of :math:`RP(6)`
    - >0: use linear segment for :math:`0 \lt S_l \lt RP(8) S_{lr}` and cubic spline for :math:`RP(8) S_{lr} \lt S_l \lt S_{lr}`, with slope at :math:`S_l = 0` of :math:`-RP(6)`.  

- :math:`RP(7) =` numerical factor used for :math:`k_{rl}` extension to :math:`S_l \gt S_l^\ast`. :math:`RP(7)` is the fraction of :math:`S_l^\ast` at which :math:`k_{rl}` curve departs from the original van Genuchten function. Recommended range of values: 0.95-0.97. For :math:`RP(7) = 0`, :math:`k_{rl} = 1` for :math:`S_l \gt S_l^\ast` (not recommended).
- :math:`RP(8) =` numerical factor used for linear :math:`k_{rg}` extension to :math:`S_l \lt S_{lr}` (only used when :math:`k_{rgmax} \lt 1`). :math:`RP(8)` is the fraction of :math:`S_{lr}` at which the linear and cubic parts of the extensions are joined.
- :math:`RP(9) =` flag to turn off hysteresis for :math:`k_{rl}` (no effect on :math:`P_c` and :math:`k_{rg}`; to turn off hysteresis entirely, set :math:`S_{grmax} = 0` in :math:`RP(3)`).

    - 0: hysteresis is on for :math:`k_{rl}`
    - 1: hysteresis is off for :math:`k_{rl}` (force :math:`k_{rl}` to stay on primary drainage branch (:math:`k_{rl}^d`) at all times)

- :math:`RP(10) = m_{gas}`, van Genuchten m for gas relative permeability (need not equal :math:`CP(1)` or :math:`CP(6)`); :math:`k_{rg}` uses same :math:`m_{gas}` for drainage and imbibition. If zero or blank, use :math:`RP(1)` so that :math:`m_{gas} = m`.


Simple Hysteresis (IRP=13)
--------------------------

The regular hysteresis option (``IRP`` = ``ICP`` = 12) provides a rigorous representation of hysteretic relative permeability and capillary pressure curves.
However, it can significantly slow down TOUGH3 simulations, because small time steps are often required at turning points, when a grid block switches between drainage and imbibition, because the slopes of the characteristic curves are discontinuous.
Moreover, several control parameters are needed, which generally must be determined by trial and error, for the code to run smoothly.
An alternative means of capturing the essence of hysteresis, while maintaining continuous slopes and requiring no additional control parameters, is the simple hysteresis algorithm of :cite:label:`patterson2012simple`, which is invoked with ``IRP`` = ``ICP`` = 13.
Presently this option is only available when ECO2N is being used.

The :cite:label:`mualem1976new` relative permeability model is used for the non-wetting phase:

.. math::

    k_{rn} = \sqrt{1 - \bar{S}_{wn}} \left( 1 - \bar{S}_{wn}^{\frac{1}{m}} \right)^{2m}

where

.. math::

    \bar{S}_{wn} = \frac{S_w - S_{wr}}{1 - S_{wr} - S_{nr}}

and :math:`S_{wr}` and :math:`S_{nr}` are residual saturations of the wetting and non-wetting phases, respectively.
Hysteresis is implemented by considering :math:`S_{nr}` to be a variable, which is calculated from the maximum historical non-wetting phase saturation in a grid block, :math:`S_{nmax}`.
The user has the option to specify :math:`S_{nr}` as a linear function of the historical :math:`S_{nmax}`:

.. math::

    S_{nr} = f_{snr} S_{nmax}

or :math:`S_{nr}` can be calculated using a modified form of the :cite:label:`land1968calculation` relationship

.. math::

    S_{nr} = \frac{S_{nmax}}{1 + C S_{nmax}}

with

.. math::

    C = \frac{1}{S_{nrmax}} - \frac{1}{1 - S_{wr}}

where :math:`f_{snr}` and :math:`S_{nrmax}`, the maximum residual non-wetting phase saturation, are user-specified material properties.
:math:`S_{nr}` is calculated during every Newton-Raphson iteration.
If :math:`S_n` drops below :math:`S_{nr}` by dissolution or compression, :math:`S_{nmax}` is recalculated as

.. math::

    S_{nmax} = \frac{S_n}{f_{snr}} \text{ or } S_{nmax} = \frac{S_n}{1 - C S_n}

Wetting-phase relative permeability (non-hysteretic) is from van Genuchten (1980)

.. math::

    k_{rw} = \sqrt{\bar{S}_w} \left( 1 - \left( 1 - \bar{S}_w^{\frac{1}{m}}\right)^m \right)^2

where

.. math::

    \bar{S}_w = \frac{S_w - S_{wr}}{S_{ws} - S_{wr}}

Parameters:

- :math:`RP(1) = m` to use in :math:`k_{rw}`
- :math:`RP(2) = S_{wr}`
- :math:`RP(3) = S_{ws}` (recommend 1)
- :math:`RP(4)`

    - <0: :math:`= -f_{snr}` in linear trapping model
    - >0: :math:`S_{nrmax}` in Land trapping model

- :math:`RP(5) = m_{gas}`, :math:`m` to use in :math:`k_{rn}`: if zero or blank, use :math:`RP(1)`
- :math:`RP(6) =` power to use in first term in :math:`k_{rn}` (default 1/2)
- :math:`RP(7)`

    - =0: use :math:`\left( 1 - \bar{S}_{wn} \right)` in first term in :math:`k_{rn}` (Mualem, 1976)
    - >0: use :math:`S_g` in first term in :math:`k_{rn}` (:cite:label:`charbeneau2007distribution`), so that :math:`k_{rn}` does not go to 1 when immobile liquid phase is present


All Phases Perfectly Mobile (IRP=31)
------------------------------------

:math:`k_{rg} = k_{rl} = k_{rn} = 1`

No parameters.


.. _irp32:

Modified Version of Stone's First Three-Phase Method (IRP=32)
-------------------------------------------------------------

After :cite:label:`stone1970probability`.

.. math::

    k_{rg} = \left( \frac{S_g - S_{gr}}{1 - S_{gr}} \right)^n

.. math::

    k_{rl} = \left( \frac{S_l - S_{lr}}{1 - S_{lr}} \right)^n

.. math::

    k_{rn} = \left( \frac{1 - S_g - S_l - S_{nr}}{1 - S_g - S_{lr} - S_{nr}} \right) \left( \frac{1 - S_{lr} - S_{nr}}{1 - S_l - S_{nr}} \right) \left( \frac{\left( 1 - S_g - S_{lr} - S_{nr} \right)\left( 1 - S_l \right)}{1 - S_{nr}} \right)^n

When :math:`S_n = 1 - S_l - S_g - S_s` is near irreducible liquid saturation, :math:`S_{nr} \le S_n \le S_{nr} + 0.005`, liquid relative permeability is taken to be

.. math::

    k_{rn}^{'} = k_{rn} \frac{S_n - S_{nr}}{0.005}

Parameters:

- :math:`RP(1) = S_{lr}`
- :math:`RP(2) = S_{nr}`
- :math:`RP(3) = S_{gr}`
- :math:`RP(4) = n`


Three-Phase Functions of Parker et al. (IRP=33)
-----------------------------------------------

After :cite:label:`parker1987parametric`.

.. math::

    k_{rg} = \sqrt{\bar{S}_g} \left( 1 - \left( \bar{S}_n \right)^{\frac{1}{m}} \right)^{2m}

.. math::

    k_{rl} = \sqrt{\bar{S}_l} \left( 1 - \left( 1 - \left( \bar{S}_l \right)^{\frac{1}{m}} \right)^m \right)^2

.. math::

    k_{rn} = \sqrt{\bar{S}_n - \bar{S}_l} \left( \left( 1 - \left( \bar{S}_l \right)^{\frac{1}{m}} \right)^m - \left( 1 - \left( \bar{S}_n \right)^{\frac{1}{m}} \right)^m \right)^2

with

.. math::

    m = 1 - \frac{1}{n}

.. math::

    \bar{S}_g = \frac{S_g}{1 - S_m}

.. math::

    \bar{S}_l = \frac{S_l - S_m}{1 - S_m}

.. math::
    
    \bar{S}_n = \frac{S_l + S_n - S_m}{1 - S_m}

where :math:`k_{rg}`, :math:`k_{rl}`, and :math:`k_{rn}` are limited to values between 0 and 1.

Parameters:

- :math:`RP(1) = S_m`
- :math:`RP(2) = n`


IRP=34
------

Same as :ref:`irp32`, except that

.. math::

    k_{rg} = 1 - \left( \frac{S_n + S_l - S_{lr}}{1 - S_{lr}} \right)^n


Power Law (IRP=35)
------------------

Phases :math:`\beta = l, n, g`.

.. math::

    k_{r \beta} = \left( \frac{S_{\beta} - S_{\beta r}}{1 - S_{\beta r}} \right)^n

Parameters:

- :math:`RP(1) = S_{lr}`
- :math:`RP(2) = S_{nr}`
- :math:`RP(3) = S_{gr}`
- :math:`RP(4) = n`


Functions Used by Faust (1985) for Two-Phase Buckley-Leverett Problem
---------------------------------------------------------------------

After :cite:label:`faust1985transport`.

.. math::

    k_{rl} = \frac{\left( S_l - 0.16 \right)^2}{0.64}

.. math::

    k_{rg} = 0

.. math::
    
    k_{rn} = \frac{\left( 0.8 - S_l \right)^2}{0.64}

where :math:`k_{rl}` and :math:`k_{rn}` are limited to values between 0 and 1.

No parameters.


IRP=37
------

Same are :ref:`irp32`, except a correction factor is applied to :math:`k_{rn}` such as to make :math:`k_{rn}` equal to :math:`k_{rg}` for two-phase conditions with the same aqueous phase saturation.


.. _relative_permeabilty_custom:

Custom
------

If the user wishes to employ other relative permeability relationships, these need to be programmed into subroutine *RELP* in module *Utility.f90*.
The routine has the following structure:

.. code-block:: fortran

    SUBROUTINE RELP(SATU,RELPERM,NNPH,NMAT,USRX)
        ...
        RELP_FUNCTION: SELECT CASE (IRP(NMAT))
		CASE (1)
			CALL RELP_LINEAR(...)
		CASE (2)
			...
		...
		...
		END SELECT RELP_FUNCTION

    END

To code an additional relative permeability function, the user needs to insert a code segment analogous to that shown above, beginning with a CASE option which would be identical to ``IRP`` and calls a subroutine for the additional relative permeability function.
