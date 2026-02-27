# ID-466

ESPAR BLE - Moduł Akwizycji i Normalizacji Danych

Opis obecnego etapu:

Zakończono budowę podstawowego silnika komunikacyjnego w języku Python, służącego do integracji z systemem anten ESPAR poprzez protokół Telnet. Skrypt pełni rolę stabilnego odbiornika strumienia danych z tagów BLE (Beaconów), stanowiąc fundament dla systemu lokalizacji wewnątrzbudynkowej (Indoor Positioning) opartej na metodzie Fingerprintingu.

Zaimplementowane funkcje:

- Stabilne połączenie TCP z serwerem urządzenia, automatyczne inicjowanie transmisji, bezpieczne zamykanie portów oraz ignorowanie uszkodzonych/uciętych ramek sieciowych (obsługa błędów formatu JSON).
- Ekstrakcja i parsowanie danych: Dekodowanie informacji o aktywnych elementach pasożytniczych anteny (charakterystykach), numerach beaconów oraz wartościach sygnału.
- Prosty interfejs konsolowy pozwalający na wybór trybu pracy bez konieczności ingerencji w kod.
- Tryb Podglądu Live: Monitorowanie surowego strumienia z automatyczną detekcją i wizualnym oddzielaniem momentów obrotu wiązki głównej anteny ESPAR.

Tryb Tworzenia Odcisku (Fingerprinting - Wersja Beta):
- Uśrednianie sygnału: Automatyczne grupowanie odczytów dla każdego z 12 kierunków i obliczanie średniej wartości RSSI (niwelowanie packet-lossu i szumu radiowego).
- Normalizacja (Min-Max): Skalowanie ostatecznego wektora sygnału do przedziału 0.0 - 1.0, co uniezależnia system od wahań mocy nadajników oraz różnic sprzętowych (zgodnie z założeniami z artykułów naukowych).

Architektura kodu:

- telnet_reader.py - funkcje parsujące oraz generator strumienia danych

- main.py - logika interfejsu użytkownika, zarządzanie połączeniem sieciowym i matematyczna obróbka wektorów
