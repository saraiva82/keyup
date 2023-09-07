import os
import platform
import sys
import time
import json
import re
from configparser import ConfigParser
import logging

# aws imports
import boto3
from botocore.exceptions import ClientError, ProfileNotFound

# test imports
import moto
import pytest
import pyaws
from tests import environment
from keyup.statics import PACKAGE
from keyup import cli


# global objects
config = ConfigParser()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# set global Autotag-specific vars
account_number = '123456789012'

# test module globals
base_path = '/tmp/autotag-tests-%s' % time.time()
version = os.path.join('testing-', base_path)
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


@pytest.fixture(scope="function")
def prepare_s3():
    moto.mock_s3().start()
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket='s3-eu-west-1-mpc-test1-pr')
    s3.create_bucket(Bucket='s3-eu-west-1-mpc-test2-pr')
    yield s3


@pytest.fixture(scope="function")
def s3_resource_objects():
    moto.mock_s3().start()
    client = boto3.client('s3')
    rsc = boto3.resource('s3')
    yield client, rsc


@pytest.fixture(scope="function")
def sts_resource_objects(region=default_region):
    moto.mock_sts().start()
    client = boto3.client('sts', region_name=region)
    yield client


@pytest.fixture(scope="function")
def return_reference(filename):
    with open(test_assets + '/' + filename, 'r') as f1:
        content = json.loads(f1.read())
        yield content


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


class TestKeyupSupport():
    def test_zero(self, prepare_s3):
        region = 'eu-west-1'
        s3c = prepare_s3
        buckets = sorted([x['Name'] for x in s3c.list_buckets()['Buckets']])
        expected = [
            's3-{region}-mpc-test1-pr'.format(region=region),
            's3-{region}-mpc-test2-pr'.format(region=region)
        ]
        assert buckets == sorted(expected)

    @pytest.mark.parametrize(
        'profilename, result', (('default', True), ('developer1', True)))
    @moto.mock_sts
    def test_1_authenicated(self, profilename, result, region=default_region):
        """
        authenticated module function, tests generic authentication to AWS
        """
        try:
            r_test = pyaws.session.authenticated(profile=profilename)
        except ProfileNotFound as e:
            logger.info(f'Exception Profile not found ({e})')
            r_test = False
        # compare
        assert r_test is result

    @pytest.mark.parametrize(
        'profilename, result', (
            ('default', True), ('developer1', True), ('gcreds-developer1', False)))
    @moto.mock_sts
    def test_2_authenicated(self, profilename, result, region=default_region):
        """
        authenticated module function, tests generic authentication to AWS
        """
        # presetup if not performed yet
        HOME = os.environ['HOME']
        with open(os.path.join(HOME,'.aws/credentials')) as f1:
            f2 = f1.readlines()
        if '[gcreds-dev1]\n' not in f2:
            expired = import_file_object(os.path.join(test_assets, 'expired-temp-creds.ini'))
            with open(os.path.join(HOME,'.aws/credentials'), 'a') as f1:
                f1.write('\n')
                f1.write(expired)
        try:
            r_test = pyaws.session.authenticated(profile=profilename)
        except ProfileNotFound as e:
            logger.info(f'Exception Profile not found ({e})')
            r_test = False
        # compare
        assert r_test is result

    @pytest.mark.parametrize(
        'os_type', (('Linux', True), ('Windows', True), ('Java', True)))
    @moto.mock_sts
    def test_3_awscli_defaults_credentials(self, os_type):
        """
        random_key generates a random string for obscuring s3 urls

        Parameter Set checks clean_key returned does not contain
        any chars illegal in s3 urls
        """
        sts_dict = pyaws.script_utils.awscli_defaults()

        # platform specific outcome
        if os_type in ('Linux', 'Java'):
            HOME = os.environ['HOME']
            assert sts_dict['awscli_defaults']['awscli_credentials'] == HOME + '/.aws/credentials'
        elif os_type == 'Windows':
            username = os.getenv('username')
            awscli_credentials = 'C:\\Users\\' + username + '\\.aws\\credentials'
            assert sts_dict['awscli_defaults']['awscli_credentials'] == awscli_credentials

    @pytest.mark.parametrize(
        'os_type, result', (
            ('Linux', True), ('Windows', True), ('Java', True)
            ))
    @moto.mock_sts
    def test_4_awscli_defaults_config_file(self, os_type, result):
        """
        random_key generates a random string for obscuring s3 urls

        Parameter Set checks clean_key returned does not contain
        any chars illegal in s3 urls
        """
        sts_dict = pyaws.script_utils.awscli_defaults(os_type)

        # platform specific outcome
        if os_type in ('Linux', 'Java'):
            HOME = os.environ['HOME']
            assert sts_dict['awscli_defaults']['awscli_config'] == HOME + '/.aws/config'
        elif os_type == 'Windows':
            username = os.getenv('username')
            awscli_config = 'C:\\Users\\' + username + '\\.aws\\config'
            assert sts_dict['awscli_defaults']['awscli_config'] == awscli_config


class TestTearDown():
    def test_teardown(self):
        result = tear_down()
        assert result is True
