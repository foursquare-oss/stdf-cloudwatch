data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

resource "aws_lambda_function" "alarmer_lambda" {
  filename         = "${path.module}/lambda.zip"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  function_name    = "cloudwatch-stdf-${var.name}-function"
  description      = "Converts alerts from CloudWatch subscription filter into STDF and publishes to alarm SNS"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.7"
  role             = aws_iam_role.alarmer_role.arn
  environment {
    variables = {
      SNS_TOPIC = var.sns_topic
      SOURCE_REGION = data.aws_region.current.name
      SOURCE_ACCOUNT_NUMBER = data.aws_caller_identity.current.account_id
      MESSAGE_TITLE = var.message_title
      MESSAGE_DESCRIPTION = var.message_description
      APP_NAME = var.app_name
    }
  }
  timeout     = 10
  memory_size = 128
}

data "aws_iam_policy" "basic_execution_role_policy" {
  arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "basic_execution_role_policy" {
  role       = aws_iam_role.alarmer_role.name
  policy_arn = data.aws_iam_policy.basic_execution_role_policy.arn
}

data "aws_iam_policy_document" "alarmer_role" {
  version = "2012-10-17"
  statement {
    actions = [
      "sts:AssumeRole",
    ]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
      ]
    }
    effect = "Allow"
    sid    = ""
  }
}

resource "aws_iam_role" "alarmer_role" {
  name = "cloudwatch-stdf-${var.name}-alarmer_role"

  assume_role_policy = data.aws_iam_policy_document.alarmer_role.json
}

data "aws_iam_policy_document" "alarmer_policy" {
  version = "2012-10-17"

  statement {
    sid    = "postToSecuritySns"
    effect = "Allow"
    actions = [
      "sns:Publish",
    ]
    resources = [
      var.sns_topic,
    ]
  }
}

resource "aws_iam_policy" "alarmer_policy" {
  name = "cloudwatch-stdf-${var.name}-alarmer_policy"

  policy = data.aws_iam_policy_document.alarmer_policy.json
}

resource "aws_iam_role_policy_attachment" "alarmer_policy" {
  role       = aws_iam_role.alarmer_role.name
  policy_arn = aws_iam_policy.alarmer_policy.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.alarmer_lambda.arn
  principal     = "logs.${data.aws_region.current.name}.amazonaws.com"
}

resource "aws_cloudwatch_metric_alarm" "error_alarm" {
  alarm_name          = "cloudwatch-stdf-${var.name}-error-alarm"
  alarm_description   = "The cloudwatch-stdf-${var.name} lambda failed"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  dimensions = {
    FunctionName = aws_lambda_function.alarmer_lambda.function_name
  }
  threshold                 = "1"
  period                    = "60"
  statistic                 = "Sum"
  treat_missing_data        = "missing" # Recocks the alarm after a failure so it triggers again on the next failure
  insufficient_data_actions = []
  alarm_actions             = [var.sns_topic]
}

