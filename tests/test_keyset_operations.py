import os
import sys
import time
import json
import re
import pdb
import datetime
import inspect
from configparser import ConfigParser
import logging
import pytz

# aws imports
import boto3
from botocore.exceptions import ClientError, ProfileNotFound

# test imports
import moto
import pytest
from tests import environment
from keyup.statics import PACKAGE
from keyup import cli
from keyup import list_ops
from keyup import vault

sys.path.insert(0, os.path.abspath(PACKAGE))
import script_utils
sys.path.pop(0)

# global objects
config = ConfigParser()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# set global Autotag-specific vars
account_number = '123456789012'
TestUsers = ('developer1', 'developer2', 'developer3')

# test module globals
base_path = '/tmp/autotag-tests-%s' % time.time()
version = 'testing-' + base_path
test_assets = 'tests/assets'

# set region default
if os.getenv('AWS_DEFAULT_REGION') is None:
    default_region = 'us-east-2'
    os.environ['AWS_DEFAULT_REGION'] = default_region
else:
    default_region = os.getenv('AWS_DEFAULT_REGION')

ami_id = 'ami-redhat7'
min_count = 1
max_count = 2
ec2_size = 't2.micro'


@moto.mock_ec2
def get_regions():
    ec2 = boto3.client('ec2')
    return [x['RegionName'] for x in ec2.describe_regions()['Regions'] if 'cn' not in x['RegionName']]


@pytest.fixture()
def regionize():
    os.environ['AWS_REGION'] = default_region
    yield
    if default_region is not None:
        os.environ['AWS_REGION'] = default_region
    else:
        del os.environ['AWS_REGION']


@pytest.fixture()
def sts_resource_objects(region=default_region):
    moto.mock_sts().start()
    client = boto3.client('sts', region_name=region)
    yield client
    moto.mock_sts().stop()


@pytest.fixture()
def iam_resource_objects(region=default_region):
    moto.mock_iam().start()
    client = boto3.client('iam', region_name=region)
    yield client
    moto.mock_iam().stop()


@pytest.fixture()
def return_reference(filename):
    with open(test_assets + '/' + filename, 'r') as f1:
        f2 = f1.read()
        content = json.loads(f2)
        yield content


@pytest.fixture()
def import_file_object(filepath):
    handle = open(filepath, 'r')
    file_obj = handle.read()
    return file_obj


def tear_down():
    """ Tears down structures setup expressly for testing """
    HOME = os.environ['HOME']
    awscli = HOME + '/.aws/credentials'
    if os.path.isfile(awscli):
        config.read(awscli)
        for profile in config.sections():
            if 'gcreds-dev1' in profile:
                config.pop(profile)
        with open(awscli, 'w') as f1:
            config.write(f1)
        return True
    return False


def get_account_info(profilename=None):
    """
    Summary:
        Queries AWS iam and sts services to discover account id information
        in the form of account name and account alias (if assigned)

    Returns:
        TYPE: tuple
    """
    if profilename:
        session = boto3.Session(profile_name=profilename)
        sts_client = session.client('sts')
        iam_client = session.client('iam')
    else:
        sts_client = boto3.client('sts')
        iam_client = boto3.client('iam')

    try:
        number = sts_client.get_caller_identity()['Account']
        name = iam_client.list_account_aliases()['AccountAliases'][0]
    except IndexError as e:
        name = '<no_alias_assigned>'
        logger.info('Error: %s. No account alias defined. account_name set to %s' % (e, name))
        return (number, name)
    except ClientError as e:
        logger.warning(
            "%s: problem retrieving caller identity (Code: %s Message: %s)" %
            (inspect.stack()[0][3], e.response['Error']['Code'], e.response['Error']['Message'])
            )
        raise e
    return (number, name)


def _classname(method):
    if inspect.ismethod(method):
        for cls in inspect.getmro(method.__self__.__class__):
            if cls.__dict__.get(method.__name__) is method:
                return cls
        method = method.__func__  # fallback to __qualname__ parsing
    if inspect.isfunction(method):
        cls = getattr(inspect.getmodule(method),
                      method.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
        if isinstance(cls, type):
            return cls
    return getattr(method, '__objclass__', None)  # handle special descriptor objects


class TestKeysetOperations():
    """
    Test Operations on IAM Access Keysets (Create, Delete, etc)
    """
    @pytest.mark.parametrize(
        'profile, result', (
            ('developer1', True), ('developer2', True), ('developer3', True)
            ))
    def test_1_list_keys(self, profile, result, region=default_region):
        """
        lists an IAM user's access keys
        """
        # set environment variables
        cli.source_globals()

        # client setup
        session = boto3.Session(profile_name=profile)
        sts_client = session.client('sts')
        r = sts_client.get_caller_identity()
        account = r['Account']
        user = os.path.split(r['Arn'])[1]
        keylist, metadata = list_ops.list_keys(account, profile, iam_user=user)
        # validate looks like a key
        pattern = re.compile('[0-9-A-Z]{20,20}$')
        assert pattern.match(keylist[0])

    @pytest.mark.parametrize(
        'profile, result', (('developer1', True), ('developer2', True),  ('developer3', True)))
    def test_2_create_keyset(self, profile, result, region=default_region):
        """
        creates a new IAM access keyset for a user
        """
        # client setup
        session = boto3.Session(profile_name=profile)
        sts_client = session.client('sts')
        r = sts_client.get_caller_identity()

        user = os.path.split(r['Arn'])[1]
        try:
            success, r_key = cli.create_keyset(iam_user=user, profile=profile)
            # place keyset in env for later retrieval
            access_key = r_key['AccessKey']['AccessKeyId']
            os.environ[profile] = access_key
            logger.info(f'test_2_create_keyset: Profile user {profile} added key: {access_key}')
            # validate looks like a key
            pattern = re.compile('[0-9-A-Z]{20,20}$')
        except ClientError as e:
            cls = _classname(self.test_2_create_keyset)
            logger.exception(f'{cls}: test_2_create_keyset Error: {e}')
            assert False
        except KeyError as e:
            logger.exception(f'{"test_2_create_keyset"}: KeyError on keyword {e}')
            assert True
        assert pattern.match(r_key['AccessKey']['AccessKeyId'])

    @pytest.mark.parametrize('result', ((True), (False)))
    @pytest.mark.parametrize('profile', (('developer1'), ('developer2'),  ('developer3')))
    def test_3_delete_keyset(self, profile, result, region=default_region):
        """
        deletes a user's access keyset
        """
        if result is False:
            key = 'ABCDEFGHIJ0123456789'
        else:
            key = os.getenv(profile)        # retrieve accessKeys created by test 2
            logger.info(f'test_3_delete_keyset: Profile user {profile} attempting to delete AccessKeyId: {key}')
        response = cli.delete_keyset(access_key=key, profile=profile)
        # validate
        assert response is result

    @pytest.mark.parametrize(
        'duration, result', (
            (30, 30), (60, 60), (30 * 24, 720)
            ))
    def test_4_key_age(self, duration, result):
        """
        Calculates human-readable age of a user's access key
        """
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        dt = datetime.timedelta(days=duration)
        create_dt = now - dt
        human, delta_time = vault._key_age(create_dt)
        assert delta_time.days == result
        assert str(duration) in human
