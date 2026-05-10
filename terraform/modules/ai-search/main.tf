resource "azurerm_search_service" "this" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.sku
  replica_count       = 1
  partition_count     = 1

  local_authentication_enabled = true
  authentication_failure_mode  = "http403"

  tags = var.tags
}
