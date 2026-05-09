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
