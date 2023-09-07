"""
Summary.

    Clean operation to remove residual test artifacts in
    the event of test failures

"""

import os
import sys
import datetime
import subprocess
import inspect
import pytz
import boto3
from botocore.exceptions import ClientError
from pyaws.session import boto3_session
from libtools import exit_codes, logger, stdout_message, Colors

c = Colors()


test_iamusers = ['developer1', 'developer2', 'developer3']


# universal colors
text = c.BLUE
act = c.ORANGE
rd = c.RED
yl = c.YELLOW
fs = c.GOLD3
bd = c.BOLD
gn = c.BRIGHT_GREEN
bcy = c.BRIGHT_CYAN
bbc = bd + c.BRIGHT_CYAN
bbl = bd + c.BRIGHT_BLUE
frame = text
btext = text + c.BOLD
bwt = c.BRIGHT_WHITE
bdwt = c.BOLD + c.BRIGHT_WHITE
ub = c.UNBOLD
url = c.URL
rst = c.RESET


def _current_key(profile_name, surrogate=''):
    """
        Extracts the STS AccessKeyId currently utilised in user's
        profile in the local awscli configuration

    Args:
        profile_name:  a username in local awscli profile
    Returns:
        key_id (str): Amazon STS AccessKeyId
    Raises:
        Exception if profile_name not found in config
    """
    if surrogate:
        profile_name = surrogate
    #
    awscli = 'aws'
    cmd = 'type ' + awscli + ' 2>/dev/null'
    if subprocess.getoutput(cmd):
        cmd = awscli + ' configure get ' + profile_name + '.aws_access_key_id'
    try:
        key_id = subprocess.getoutput(cmd)
    except Exception as e:
        logger.exception(
            '%s: Failed to identify AccessKeyId used in %s profile. Error: %s' %
            (inspect.stack()[0][3], profile_name, str(e)))
        return ''
    return key_id


def delete_keyset(access_key, profile, surrogate='', debug=False):
    """
        Deletes oldest access key credentials associated with a user

    Args:
        - **access_key (str)**:  AccessKeyId of the keyset to delete
        - **user (str)**: profile name of iam user from which to delete key
    Returns:
        TYPE: bool, Success | Failure
    """
    try:
        if os.environ.get('AWS_ACCESS_KEY_ID'):
            session = boto3.Session(
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                profile_name=profile)
            client = session.client('iam')
        else:
            # use in-memory keys set in environment
            client = boto3_session(service='iam', profile=profile)

        if debug:
            # delete keyset, given AccessKeyId
            stdout_message(f'{access_key} set for deletion from profile {profile}')
            return False

        if surrogate:
            response = client.delete_access_key(
                AccessKeyId=access_key, UserName=surrogate
                )
        else:
            response = client.delete_access_key(AccessKeyId=access_key)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            logger.warning(
                '%s: Response code %d, deprecated access key %s may not have been deleted properly' %
                (inspect.stack()[0][3], response['ResponseMetadata']['HTTPStatusCode'], access_key))
            return False
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            logger.exception(
                "%s: AccessKeyId %s Not Found. Key not deleted" %
                (inspect.stack()[0][3], access_key))
            return False
        else:
            logger.exception(
                "%s: Problem deleting AccessKeyId %s (Code: %s Message: %s)" %
                (inspect.stack()[0][3], access_key, e.response['Error']['Code'],
                 e.response['Error']['Message']))
            return False
    except Exception as e:
        logger.exception(
            "%s: Unknown problem deleting AccessKeyId %s (Error: %s)" %
            (inspect.stack()[0][3], access_key, str(e)))
        return False


