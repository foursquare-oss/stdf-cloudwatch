variable "name" {
  description = "the root name that all resource names are based on"
}

variable "sns_topic" {
  description = "topic arn of the security SNS"
}

variable "message_title" {
  description = "title of the message"
}

variable "message_description" {
  description = "description of the message"
}

variable "app_name" {
  description = "the app which generated the message"
}
