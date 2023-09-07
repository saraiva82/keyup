===============================
 v0.9.6 \| Release Notes
===============================


**Release date**: April 7, 2018

--------------

Features, v0.9.6
-----------------

- **Backup Copy of New Keysets**:
    If set in the configuration file, ``keyup`` will write all newly generated
    keysets to both the local awscli configuration as well as a backup filesystem
    location on disk.


Fixed, v0.9.6
--------------

- **Local Configuration File Deletion**:
    some previous installations of ``keyup`` versions experience premature deletion
    of the local configuration file located at:

        ``~/.config/key/config.json``

    Upgrading to version **0.9.6** will remedy this problem;
    after which you should regenerate the local configuration file by executing:

    .. code-block:: bash

        $ keyup --configure


- **Various Bug Fixes**:  Fixed various minor issues


--------------

( `Back to Releases <./toctree_releases.html>`__ )

--------------

|
