import boto3
import re
import os
from botocore.exceptions import ClientError

logs_client = boto3.client('logs')


class PrefixSet:
    def __init__(self, string_list):
        self.regexp = re.compile("^(?:" + "|".join(string_list) + ")", re.IGNORECASE)

    def matches(self, search_str):
        return self.regexp.search(search_str) is not None


blacklisted_log_groups = PrefixSet(os.environ["BLACKLISTED_LOG_GROUPS"].split())


def put_subscription_filter(log_group_name, destination_arn, role_arn):
    try:
        logs_client.put_subscription_filter(
            logGroupName=log_group_name,
            filterName="firehose",
            filterPattern='',
            destinationArn=destination_arn,
            roleArn=role_arn
        )
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") != 'ResourceNotFoundException':
            raise e
        print("Log group could not be found: {}".format(log_group_name))


def handler(event, context):
    """Main Lambda function
    """
    log_group_name = event['detail']['requestParameters']['logGroupName']
    account_id = context.invoked_function_arn.split(":")[4]
    delivery_stream_arn = "arn:aws:firehose:us-east-1:{0}:deliverystream/Kinesis-Firehose-ELK".format(account_id)
    cwl_to_kinesis_role_arn = "arn:aws:iam::{0}:role/cwl-firehose".format(account_id)
    if not blacklisted_log_groups.matches(log_group_name):
        print("Subscribing log group {0} to firehose".format(log_group_name))
        put_subscription_filter(log_group_name, delivery_stream_arn, cwl_to_kinesis_role_arn)
    else:
        print("Log group {0} is blacklisted. Not subscribed to firehose".format(log_group_name))
