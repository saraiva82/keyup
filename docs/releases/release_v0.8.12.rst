===============================
 v0.8.12 \| Release Notes
===============================


**Release date**: Jan 19, 2018

--------------

Features, v0.8.12
-----------------

- **Conduct key operations for another user** (--user-name Parameter)
    Profile user can be used to list or rotate keys for another user given in the
    --user-name parameter.  This enables key operations when a profile is not
    represented in the local awscli configuration.

- **Key Age Hooks**: Hooks put in place for keyup rotate functionality when key age is between
    key_min age and key_max age.  Beneficial for automated (ie, scheduled) key rotation so that
    keys only refreshed when older than the min age.  Avoids premature key rotation when executing
    in automated mode via scheduler.

Fixed, v0.8.12
--------------

- **Configuration Script**:  Fixed issues resolving answers to configuration questionnaire
- **Key Age Inaccuracies**:  Fixed key age across multi-day periods.  Now accurate.

--------------

( `Back to Releases <./toctree_releases.html>`__ )

--------------

|
