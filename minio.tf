terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

# 🧠 Common Docker Network for All Containers
resource "docker_network" "minio_net" {
  name = "minio_net"
}

# 🔐 MinIO Server with KMS support
resource "docker_image" "minio" {
  name         = "minio/minio:latest"
  keep_locally = false
}

resource "docker_container" "minio" {
  name  = "minio-server"
  image = docker_image.minio.name

  ports {
    internal = 9000
    external = 9000
  }

  ports {
    internal = 9001
    external = 9001
  }

  env = [
    "MINIO_ROOT_USER=minioadmin",
    "MINIO_ROOT_PASSWORD=minioadmin",
    "MINIO_KMS_SECRET_KEY=mykey:MzJieXRlc2xvbmdzZWNyZXRrZXltdXN0YmVleGFjdCE="
  ]

  command = [
    "server", "/data", "--console-address", ":9001"
  ]

  volumes {
    container_path = "/data"
    host_path      = "/opt/minio-data"
  }

  networks_advanced {
    name = docker_network.minio_net.name
  }
}

# 📦 Session App
resource "docker_image" "session_app" {
  name         = "minio-session-app"
  build {
    context = "./minio-session-app"
  }
  keep_locally = false
}

resource "docker_container" "session_app" {
  name  = "session-app"
  image = docker_image.session_app.name

  ports {
    internal = 5000
    external = 5000
  }

  env = [
    "MINIO_ENDPOINT=http://minio-server:9000",
    "MINIO_ACCESS_KEY=minioadmin",
    "MINIO_SECRET_KEY=minioadmin",
    "MINIO_BUCKET=session-data"
  ]

  networks_advanced {
    name = docker_network.minio_net.name
  }
}

# 📁 Upload App
resource "docker_image" "upload_app" {
  name         = "file-upload-app"
  build {
    context = "./file-upload-app"
  }
  keep_locally = false
}

resource "docker_container" "upload_app" {
  name  = "upload-app"
  image = docker_image.upload_app.name

  ports {
    internal = 5001
    external = 5001
  }

  env = [
    "MINIO_ENDPOINT=http://minio-server:9000",
    "MINIO_ACCESS_KEY=minioadmin",
    "MINIO_SECRET_KEY=minioadmin",
    "MINIO_BUCKET=uploads"
  ]

  networks_advanced {
    name = docker_network.minio_net.name
  }
}

