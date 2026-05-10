resource "azuread_group" "hr" {
  display_name     = "sg-hr"
  mail_nickname    = "sg-hr"
  description      = "ai security demo: HR group"
  security_enabled = true
}

resource "azuread_group" "engineering" {
  display_name     = "sg-engineering"
  mail_nickname    = "sg-engineering"
  description      = "ai security demo: engineering group"
  security_enabled = true
}

resource "azuread_group" "all_employees" {
  display_name     = "sg-all-employees"
  mail_nickname    = "sg-all-employees"
  description      = "ai security demo: all-employees group"
  security_enabled = true
}
