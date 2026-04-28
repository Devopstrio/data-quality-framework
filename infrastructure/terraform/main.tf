provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

resource "azurerm_resource_group" "quality" {
  name     = "rg-${var.project_name}-quality-${var.environment}"
  location = var.location
}

# --- Quality Control Plane (AKS) ---

resource "azurerm_kubernetes_cluster" "quality_k8s" {
  name                = "aks-trust-iq-${var.environment}"
  location            = azurerm_resource_group.quality.location
  resource_group_name = azurerm_resource_group.quality.name
  dns_prefix          = "quality-k8s"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }
}

# --- Quality Metadata Store (Postgres) ---

resource "azurerm_postgresql_flexible_server" "metadata" {
  name                   = "psql-quality-metadata-${var.environment}"
  resource_group_name    = azurerm_resource_group.quality.name
  location               = azurerm_resource_group.quality.location
  version                = "13"
  administrator_login    = "dqadmin"
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "GP_Standard_D2ds_v4"
}

# --- Rule Telemetry Cache (Redis) ---

resource "azurerm_redis_cache" "rule_cache" {
  name                = "redis-quality-cache-${var.environment}"
  location            = azurerm_resource_group.quality.location
  resource_group_name = azurerm_resource_group.quality.name
  capacity            = 1
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = false
}

# --- Multi-Cloud Telemetry Archive (S3) ---

resource "aws_s3_bucket" "quality_archive" {
  bucket = "data-quality-archive-${var.environment}"
}
