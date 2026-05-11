output "workspace_id" {
  value = azurerm_log_analytics_workspace.law.id
}

output "workspace_customer_id" {
  value = azurerm_log_analytics_workspace.law.workspace_id
}

output "dce_ingestion_endpoint" {
  value = azurerm_monitor_data_collection_endpoint.dce.logs_ingestion_endpoint
}

output "dcr_immutable_id" {
  value = azurerm_monitor_data_collection_rule.dcr.immutable_id
}

output "stream_name" {
  value = "Custom-${var.table_name}"
}

output "table_name" {
  value = var.table_name
}
