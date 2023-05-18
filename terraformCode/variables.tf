variable "rgname" {
  type = string
  description = "ressource group name"
}

variable "location" {
    type = string
    default = "East US 2"
  
}
variable "service_principal_name" {
  type = string
}

variable "keyvault_name" {
  type = string
}