
IAM Permissions
^^^^^^^^^^^^^^^^

Required |permissions-link1| permissions to use **keyup**.

--------------

Permissions Contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- :ref:`required`
- :ref:`recommended`
- :ref:`policy-detail`

--------------

.. _required:

Required IAM Policy Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are minimal |permissions-link1| permissions required to return valid results for an IAM user. If an iam user referenced in the local awscli configuration file does not have adequate permissions to return access key information, **keyup** will simply skip the user and omit the iam user from the key report.

The following IAM policy must be assigned to each IAM user either via group policy assignment or directly attached to the IAM user identity in the AWS Account.

.. code-block:: json

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "iam:ListAccountAliases"
          ],
          "Resource": [
            "arn:aws:iam::000000000000:user/*"
          ],
          "Effect": "Allow",
          "Sid": "iamAccountInfo"
        },
        {
          "Action": [
            "iam:CreateAccessKey",
            "iam:DeleteAccessKey",
            "iam:ListAccessKeys",
            "iam:GetAccessKeyLastUsed"
          ],
          "Resource": [
            "arn:aws:iam::742134111111:user/${aws:username}"
          ],
          "Effect": "Allow",
          "Sid": "iamUserChangeOwnAccessKeys"
        }
      ]
    }


Back to :ref:`IAM Permissions` Top

--------------

.. _recommended:

Recommended IAM Policy Permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The policy below is highly recommended as a complement to the required IAM permissions policy above. The recommended policy will require a 2-factor MFA code when attempting to provision resources in an AWS Account.

.. code-block:: json

    {
      "Statement": [
        {
          "Action": [
            "iam:ChangePassword",
            "iam:CreateLoginProfile",
            "iam:DeleteLoginProfile",
            "iam:GetAccountPasswordPolicy",
            "iam:GetAccountSummary",
            "iam:GetLoginProfile",
            "iam:UpdateLoginProfile"
          ],
          "Effect": "Allow",
          "Resource": [
            "arn:aws:iam::000000000000:user/${aws:username}"
          ],
          "Sid": "AllowIndividualUserToSeeTheirAccountInformation"
        },
        {
          "Action": [
            "iam:ListVirtualMFADevices",
            "iam:ListMFADevices"
          ],
          "Effect": "Allow",
          "Resource": [
            "arn:aws:iam::000000000000:user/${aws:username}",
            "arn:aws:iam::000000000000:mfa/*"
          ],
          "Sid": "AllowIndividualUserToListTheirMFA"
        },
        {
          "Action": [
            "iam:CreateVirtualMFADevice",
            "iam:DeactivateMFADevice",
            "iam:DeleteVirtualMFADevice",
            "iam:EnableMFADevice",
            "iam:ResyncMFADevice"
          ],
          "Effect": "Allow",
          "Resource": [
            "arn:aws:iam::000000000000:user/${aws:username}",
            "arn:aws:iam::000000000000:mfa/*"
          ],
          "Sid": "AllowIndividualUserToManageThierMFA"
        },
        {
          "Condition": {
            "Null": {
              "aws:MultiFactorAuthAge": "true"
            }
          },
          "Effect": "Deny",
          "NotAction": "iam:*",
          "Resource": "*",
          "Sid": "DoNotAllowAnythingOtherThanAboveUnlessMFAd"
        }
      ],
      "Version": "2012-10-17"
    }


Back to :ref:`IAM Permissions` Top

--------------

.. _policy-detail:

IAM Policy Details
~~~~~~~~~~~~~~~~~~~~~~~~~~

The iam policy provides explicit permissions to an individual user to read and update *only* the user's own iam access keys.

.. note::

    The IAM policy permissions allow keyup to rotate access keys *without requiring a*
    *Multi-factor Authorization (MFA, 2-factor) code*. This is a recommended policy provided all
    other permissions to provision or modify resources in the AWS Account mandate a 2-factor
    MFA code.

    *an attacker can obtain keys with a compromised iam user account, but can nothing with them.*


``iam:ListAccountAliases``:

    * Required to query the AWS Account for an assigned alias (human-readable account name).
    * Not all AWS Accounts have an alias assigned.
    * If no alias is returned, the AWS Account Id is displayed instead.

``iam:CreateAccessKey``:

    * Required for keyup to generate new access keys when rotating keys.

``iam:DeleteAccessKey``:

    * Required by keyup to delete deprecated access keys after a new set is generated.

``iam:ListAccessKeys``:

    * Required by keyup to list access keys for a given IAM user.

``iam:GetAccessKeyLastUsed``:

    * Required by keyup to retrieve access key meta data (data about a user's key set).



.. |permissions-link1| raw:: html

    <a href="https://docs.aws.amazon.com/iam/index.html" target="_blank">Identity and Access Management (IAM)</a>



--------------

Back to :ref:`IAM Permissions` top

--------------

`Table Of Contents <./index.html>`__

-----------------

|
