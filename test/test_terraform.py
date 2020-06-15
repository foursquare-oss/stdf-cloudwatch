import os
import unittest
import json
import terraform_validate


class TestTerraformConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        return super().tearDownClass()

    def setUp(self):
        self.validator = terraform_validate.Validator(self.path)
        self.validator.error_if_property_missing()
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def get_resources_by_type_and_name(self, resource_type, resource_name):
        all_of_type = self.validator.resources(resource_type)
        resources = terraform_validate.TerraformResourceList(all_of_type.validator, all_of_type.resource_types, {})
        for resource in all_of_type.resource_list:
            if resource.name == resource_name:
                resources.resource_list.append(resource)
        return resources

    def assert_resources_match(self, resources, spec):
        for resource_property in spec:
            resources.property(resource_property).should_equal(spec[resource_property])
        return

    def assert_variable(self, variable_name, value):
        self.assertEqual(self.validator.variable(variable_name).value, value)

    def test_aws_lambda_permission(self):
        # Arrange
        expected_resource_type = 'aws_lambda_permission'
        expected_resource_name = 'allow_cloudwatch'
        expected_number_of_resources = 1
        expected_properties = {
            'statement_id': "AllowExecutionFromCloudWatch",
            'action': "lambda:InvokeFunction",
            'function_name': 'aws_lambda_function.alarmer_lambda.arn',
            'principal': "logs.${data.aws_region.current.name}.amazonaws.com",
        }

        # Act
        actual_resources = self.get_resources_by_type_and_name(expected_resource_type, expected_resource_name)

        # Assert
        self.assertEqual(len(actual_resources.resource_list), expected_number_of_resources)
        self.assert_resources_match(actual_resources, expected_properties)

    def test_lambda_function(self):
        # Arrange
        expected_resource_type = 'aws_lambda_function'
        expected_resource_name = 'alarmer_lambda'
        expected_number_of_resources = 1

        expected_environment = {
            'variables': {
                'SNS_TOPIC': 'var.sns_topic',
                'SOURCE_REGION': 'data.aws_region.current.name',
                'SOURCE_ACCOUNT_NUMBER': 'data.aws_caller_identity.current.account_id',
                'MESSAGE_TITLE': 'var.message_title',
                'MESSAGE_DESCRIPTION': 'var.message_description',
                'APP_NAME': 'var.app_name'
            }
        }

        expected_properties = {
            'filename': '${path.module}/lambda.zip',
            'source_code_hash': 'data.archive_file.lambda_zip.output_base64sha256',
            'function_name': 'cloudwatch-stdf-${var.name}-function',
            'description': 'Converts alerts from CloudWatch subscription filter into STDF and publishes to alarm SNS',
            'handler': 'lambda_function.lambda_handler',
            'runtime': 'python3.7',
            'role': 'aws_iam_role.alarmer_role.arn',
            'environment': expected_environment,
            'timeout': 10,
            'memory_size': 128
        }

        # Act
        actual_resources = self.get_resources_by_type_and_name(expected_resource_type, expected_resource_name)

        # Assert
        self.assertEqual(len(actual_resources.resource_list), expected_number_of_resources)
        self.assert_resources_match(actual_resources, expected_properties)
