===============================
 v1.2.0 \| Release Notes
===============================


**Release date**: August 13, 2019

Performance, Reliability, & Stability release

--------------

Performance & Stability, v1.2.0
---------------------------------

    * **Extensive installation testing** from pypi to resolve post-installation artifact issues.

    * **sudo/ root user installation**:  testing resulted in extensive refactor of ``setup.py`` and other installation artifacts

    * |location_r2| is now the default format for all included documentation for `keyup <http://keyup.readthedocs.io>`__  deployments, replacing markdown README and other documnetation in this format.

    * **common.py**:  new commons (as in "common functionality") module introduced in this release.  This is part of the deprecation movement for ``script_utils.py`` module.


Reliability, v1.2.0
----------------------

    * A runtime test to ensure system logger is enabled and functional added in this release. Prevents catastrophic exception failures when keyup is used in a Docker container or LXC environment.

    * Applies to the following linux system loggers:

        * |location_r3|
        * |location_r4|


.. |location_r2| raw:: html

    <a href="http://docutils.sourceforge.net/rst.html" target="_blank">Restructuredtext</a>

.. |location_r3| raw:: html

    <a href="https://www.syslog-ng.com" target="_blank">syslog-ng</a>

.. |location_r4| raw:: html

    <a href="https://wiki.debian.org/Rsyslog" target="_blank">rsyslog</a>


--------------

( `Back to Releases <./toctree_releases.html>`__ )

--------------

|
