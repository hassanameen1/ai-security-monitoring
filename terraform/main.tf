provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  subscription_id = var.subscription_id
}

locals {
  tags = {
    project     = "ai-security-monitoring"
    environment = "prod"
    managed_by  = "terraform"
  }
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.tags
}

module "openai" {
  source              = "./modules/openai"
  name                = var.openai_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

module "search" {
  source              = "./modules/ai-search"
  name                = var.search_name
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

module "identity" {
  source = "./modules/identity"
}

data "azurerm_client_config" "current" {}

module "loganalytics" {
  source              = "./modules/loganalytics"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_name      = var.law_name
  dce_name            = var.dce_name
  dcr_name            = var.dcr_name
  writer_principal_id = data.azurerm_client_config.current.object_id
  tags                = local.tags
}
