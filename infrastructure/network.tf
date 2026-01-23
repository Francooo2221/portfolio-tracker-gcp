resource "google_compute_network" "vpc_network" {
  name                    = "portfolio-vpc"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "allow_ssh_app" {
  name    = "allow-ssh-and-app"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22", "8501"]
  }

  source_ranges = ["0.0.0.0/0"]
}
