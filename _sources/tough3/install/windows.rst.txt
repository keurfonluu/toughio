.. _installation_on_windows:

Installation on Windows
=======================

On Windows, it is recommended to compile TOUGH3 using Windows Subsystem for Linux (WSL). Otherwise, TOUGH3 can be compiled using Cygwin.


Installation with WSL
---------------------

Please refer to the following link to install WSL on Windows 10 and Windows 11: https://docs.microsoft.com/en-us/windows/wsl/install

Once WSL is setup, refer to Section :ref:`installation_on_linux` to compile TOUGH3.

If you get an error like `"/bin/bash^M: bad interpreter: No such file or directory"`, run the following commands:

.. code-block:: bash

    sudo apt install dos2unix
    dos2unix *.sh
