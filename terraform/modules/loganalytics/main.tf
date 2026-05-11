resource "azurerm_log_analytics_workspace" "law" {
  name                = var.workspace_name
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_sentinel_log_analytics_workspace_onboarding" "sentinel" {
  workspace_id = azurerm_log_analytics_workspace.law.id
}

resource "azapi_resource" "ai_interactions_table" {
  type      = "Microsoft.OperationalInsights/workspaces/tables@2022-10-01"
  parent_id = azurerm_log_analytics_workspace.law.id
  name      = var.table_name

  body = {
    properties = {
      schema = {
        name = var.table_name
        columns = [
          { name = "TimeGenerated", type = "datetime" },
          { name = "session_id", type = "string" },
          { name = "user_id", type = "string" },
          { name = "user_groups", type = "dynamic" },
          { name = "prompt", type = "string" },
          { name = "response", type = "string" },
          { name = "sources", type = "dynamic" },
          { name = "tool_calls", type = "dynamic" },
          { name = "latency_ms", type = "int" },
          { name = "prompt_tokens", type = "int" },
          { name = "completion_tokens", type = "int" },
          { name = "prompt_shield_verdict", type = "string" },
          { name = "prompt_shield_categories", type = "dynamic" },
          { name = "output_eval_verdict", type = "string" },
          { name = "output_eval_findings", type = "dynamic" },
          { name = "blocked_reason", type = "string" },
        ]
      }
      retentionInDays      = 30
      totalRetentionInDays = 30
    }
  }
}

resource "azurerm_monitor_data_collection_endpoint" "dce" {
  name                = var.dce_name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "Linux"
  tags                = var.tags
}

resource "azurerm_monitor_data_collection_rule" "dcr" {
  name                        = var.dcr_name
  location                    = var.location
  resource_group_name         = var.resource_group_name
  data_collection_endpoint_id = azurerm_monitor_data_collection_endpoint.dce.id
  tags                        = var.tags

  destinations {
    log_analytics {
      workspace_resource_id = azurerm_log_analytics_workspace.law.id
      name                  = "law-dest"
    }
  }

  data_flow {
    streams       = ["Custom-${var.table_name}"]
    destinations  = ["law-dest"]
    output_stream = "Custom-${var.table_name}"
    transform_kql = "source"
  }

  stream_declaration {
    stream_name = "Custom-${var.table_name}"

    column {
      name = "TimeGenerated"
      type = "datetime"
    }
    column {
      name = "session_id"
      type = "string"
    }
    column {
      name = "user_id"
      type = "string"
    }
    column {
      name = "user_groups"
      type = "dynamic"
    }
    column {
      name = "prompt"
      type = "string"
    }
    column {
      name = "response"
      type = "string"
    }
    column {
      name = "sources"
      type = "dynamic"
    }
    column {
      name = "tool_calls"
      type = "dynamic"
    }
    column {
      name = "latency_ms"
      type = "int"
    }
    column {
      name = "prompt_tokens"
      type = "int"
    }
    column {
      name = "completion_tokens"
      type = "int"
    }
    column {
      name = "prompt_shield_verdict"
      type = "string"
    }
    column {
      name = "prompt_shield_categories"
      type = "dynamic"
    }
    column {
      name = "output_eval_verdict"
      type = "string"
    }
    column {
      name = "output_eval_findings"
      type = "dynamic"
    }
    column {
      name = "blocked_reason"
      type = "string"
    }
  }

  depends_on = [azapi_resource.ai_interactions_table]
}

resource "azurerm_role_assignment" "dcr_writer" {
  scope                = azurerm_monitor_data_collection_rule.dcr.id
  role_definition_name = "Monitoring Metrics Publisher"
  principal_id         = var.writer_principal_id
}
