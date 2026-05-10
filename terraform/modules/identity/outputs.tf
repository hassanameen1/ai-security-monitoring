output "sg_hr_id" {
  value = azuread_group.hr.object_id
}

output "sg_engineering_id" {
  value = azuread_group.engineering.object_id
}

output "sg_all_employees_id" {
  value = azuread_group.all_employees.object_id
}
