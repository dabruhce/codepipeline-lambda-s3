# codepipeline-lambda-s3
An AWS Lambda function to go in your AWS CodePipeline and upload artifacts, you might use this
if you want your CodePipeline to actually deploy code to Lambda.

## Instructions
### Setup the lambda function
Copy the source code in index.py into another Lambda function.

For lambda Configuration I have:

* Runtime: Python 2.7
* Handler: lambda_function.lambda_handler
* Role: CodePipelineLambdaExecRole

Where CodePipelineLambdaExecRole has had  the following policy
added to the defaults that CodePipeline sets up for you.

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "UpdateAnyLambdaFunction",
            "Effect": "Allow",
            "Action": [
                "lambda:UpdateFunctionCode"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
### Tell CodePipeline to use it.
This should be pretty self explanatory in the CodePipeline UI.

The main things to remember are:
1. Give it one and only one input artifact.
2. Set the name of the function that you want to update as the user parameters.
