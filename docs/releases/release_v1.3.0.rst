===============================
 v1.3.0 \| Release Notes
===============================


**Release date**: November 1, 2022

Enhancement & Bug Fix release

--------------

Features, v1.3.0
---------------------------------

    * **Prompt Toolkit v3 Compatibility Enhancement**:

        - Upgraded code for |link-v1.3.0a| dependency to utilise a queue in threaded operations.  This is required for compatibility with |link-v1.3.0b| (current version as of this writing).

        - **Note**: Since this upgrade breaks backward compatibility with prompt-toolkit v2 used in `keyup <http://keyup.readthedocs.io>`__ version 1.2.X, only keyup version 1.3+ may be used with prompt-toolkit v3.X installed on your local machine.




Maintenance, v1.3.0
----------------------

    * Resolved |link-v1.3.0c|:

        -  Issue resulted from broken forward compatibility with `Amazon Web Services' <https://aws.amazon.com>`__ `application programming interface (API) <https://docs.aws.amazon.com/accounts/latest/reference/api-reference.html>`__ that evolved during the last 2 years as API enhancements were made.

        -  Defect caused `keyup <http://keyup.readthedocs.io>`__ to create a second `Identity & Access Management (IAM) <https://aws.amazon.com/iam>`__ access key instead of renewing the existing access key.

        -  Although this error was isolated only to IAM users with a single access key, this issue breaks the major use case for keyup (rotation of a single IAM access key).  Issue did not affect key rotation operations for IAM users with `2 registered IAM access keys <https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys>`__.  Since users with 2 access keys would not have noticed any problems with `keyup <http://keyup.readthedocs.io>`__, this led to a wider misconception that |link-v1.3.0c| was transient.




.. role:: underline
    :class: underline


.. |link-v1.3.0a| raw:: html

    <a href="https://python-prompt-toolkit.readthedocs.io" target="_blank">prompt-toolkit</a>

.. |link-v1.3.0b| raw:: html

    <a href="https://python-prompt-toolkit.readthedocs.io/en/master/pages/upgrading/3.0.html" target="_blank">prompt-toolkit v3</a>

.. |link-v1.3.0c| raw:: html

    <a href="https://bitbucket.org/blakeca00/keyup/issues/52/key-rotation-operation-creating-2nd-access" target="_blank">Issue 52</a>


--------------

( `Back to Releases <./toctree_releases.html>`__ )

--------------

|
