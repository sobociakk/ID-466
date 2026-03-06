import socket
import time
import json
import os
from telnet_reader import get_espar_stream

HOST = '153.19.49.102'
#HOST = '127.0.0.1'
PORT = 8893
TIMEOUT = 10

def connect_and_start():
    print(f"\nŁączenie z {HOST}:{PORT}...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((HOST, PORT))
        s.sendall(b'\r\n')
        time.sleep(0.5)
        s.sendall(b'start\r\n')
        print("Połączono. Odbieranie danych...\n")
        return s
    except ConnectionRefusedError:
        print(f"Nie można nawiązać połączenia z hostem na porcie {PORT}: Połączenie nie powiodło się.")
        return None
    except socket.timeout:
        print(f"Nie można nawiązać połączenia z hostem na porcie {PORT}: Przekroczono czas oczekiwania.")
        return None
    except Exception as e:
        print(f"Wystąpił błąd sieci: {e}")
        return None

def stop_and_close(sock):
    if sock is None:
        return
    try:
        print("\nZatrzymuję transmisję...")
        sock.sendall(b'stop\r\n')
        time.sleep(0.5)
    except Exception:
        pass
    sock.close()

def run_live():
    #Tryb 1: Podgląd na żywo
    sock = connect_and_start()
    if not sock:
        return
    try:
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
        print("\n[!] Przerwano podgląd.")
    except socket.timeout:
        print("\n[!] Błąd: Przekroczono czas oczekiwania na dane z serwera.")
    finally:
        stop_and_close(sock)

def run_average():
    # Tryb 2: Zbieranie danych, uśrednianie i NORMALIZACJA RSSI (z podziałem na beacony)
    sock = connect_and_start()
    if not sock:
        return
    try:
        # Struktura: beacons_data[beacon_num][espar_char_int] = [rssi1, rssi2, ...]
        beacons_data = {}
        
        print("Zbieranie i uśrednianie danych dla wielu beaconów...")
        print("Naciśnij Ctrl+C, aby zakończyć, znormalizować wektory i zapisać do pliku.\n")
        
        packet_count = 0
        
        for frame in get_espar_stream(sock):
            b_num = frame['beacon_num']
            char_int = frame['espar_char_int']
            rssi = frame['rssi_dbm']
            
            # Inicjalizacja słowników dla nowego beacona/charakterystyki
            if b_num not in beacons_data:
                beacons_data[b_num] = {}
            if char_int not in beacons_data[b_num]:
                beacons_data[b_num][char_int] = []
                
            # Dodanie pomiaru
            beacons_data[b_num][char_int].append(rssi)
            packet_count += 1
            
            # Prosty wskaźnik postępu (żeby nie zalać konsoli tekstem)
            if packet_count % 50 == 0:
                print(f"Zebrano już {packet_count} pakietów od {len(beacons_data)} beaconów...", end='\r')
            
    except KeyboardInterrupt:
        print("\n\n[!] Zakończono zbieranie pomiarów. Przetwarzanie danych...")
        
        fingerprints = {}
        normalized_fingerprints = {}
        
        # --- UŚREDNIANIE I NORMALIZACJA DLA KAŻDEGO BEACONA ---
        for b_num, chars_data in beacons_data.items():
            fingerprints[b_num] = {}
            
            # 1. Uśrednianie
            for char_int, rssi_list in chars_data.items():
                srednia = sum(rssi_list) / len(rssi_list)
                fingerprints[b_num][char_int] = round(srednia, 2)
            
            # 2. Normalizacja min-max (0.0 - 1.0)
            if fingerprints[b_num]:
                min_rssi = min(fingerprints[b_num].values())
                max_rssi = max(fingerprints[b_num].values())
                
                normalized_fingerprints[b_num] = {}
                
                if max_rssi > min_rssi:
                    for char_int, s_rssi in fingerprints[b_num].items():
                        norm_val = (s_rssi - min_rssi) / (max_rssi - min_rssi)
                        normalized_fingerprints[b_num][char_int] = round(norm_val, 4)
                else:
                    # Zabezpieczenie przed dzieleniem przez zero
                    for char_int in fingerprints[b_num].keys():
                        normalized_fingerprints[b_num][char_int] = 0.0

        # --- WYŚWIETLANIE I ZAPIS ---
        print("\n--- ZNORMALIZOWANE ODCISKI (0.0 - 1.0) ---")
        print(json.dumps(normalized_fingerprints, indent=4))
        
        # Zapis do pliku
        os.makedirs('data', exist_ok=True)
        file_path = os.path.join('data', 'radio_map.json')
        with open(file_path, 'w') as f:
            json.dump(normalized_fingerprints, f, indent=4)
        print(f"\n[V] Zapisano mapę radiową do pliku: {file_path}")

    except socket.timeout:
        print("\n[!] Błąd: Przekroczono czas oczekiwania na dane z serwera.")
    finally:
        stop_and_close(sock)

if __name__ == '__main__':
    while True:
        print("\n=== SYSTEM LOKALIZACJI ESPAR ===")
        print("1 - Podgląd na żywo ")
        print("2 - Tworzenie odcisku ")
        print("3 - Wyjście")
        
        wybor = input("Wybierz tryb -> ").strip()
        
        if wybor == '1':
            run_live()
        elif wybor == '2':
            run_average()
        elif wybor == '3':
            print("Zamykanie programu...")
            break
        else:
            print("Nieprawidłowy wybór. Wpisz 1, 2 lub 3.")