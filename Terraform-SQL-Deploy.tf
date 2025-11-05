# terraform-sql-deploy.tf
# Zero-touch Azure SQL + pgvector

provider "azurerm" { features {} }

resource "azurerm_resource_group" "aiops" {
  name     = "rg-aiops-aaron"
  location = "East US"
}

resource "azurerm_sql_server" "main" {
  name                         = "sql-aiops-aaron"
  resource_group_name          = azurerm_resource_group.aiops.name
  location                     = azurerm_resource_group.aiops.location
  version                      = "12.0"
  administrator_login          = "aaronadmin"
  administrator_login_password = "P@ssw0rd123!"
}

resource "azurerm_sql_database" "app" {
  name                = "appdb"
  resource_group_name = azurerm_resource_group.aiops.name
  location            = azurerm_resource_group.aiops.location
  server_name         = azurerm_sql_server.main.name
}