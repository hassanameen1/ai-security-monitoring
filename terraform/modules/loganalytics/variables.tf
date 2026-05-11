variable "location" {
  description = "resource region"
  type        = string
}

variable "resource_group_name" {
  description = "rg to deploy into"
  type        = string
}

variable "workspace_name" {
  description = "law name"
  type        = string
}

variable "dce_name" {
  description = "data collection endpoint name"
  type        = string
}

variable "dcr_name" {
  description = "data collection rule name"
  type        = string
}

variable "table_name" {
  description = "custom log table name (must end in _CL)"
  type        = string
  default     = "AIInteractions_CL"
}

variable "writer_principal_id" {
  description = "object id granted Monitoring Metrics Publisher on the dcr"
  type        = string
}

variable "tags" {
  description = "resource tags"
  type        = map(string)
  default     = {}
}
