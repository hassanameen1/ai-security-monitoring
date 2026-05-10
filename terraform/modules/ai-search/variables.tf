variable "name" {
  description = "search service name"
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

variable "sku" {
  description = "pricing tier"
  type        = string
  default     = "free"
}

variable "tags" {
  description = "tags"
  type        = map(string)
  default     = {}
}
