import os
import unittest.mock
import importlib
import json

lambdafn = importlib.import_module('lambda.lambda_function')

class TestPostToSns(unittest.TestCase):
    def setUp(self):
        importlib.reload(lambdafn)

    @unittest.mock.patch('lambda.lambda_function.boto3.client')
    def test_post_to_sns(self, mock_boto3_client):
        # Arrange
        expected_service_name = 'sns'
        expected_stdf_message = {'foo': 'bar'}
        expected_sns_topic = 'topic_name'
        expected_dumped_json = json.dumps(expected_stdf_message)

        mock_sns_client = mock_boto3_client.return_value

        # Act
        lambdafn.post_to_sns(expected_stdf_message, expected_sns_topic)

        # Assert
        mock_boto3_client.assert_called_once_with(expected_service_name)
        mock_sns_client.publish.assert_called_once_with(
            TopicArn=expected_sns_topic,
            Subject='stdfMessage',
            Message=expected_dumped_json
        )


class TestExtractLogEvents(unittest.TestCase):
    def setUp(self):
        importlib.reload(lambdafn)

    def test_extract_log_events(self):
        # Arrange
        expected_event = {"awslogs": {"data": "H4sIAAAAAAAAAI1U227bOBT8lUDPkSyKom5vqq0mburCiNwUSBwEtMQ4RCXRJak1vIH/fY8oyfbuFm1ffDlnOHMuQ75bNVOKbtnqsGNWYs3SVfqyyPI8vcmsa0vsGyYhHHhR5Po4DiPfg3AltjdStDvITCvRlitJeTVZ0AaIatbo7C/4UD0w15LR+j8cL+djL62yGVXaRoBX7UYVku80F81HXmkmlZU8WQrbtOhiyq5Fw7WQ9iXSejZKg2ry9G7xEgSxH0c+cnFIYhd7ge/GBKEIY+JFoRfFLsF+EHuIRCFCJMQuQSEO4CfUoTmMRdMaOkQkiEIf+UEY+8H1OC6gf19brFN8gCKhiLWVrC3kuGRtXa+tVjE5LyHL9QEygNUwYIOZp4uvkDWwneRNwXe0mpcml85n6WP2SD49LD4t8er2yzTAmUFS2SvAd0L3KuG0TpLLkSad5ITKA+3xRSHaRg+8l8AxDY3cscMofDc/CX+++/Y19PyHUyNfaM0G8Y79eD10vuJD3HNRbLuxjcIVChMUJSR+NKcNLBetLHqgwg6t6d+igRacQtRn0Elj2eoPbfGd6aWoeHHoq92re7Ydh3wyjMkpwz5fpmUpoaWhnthBxHUIchA+LyTdgpABPH0QWuAJcgAXu1fLg34TzQQ7oYOvZlTueTNBkRM47lUHLIRkgEVeB342dJL9aMEhSyqh7s6m/ZI3pvJTL776YStWtBJcYP/ExBooDN3mXx13TJeugvF6NnJhvAaca6rNNVt3Xof/vN/hamTLXl9Z0TeaVpXYm+BytFrPn37Lf+MnKYTul52asocFJp+5GjZkeO+ZOu93ZANYkvxZ98fnTuJNKNPOn83M+b+PnrvbNM4PaCByNHtSOzjNsspMrFtT01ZV56my5B0zrcy7MaOa9pPJ+bahupXscgUQfPBNv1O+e2Myb7nuW86ms9vMvs9TO81y5EX2zXRh57epRwKDT1v91r0DBe3UFgycNlw5SNwyWnZPwfFsqfnMZMP4I4HHyQ2mJEN+HJ9vygDwyvKVeDSyQx9j20cktjeUUDtgkRtGKCKYbc6HVuPrk+5VuuNTWlWDj8ETHADpL96LY7ekfwDz2nAKKgYAAA=="}}
        expected_data = [{'id': '34984103759032640951183352872890534692158711573051736115', 'timestamp': 1568741467946, 'message': '{"eventVersion":"1.05","userIdentity":{"type":"IAMUser","principalId":"AIDAZEZ5JVMJP3THNC63E","arn":"arn:aws:iam::628804397842:user/arya","accountId":"628804397842","accessKeyId":"AKIAZEZ5JVMJLKWU724V","userName":"arya"},"eventTime":"2019-09-17T17:18:59Z","eventSource":"s3.amazonaws.com","eventName":"PutBucketPolicy","awsRegion":"us-east-1","sourceIPAddress":"209.150.51.135","userAgent":"[Boto3/1.9.190 Python/3.7.3 Darwin/18.6.0 Botocore/1.12.190]","requestParameters":{"bucketName":"4sq-security-s3-actions-monitor-test","bucketPolicy":{"Version":"2012-10-17","Statement":[{"Sid":"Test","Effect":"Allow","Principal":{"AWS":"arn:aws:iam::628804397842:root"},"Action":"s3:ListBucket","Resource":"arn:aws:s3:::4sq-security-s3-actions-monitor-test"}]},"host":["4sq-security-s3-actions-monitor-test.s3.amazonaws.com"],"policy":[""]},"responseElements":null,"additionalEventData":{"SignatureVersion":"SigV4","CipherSuite":"ECDHE-RSA-AES128-GCM-SHA256","AuthenticationMethod":"AuthHeader"},"requestID":"79F592106C5E1499","eventID":"2ddf52a8-7433-4159-ba5a-6e80781853eb","eventType":"AwsApiCall","recipientAccountId":"628804397842"}'}]
        # Act
        actual_data = lambdafn.extract_log_events(expected_event)

        # Assert
        self.assertEqual(expected_data, actual_data)

class TestFormatToStdf(unittest.TestCase):
    def setUp(self):
        importlib.reload(lambdafn)

    def test_format_to_stdf(self):
        # Arrange
        expected_id = '34984103759032640951183352872890534692158711573051736115'
        expected_timestamp_milliseconds = 1568741467946
        expected_log_line = '2020-03-01 14:09:06 DEBUG SQL:92 - select engageenti0_.id as id1_77_0_, engageenti0_.enabled as enabled2_77_0_ from engage engageenti0_ where engageenti0_.id=?'

        expected_single_event = {
            'id': expected_id,
            'timestamp': expected_timestamp_milliseconds,
            'message': expected_log_line
        }

        expected_service_name = 'CloudWatch'
        expected_provider = 'AWS'

        expected_account_id = '906911110000'
        expected_region = 'us-east-9000'
        expected_title = 'Security Alert'
        expected_description = 'Something happened'
        expected_app_name = 'Jamf'

        os.environ['SOURCE_ACCOUNT_NUMBER'] = expected_account_id
        os.environ['MESSAGE_TITLE'] = expected_title
        os.environ['MESSAGE_DESCRIPTION'] = expected_description
        os.environ['SOURCE_REGION'] = expected_region
        os.environ['APP_NAME'] = expected_app_name

        expected_message_json = {
            'payload': {
                'title': expected_title,
                'description': expected_description,
                'raw_data': expected_log_line
            },
            'meta': {
                'timestamp': expected_timestamp_milliseconds,
                'source': {
                    'provider': expected_provider,
                    'account_id': expected_account_id,
                    'region': expected_region,
                    'service': expected_service_name,
                    'event_id': expected_id,
                    'app_name': expected_app_name
                },
            },
            'stdf_version': 2,
        }

        # Act
        actual_message_json = lambdafn.format_to_stdf(expected_single_event)

        # Assert
        self.maxDiff = None
        self.assertEqual(expected_message_json, actual_message_json)
