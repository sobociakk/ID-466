# ID-466

ESPAR BLE - Moduł Akwizycji i Normalizacji Danych (Faza 1)

Opis obecnego etapu
Zakończono budowę podstawowego silnika komunikacyjnego w języku Python, służącego do integracji z systemem anten ESPAR poprzez protokół Telnet. Skrypt pełni rolę stabilnego odbiornika strumienia danych z tagów BLE (Beaconów), stanowiąc fundament dla systemu lokalizacji wewnątrzbudynkowej (Indoor Positioning) opartej na metodzie Fingerprintingu (wzorców radiowych).

Zaimplementowane funkcje (Features)

Odporny klient sieciowy (Defensive Programming): Stabilne połączenie TCP z serwerem urządzenia, automatyczne inicjowanie transmisji, bezpieczne zamykanie portów oraz ignorowanie uszkodzonych/uciętych ramek sieciowych (obsługa błędów formatu JSON).

Ekstrakcja i parsowanie danych: Dekodowanie informacji o aktywnych elementach pasożytniczych anteny (charakterystykach), numerach beaconów oraz wartościach sygnału.

Interaktywne menu (CLI): Prosty interfejs konsolowy pozwalający na wybór trybu pracy bez konieczności ingerencji w kod.

Tryb Podglądu Live: Monitorowanie surowego strumienia z automatyczną detekcją i wizualnym oddzielaniem momentów obrotu wiązki głównej anteny ESPAR.

Tryb Tworzenia Odcisku Palca (Fingerprinting - Wersja Beta):

Uśrednianie sygnału: Automatyczne grupowanie odczytów dla każdego z 12 kierunków i obliczanie średniej wartości RSSI (niwelowanie packet-lossu i szumu radiowego).

Normalizacja (Min-Max): Skalowanie ostatecznego wektora sygnału do przedziału 0.0 - 1.0, co uniezależnia system od wahań mocy nadajników oraz różnic sprzętowych (zgodnie z założeniami z artykułów naukowych).

Architektura kodu
Projekt został podzielony na moduły dla zachowania czystości i skalowalności:

espar_core.py - Maszynownia systemu: funkcje parsujące oraz generator (taśmociąg) strumienia danych.

main.py - Logika interfejsu użytkownika, zarządzanie połączeniem sieciowym i matematyczna obróbka wektorów.

Co dalej? (Roadmap)
Obecnie program przetwarza dane w pamięci RAM. Kolejne kroki obejmują domknięcie architektury systemu lokalizacji:

[ ] Zakończenie Fazy Offline: Dodanie mechanizmu zapytania o koordynaty (X, Y) i zapis znormalizowanych wektorów RSSI do trwałej bazy danych radio_mapa.csv.

[ ] Budowa Fazy Online: Implementacja algorytmu k-Nearest Neighbors (k-NN) do obliczania odległości euklidesowej i estymacji pozycji obiektu w czasie rzeczywistym.
