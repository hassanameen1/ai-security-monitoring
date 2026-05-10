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
