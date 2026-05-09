variable "name" {
  description = "openai resource name"
  type        = string
}

variable "location" {
  description = "azure region"
  type        = string
}

variable "resource_group_name" {
  description = "rg name"
  type        = string
}

variable "deployment_name" {
  description = "model deployment name"
  type        = string
  default     = "gpt-4o-mini"
}

variable "model_name" {
  description = "openai model"
  type        = string
  default     = "gpt-4o-mini"
}

variable "model_version" {
  description = "openai model version"
  type        = string
  default     = "2024-07-18"
}

variable "deployment_capacity" {
  description = "tpm capacity (in thousands)"
  type        = number
  default     = 30
}

variable "tags" {
  description = "tags"
  type        = map(string)
  default     = {}
}
