import unittest

import index


class TestIndex(unittest.TestCase):

    def test_get_input_artifact(self):
        bucket = 'foo'
        key = 'bar'
        artifacts = [{
                    'name': 'mything',
                    'location': {
                        'type': 'S3',
                        's3Location': {
                            'bucketName': 'foo',
                            'objectKey': 'bar'}
                        }
                    }
                ]
        actual = index.get_input_artifact(artifacts)
        self.assertEqual(actual['Bucket'], bucket)
        self.assertEqual(actual['Key'], key)

    def test_multiple_input_artifacts(self):
        artifacts = [{}, {}]
        with self.assertRaises(ValueError) as context:
            index.get_input_artifact(artifacts)
        self.assertTrue(
            'Expected one and only one' in context.exception.message)
        self.assertTrue(
            'input artifact, got [{}, {}]' in context.exception.message)

    def test_no_input_artifacts(self):
        artifacts = []
        with self.assertRaises(ValueError) as context:
            index.get_input_artifact(artifacts)
        self.assertTrue(
            'Expected one and only one' in context.exception.message)
        self.assertTrue(
            'input artifact, got []' in context.exception.message)

    def test_parse_job_data(self):
        func = 'myLambdaFunction'
        config = {'UserParameters': func}
        job_data = {'artifactCredentials': {},
                    'inputArtifacts': [],
                    'actionConfiguration': {
                        'configuration': config}
                    }
        creds, inputs, function = index.parse_job_data(job_data)
        self.assertEqual(creds, {})
        self.assertEqual(inputs, [])
        self.assertEqual(function, func)

    def test_parse_job_data_without_user_params(self):
        job_data = {'artifactCredentials': {},
                    'inputArtifacts': [],
                    'actionConfiguration': {
                        'configuration': {}}
                    }
        with self.assertRaises(ValueError) as context:
            index.parse_job_data(job_data)
        self.assertEqual(
            context.exception.message,
            'Must be given a Lambda function name in user parameters.')

    def test_parse_job_data_with_blank_function_name(self):
        config = {'UserParameters': ''}
        job_data = {'artifactCredentials': {},
                    'inputArtifacts': [],
                    'actionConfiguration': {
                        'configuration': config}
                    }
        with self.assertRaises(ValueError) as context:
            index.parse_job_data(job_data)
        self.assertEqual(
            context.exception.message,
            'Lambda function name is blank.')
