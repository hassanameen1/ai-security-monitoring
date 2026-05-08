variable "subscription_id" {
  description = "azure subs id to deploy"
  type        = string
}

variable "location" {
  description = "resource region"
  type        = string
  default     = "swedencentral"
}

variable "resource_group_name" {
  description = "the name of the group"
  type        = string
  default     = "rg-ai-security-prod"
}
