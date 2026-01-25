# 📈 Personal Wealth Tracker – Cloud-Based Financial Analytics

## 📝 Opis projektu
Projekt polega na stworzeniu i wdrożeniu autorskiej aplikacji webowej do monitorowania portfela inwestycyjnego w czasie rzeczywistym. System integruje się z zewnętrznymi API finansowymi, dostarczając precyzyjnych danych analitycznych. Kluczowym elementem projektu było wykorzystanie podejścia **Infrastructure as Code (IaC)** do pełnej automatyzacji procesu wdrażania na platformie **Google Cloud Platform (GCP)**.

**Główne filary projektu:**
* **Automatyzacja infrastruktury (Terraform)**: Definicja i aprowizacja zasobów chmurowych (Compute Engine, sieci VPC, reguły Firewall) na GCP.
* **Automatyzacja konfiguracji (Ansible)**: Przygotowanie serwera "od zera", instalacja zależności systemowych, konfiguracja środowisk Python (`venv`) oraz wdrożenie kodu aplikacji.
* **System autoryzacji i bezpieczeństwa**: Bezpieczne logowanie z szyfrowaniem haseł (hashing) i zarządzaniem sesjami (Flask-Login).
* **Dynamiczna analityka danych**: Integracja z `yfinance` oraz przetwarzanie danych w `Pandas` w celu generowania wykresów historycznych (Chart.js).

---

## 🛠 Technologie
* **Chmura**: Google Cloud Platform (GCP)
* **IaC & Automatyzacja**: Terraform, Ansible
* **Backend**: Python (Flask), SQLAlchemy (SQLite)
* **Data Science**: Pandas, yfinance
* **Frontend**: Bootstrap 5, Chart.js
* **System**: Ubuntu Linux



---

## 🎓 Zdobyte umiejętności i doświadczenie

### Infrastructure & DevOps
* **Infrastructure as Code (IaC)**: Praktyczne zastosowanie **Terraform** do zarządzania cyklem życia zasobów w chmurze publicznej, zapewniające pełną powtarzalność środowiska.
* **Zarządzanie konfiguracją**: Wykorzystanie **Ansible** do automatyzacji zadań administracyjnych, zarządzania pakietami systemowymi i automatycznego wdrażania aplikacji na zdalne instancje.
* **Architektura Cloud-Native**: Projektowanie i zabezpieczanie sieci wewnątrz chmury (VPC, reguły firewall ograniczające ruch do niezbędnego minimum).

### Software Engineering
* **Integracja z API**: Obsługa asynchronicznego pobierania danych finansowych w czasie rzeczywistym oraz obsługa błędów i braków w danych rynkowych.
* **Bezpieczeństwo**: Implementacja standardów bezpieczeństwa w aplikacjach webowych, w tym hashowanie haseł (Werkzeug) i ochrona sesji użytkownika.
* **Data Processing**: Wykorzystanie biblioteki **Pandas** do czyszczenia, transformacji i normalizacji surowych danych finansowych przed ich wizualizacją.

---

