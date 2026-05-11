output "openai_endpoint" {
  value = module.openai.endpoint
}

output "openai_deployment_name" {
  value = module.openai.deployment_name
}

output "openai_primary_key" {
  value     = module.openai.primary_key
  sensitive = true
}

output "sg_hr_id" {
  value = module.identity.sg_hr_id
}

output "sg_engineering_id" {
  value = module.identity.sg_engineering_id
}

output "sg_all_employees_id" {
  value = module.identity.sg_all_employees_id
}

output "law_workspace_customer_id" {
  value = module.loganalytics.workspace_customer_id
}

output "dce_ingestion_endpoint" {
  value = module.loganalytics.dce_ingestion_endpoint
}

output "dcr_immutable_id" {
  value = module.loganalytics.dcr_immutable_id
}

output "stream_name" {
  value = module.loganalytics.stream_name
}
