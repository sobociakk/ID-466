import socket
import time
import json
from espar_core import get_espar_stream

HOST = '153.19.49.102'
PORT = 8893
TIMEOUT = 10

def connect_and_start():
    """Nawiązuje połączenie i wysyła komendę start."""
    print(f"\nŁączenie z {HOST}:{PORT}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.connect((HOST, PORT))
    s.sendall(b'\r\n')
    time.sleep(0.5)
    s.sendall(b'start\r\n')
    print("Połączono! Odbieranie danych...\n")
    return s

def stop_and_close(sock):
    """Kulturalnie zatrzymuje transmisję i zamyka port."""
    try:
        print("\nZatrzymuję transmisję (wysyłam 'stop')...")
        sock.sendall(b'stop\r\n')
        time.sleep(0.5)
    except Exception:
        pass
    sock.close()

def run_live():
    """Tryb 1: Podgląd na żywo ze znacznikami zmiany kierunku."""
    try:
        sock = connect_and_start()
        current_char = None
        print("Naciśnij Ctrl+C, aby zakończyć podgląd.\n")
        
        for frame in get_espar_stream(sock):
            char_int = frame['espar_char_int']
            
            if current_char is not None and char_int != current_char:
                print("-" * 60)
            current_char = char_int
            
            print(f"[{frame['ble_frame_num']:>7}] ESPAR: {frame['map_loc']} | "
                  f"Beacon: {frame['beacon_num']:>2} | RSSI: {frame['rssi_dbm']:>3} dBm | "
                  f"Ch-tyka: {char_int:<4} ({frame['espar_char_bin']})")
                  
    except KeyboardInterrupt:
        print("\n[!] Przerwano podgląd przez użytkownika (Ctrl+C).")
    except socket.timeout:
        print("\n[!] Błąd: Przekroczono czas oczekiwania na dane z serwera.")
    finally:
        stop_and_close(sock)

def run_average():
    """Tryb 2: Zbieranie danych, uśrednianie i NORMALIZACJA RSSI."""
    try:
        sock = connect_and_start()
        current_char = None
        rssi_koszyk = []
        fingerprint = {}
        
        print("Zbieranie i uśrednianie danych... Naciśnij Ctrl+C, aby zakończyć i znormalizować wektor.\n")
        
        for frame in get_espar_stream(sock):
            char_int = frame['espar_char_int']
            rssi = frame['rssi_dbm']
            
            if current_char is not None and char_int != current_char:
                if len(rssi_koszyk) > 0:
                    srednia = sum(rssi_koszyk) / len(rssi_koszyk)
                    fingerprint[current_char] = round(srednia, 2)
                    print(f"Kierunek: {current_char:<4} | Zebrano ramek: {len(rssi_koszyk):<2} | Średnia RSSI: {srednia:.2f} dBm")
                rssi_koszyk = [] 
            
            current_char = char_int
            rssi_koszyk.append(rssi)
            
    except KeyboardInterrupt:
        print("\n\n[!] Zakończono zbieranie pomiarów.")
        
        # Podliczamy ostatni, przerwany koszyk
        if current_char is not None and len(rssi_koszyk) > 0:
            fingerprint[current_char] = round(sum(rssi_koszyk) / len(rssi_koszyk), 2)
            
        # --- NORMALIZACJA RSSI ---
        if fingerprint:
            min_rssi = min(fingerprint.values())
            max_rssi = max(fingerprint.values())
            
            normalized_fingerprint = {}
            
            # Zabezpieczenie przed dzieleniem przez zero (gdyby wszystkie pomiary były identyczne)
            if max_rssi > min_rssi:
                for kierunek, s_rssi in fingerprint.items():
                    norm_val = (s_rssi - min_rssi) / (max_rssi - min_rssi)
                    normalized_fingerprint[kierunek] = round(norm_val, 4)
            else:
                # Jeśli różnica wynosi 0, przypisujemy sztuczne 0.0 do wszystkich (awaria / błąd pomiaru)
                for kierunek in fingerprint.keys():
                    normalized_fingerprint[kierunek] = 0.0
                    
            print("\n--- SUROWY WEKTOR RSSI ---")
            print(json.dumps(fingerprint, indent=4))
            
            print("\n--- ZNORMALIZOWANY ODCISK PALCA (0.0 - 1.0) ---")
            print(json.dumps(normalized_fingerprint, indent=4))
        else:
            print("Nie zebrano wystarczającej ilości danych do utworzenia odcisku palca.")

    except socket.timeout:
        print("\n[!] Błąd: Przekroczono czas oczekiwania na dane z serwera.")
    finally:
        stop_and_close(sock)

if __name__ == '__main__':
    while True:
        print("\n=== SYSTEM LOKALIZACJI ESPAR ===")
        print("1 - Podgląd na żywo (strumień z oddzielaniem)")
        print("2 - Tworzenie odcisku palca (Uśrednianie + Normalizacja RSSI)")
        print("3 - Wyjście")
        
        wybor = input("Wybierz tryb (1/2/3): ").strip()
        
        if wybor == '1':
            run_live()
        elif wybor == '2':
            run_average()
        elif wybor == '3':
            print("Zamykanie programu. Do widzenia!")
            break
        else:
            print("Nieprawidłowy wybór. Wpisz 1, 2 lub 3.")