provider "azurerm" {
  features {
     
  }
}

resource "azurerm_resource_group" "rg1" {
  name     = var.rgname
  location = var.location
}

module "ServicePrincipal" {
  source = "./modules/ServicePrincipal"
  service_principal_name = var.service_principal_name
  
  depends_on = [ 
    azurerm_resource_group.rg1
   ]
}


resource "azurerm_role_assignment" "rolePanoptic" {

  scope                = "/subscriptions/e11d97b1-1116-4846-adbe-62819df517db/"
  role_definition_name = "Contributor"
  principal_id         = module.ServicePrincipal.service_principal_object_id

  depends_on = [
    module.ServicePrincipal
  ]
}

module "keyvault" {
  source                      = "./modules/keyvault"
  keyvault_name               = var.keyvault_name
  location                    = var.location
  resource_group_name         = var.rgname
  service_principal_name      = var.service_principal_name
  service_principal_object_id = module.ServicePrincipal.service_principal_object_id
  service_principal_tenant_id = module.ServicePrincipal.service_principal_tenant_id

  depends_on = [
    module.ServicePrincipal
  ]
}

resource "azurerm_key_vault_secret" "example" {
  name         = module.ServicePrincipal.client_id  //bech yemchi ychouf fi output.tf
  value        = module.ServicePrincipal.client_secret
  key_vault_id = module.keyvault.keyvault_id

  depends_on = [
    module.keyvault
  ]
}

provider "kubernetes" {
  config_path = "~/.kube/config"  # Path to your kubeconfig file
}

locals {
  folder_path = "/home/pc/Documents/BindMounting/Input/S2-2017-T31TFM-meanstd.pkl"
}

data "local_file" "folder_contents" {
  filename = local.folder_path
  
}

resource "kubernetes_config_map" "my_config_mapnew" {
  metadata {
    name = "my-confignew"
  }

  data = {
    folder_contents = data.local_file.folder_contents.content
  }
}

module "aks" {
  source = "./modules/aks"
  service_principal_name = var.service_principal_name
  client_id = module.ServicePrincipal.client_id
  client_secret = module.ServicePrincipal.client_secret
  location = var.location
  resource_group_name = var.rgname

  depends_on = [ 
    module.ServicePrincipal
   ]

}