resource "google_compute_instance" "vm_instance" {
  name         = "portfolio-tracker-vm"
  machine_type = var.machine_type

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 20 # Rozmiar dysku w GB
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
      // Ephemeral IP
    }
  }
}