def query_keyinfo(account, profile, surrogate='', quiet=False):
    """
    Summary.
        boto3 client instantiation and error handling

    Args:
        :account (str): AWS account number
        :profile (str): name of the iam user for which we are interrogating keys
        :surrogate (str): name of profile user used to execute key operations
            in place of the profile user
        :quiet (bool): No output to stdout (True) | Show output (False)

    Returns:
        boto3 response, TYPE: dict

    """
    client = boto3_session(service='iam', profile=profile)

    try:
        if surrogate:
            r = client.list_access_keys(UserName=surrogate)
        else:
            r = client.list_access_keys()
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDenied' and surrogate:
            stdout_message(
                ('User %s has inadequate permissions for key operations\n\t     on user %s - Exit [Code: %d]' %
                 (profile, surrogate, exit_codes['EX_NOPERM']['Code'])),
                prefix='PERM', severity='WARNING'
                )
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])

        elif e.response['Error']['Code'] == 'AccessDenied':
            stdout_message(
                ('%s: User %s has inadequate permissions to conduct key operations. Exit [Code: %d]'
                 % (inspect.stack()[0][3], profile, exit_codes['EX_NOPERM']['Code'])),
                prefix='AUTH', severity='WARNING')
            logger.warning(exit_codes['EX_NOPERM']['Reason'])
            sys.exit(exit_codes['EX_NOPERM']['Code'])

        elif e.response['Error']['Code'] == 'NoSuchEntity':
            tab = '\n\t'.expandtabs(12)
            user = rd + bd + (surrogate if surrogate else profile) + rst
            stdout_message(
                (
                    'User %s does not exist in local awscli profiles %s for AWS Account %s [Code: %d]'
                    % (user, tab, bdwt + account + rst, exit_codes['EX_AWSCLI']['Code'])
                ),
                prefix='USER',
                severity='WARNING'
            )
            logger.warning(exit_codes['EX_AWSCLI']['Reason'])
            sys.exit(exit_codes['EX_AWSCLI']['Code'])

        else:
            logger.warning(
                '%s: Inadequate User permissions (Code: %s Message: %s)' %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            raise e
    return r['AccessKeyMetadata'], r['ResponseMetadata']['HTTPStatusCode']


def list_keys(account, profile, iam_user, surrogate='', stage=None, quiet=False):
    """
    Summary.
        Displays iam user available access keys

    Args:
        :account (str): AWS account number
        :profile (str): name of the iam user for which we are interrogating keys
        :iam_user (str): name of the iam user which corresponds to profile name
            from local awscli configuration
        :surrogate (str): name of profile user used to execute key operations
            in place of the profile user
        :stage (str): stage of key rotation; ie, either BEFORE | AFTER rotation
        :quiet (bool): No output to stdout (True) | Show output (False)

    Returns:
        TYPE: list, AccessKeyIds listed for the IAM user

    """
    metadata, statuscode = query_keyinfo(account, profile, surrogate, quiet)

    if not str(statuscode).startswith('20'):
        fx = inspect.stack()[0][3]
        raise OSError(
                '{}: Problem retrieving access keys for user profile: {}'.format(fx, profile)
            )

    # collect key metadata
    access_keys = [x['AccessKeyId'] for x in metadata]
    return access_keys, metadata


def map_identity(profile):
    """
    Summary:
        retrieves iam user info for profiles in awscli config
    Args:
        :user (str): string, local profile user from which the current
           boto3 session object created
    Returns:
        :iam_user (str): AWS iam user corresponding to the provided
           profile user in local config
    """
    try:
        sts_client = boto3_session(service='sts', profile=profile)
        r = sts_client.get_caller_identity()
        iam_user = r['Arn'].split('/')[1]
        account = r['Account']
        logger.info(
            '%s: profile %s mapped to iam_user: %s' %
            (inspect.stack()[0][3], profile, iam_user)
            )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidClientTokenId':
            return None, None
        else:
            logger.warning(
                '%s: Inadequate User permissions (Code: %s Message: %s)' %
                (inspect.stack()[0][3], e.response['Error']['Code'],
                 e.response['Error']['Message']))
            raise e
    return iam_user, account


def _key_age(create_dt):
    """

        Calculates Access key age from today given it's creation date

    Args:
        :**create_dt (datetime object)**: the STS CreateDate parameter returned
          with key key_metadata when an iam access key is created

    Returns:
        age, TYPE: timedelta datatime object

    """
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    delta_td = now - create_dt
    return delta_td


def deprecated_key(profile, metadata):
    r = list(filter(lambda x: x['AccessKeyId'] != _current_key(profile), metadata))
    return r[0]['AccessKeyId']


def active_key(profile):
    """
    Determines which iam access keys are active in the local
    awscli configurtion
    """
    try:
        client = boto3_session(service='sts', profile=profile)
    except ClientError as e:
        fx = inspect.stack()[0][3]
        logger.exception(f'{fx}: Error during sts call: {e}')
    return client.get_caller_identity()['UserId']


def clean_keys(debug=False):
    """
    Identify key for deletion if 2 exit for an iam user.  If yes, delete
    one access key
    """
    for profilename in test_iamusers:

        # id info from profile user
        iam_user, aws_account = map_identity(profile=profilename)

        if (iam_user or aws_account) is None:
            stdout_message(
                message=f'Skipping user {profilename} cannot authenticate - invalid credentials',
                prefix='WARN'
            )
            continue

        # key info
        keys, keydata = list_keys(account=aws_account, profile=profilename, iam_user=iam_user)

        if len(keys) < 2:
            stdout_message(f'Only 1 access key associated with {profilename} - Nothing to clean')
            continue
        else:
            _key = deprecated_key(profilename, keydata)

            if delete_keyset(_key, profilename, debug):
                stdout_message(
                        f'Successfully deleted second key {_key} for profile_name {profilename}',
                        prefix='OK'
                    )
            else:
                stdout_message(
                        f'Failure to delete second access key {_key} for profile_name {profilename}',
                        prefix='WARN'
                    )


if __name__ == '__main__':
    debug = False
    if '--debug' in sys.argv:
        debug = True
        stdout_message('Debug mode enabled')

    clean_keys(debug)
    sys.exit(exit_codes['EX_OK']['Code'])
