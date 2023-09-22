TOUGH3
======

TOUGH3 is a general-purpose numerical simulator for multi-dimensional fluid and heat flows of multiphase, multicomponent fluid mixtures in porous and fractured media.
It is developed as an enhanced, more efficient version of the TOUGH2 suite of codes. TOUGH3 consolidates the serial (TOUGH2; :cite:label:`pruess1999tough2`) and parallel (TOUGH2-MP; :cite:label:`zhang2008user`) implementations, enabling simulations to be performed on desktop computers and supercomputers using a single source code.
New PETSc parallel linear solvers (:cite:label:`balay2016petsc`) are added to the existing serial solvers of TOUGH2 and the Aztec solver used in TOUGH2-MP.
TOUGH3 also implements numerous enhanced features. The code inherits all the existing key processes and features of its predecessors, and is backwards compatible with a few justifiable exceptions. However, the parallel computing capability and the additional, parallel linear solvers employed by TOUGH3 remarkably improve the code's computational efficiency.
 
The present documentation provides a summary of the mathematical models and numerical methods, discusses new user features, and gives complete specifications for preparing input data.
It also includes a quick start guide to TOUGH3 that describes how to install the code, set up the problem, execute the simulation, and analyze the output.
To make this documentation self-contained, we include much of the material that was covered in the TOUGH2 user's guide (:cite:label:`pruess1999tough2`).

.. toctree::
    :maxdepth: 2
    :hidden:

    install/index
    guide/index
    eos/index
    references
