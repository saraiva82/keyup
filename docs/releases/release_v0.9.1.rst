===============================
 v0.9.1 \| Release Notes
===============================


**Release date**: Jan 22, 2018

--------------

Features, v0.9.1
-----------------

- **Awareness of STS Temporary Credentials**.
    ``keyup`` is now temporary-credential aware in that it will detect when the local awscli
    config contains temporary credentials.  If it does, keyup will test up to 2 profiles to
    determine if the credentials are currently ACTIVE. If ACTIVE, key rotation will not be
    be permitted.  If temp credentials are inactive, key operations proceed normally.  When
    writing to the local config, keyup can keyup can interrupt automated jobs utilising
    temporary credentials.

- **Console Script: for displaying local config file contents**.
    Console script ``keyconfig`` can now be used to display the contents of The local configuration file,
    if one exists.  If the local config file does not exist yet because the user has not yet
    to run the configuration menu, then a message informing the user how to generate a local configure
    is displayed.

- **Documentation: FAQ**.
    Full `Frequently Asked Questions <../FAQ.rst>`__ section on readthedocs
    completed and available.

- **Improved Exception Handling**
    ``keyup`` now handles IAM usernames that do not exist more gracefully during list-keys
    or key rotation operations.


Fixed, v0.9.1
--------------

- **Various Bug Fixes**:  Fixed various minor issues
- **IAM User Reporting Inaccuracies**:  Previously reporting IAM Usernames as 'None'

--------------

( `Back to Releases <./toctree_releases.html>`__ )

--------------

|
