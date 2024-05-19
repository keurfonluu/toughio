.. _installation_on_linux:

Installation on Linux
=====================

Installation of dependencies
****************************

Run the following commands

.. code-block:: bash

    sudo apt update
    sudo apt upgrade
    sudo apt install gcc gfortran mpich cmake libblas-dev liblapack-dev python2 python


Installation of TOUGH3
**********************

Go to your home directory

.. code-block:: bash

    cd

Create and go to a new directory "tough3-build"

.. code-block:: bash

    mkdir tough3-build
    cd tough3-build

Place TOUGH3 installation folders "esd-tough3" and "esd-toughlib" in this new directory

.. code-block:: bash

    cp -R PATH_TO_ESD_TOUGH3 .
    cp -R PATH_TO_ESD_TOUGHLIB .

Go to "esd-tough3"

.. code-block:: bash

    cd esd-tough3

Compile desired EOS (for instance EOS3, can be a list too)

.. code-block:: bash

    ./compile_T3_Linux.sh 3
