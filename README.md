# Warframe Market Fetcher

Narzędzie w Pythonie do pobierania listy przedmiotów z Warframe Market oraz wszystkich aukcji (orders) i zapisywania ich do lokalnej bazy danych SQLite.

## Wymagania

- Python 3.10+ (zalecane).
- Dostęp do internetu (API Warframe Market).
- Zależności z `requirements.txt`.

Instalacja zależności:

```bash
pip install -r requirements.txt
```

## Czy potrzebny jest klucz API?

Nie. Warframe Market udostępnia publiczne API i do podstawowego pobierania danych **nie jest wymagany żaden klucz API**. Narzędzie działa bez dodatkowej konfiguracji.

## Sposób uruchomienia

Podstawowe uruchomienie (utworzy plik bazy w bieżącym katalogu):

```bash
python warframe_market_fetcher.py
```

Parametry:

- `--db` – ścieżka do pliku bazy danych SQLite (domyślnie `warframe_market.sqlite3`).
- `--limit` – limit liczby przedmiotów do pobrania (przydatne w testach).
- `--pause` – przerwa między zapytaniami do API w sekundach (domyślnie `0.2`).
- `--api-base` – bazowy adres API (domyślnie `https://api.warframe.market/v1`).
  Narzędzie automatycznie spróbuje też wariantu bez `/v1` lub z `/v1`, jeśli jest to konieczne.

Przykład (pobierz tylko 20 pierwszych przedmiotów i zapisuj do osobnej bazy):

```bash
python warframe_market_fetcher.py --db ./data/warframe.sqlite3 --limit 20 --pause 0.1
```

## Jak testować?

Poniżej przykładowe scenariusze testowe, które pozwalają sprawdzić poprawność działania bez pobierania całego katalogu:

1. **Szybki test połączenia z API (limit 5):**

   ```bash
   python warframe_market_fetcher.py --limit 5 --pause 0
   ```

   Oczekiwany rezultat:
   - powstaje plik `warframe_market.sqlite3`,
   - w bazie pojawiają się rekordy w tabelach `items` i `orders`.

2. **Test z własną ścieżką bazy:**

   ```bash
   python warframe_market_fetcher.py --db ./tmp/test.sqlite3 --limit 3
   ```

   Oczekiwany rezultat:
   - utworzony plik `./tmp/test.sqlite3`,
   - zasilone tabele `items` i `orders`.

3. **Kontrola zawartości bazy (SQLite):**

   Jeśli masz zainstalowane `sqlite3`, możesz sprawdzić liczbę rekordów:

   ```bash
   sqlite3 warframe_market.sqlite3 "SELECT COUNT(*) FROM items;"
   sqlite3 warframe_market.sqlite3 "SELECT COUNT(*) FROM orders;"
   ```

## Struktura bazy

Narzędzie tworzy dwie tabele:

- `items` – podstawowe dane o przedmiotach,
- `orders` – aukcje przypisane do przedmiotów (połączone przez `item_id`).

Tabele są uzupełniane mechanizmem upsert, więc kolejne uruchomienia aktualizują istniejące wpisy.

## Instrukcja od A do Z (komputer nieprzygotowany)

Poniżej kompletna instrukcja dla systemu Windows, jeśli komputer nie jest w ogóle przygotowany:

1. **Zainstaluj Python:**
   - Wejdź na https://www.python.org/downloads/ i pobierz najnowszą wersję Python 3.
   - Podczas instalacji zaznacz opcję **Add Python to PATH**.

2. **Sprawdź instalację:**
   - Otwórz PowerShell lub CMD i wpisz:
     ```bash
     python --version
     ```
   - Jeśli komenda nie działa, zrestartuj terminal lub komputer i spróbuj ponownie.

3. **Pobierz projekt:**
   - Rozpakuj archiwum ZIP z repozytorium lub sklonuj repozytorium Git.
   - Przejdź do katalogu projektu, np.:
     ```bash
     cd C:\Users\TwojUzytkownik\Downloads\warframemarket-main
     ```

4. **Utwórz wirtualne środowisko:**
   - W katalogu projektu wpisz:
     ```bash
     python -m venv .venv
     ```

5. **Aktywuj środowisko:**
   - PowerShell:
     ```bash
     .\.venv\Scripts\Activate.ps1
     ```
   - CMD:
     ```bash
     .\.venv\Scripts\activate
     ```
   - Jeśli PowerShell blokuje skrypt aktywacji, uruchom:
     ```bash
     Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
     ```
     i ponownie aktywuj środowisko.

6. **Zainstaluj zależności:**
   ```bash
   python -m pip install -r requirements.txt
   ```

7. **Uruchom testowo z limitem:**
   ```bash
   python warframe_market_fetcher.py --limit 5 --pause 0
   ```

8. **Sprawdź, czy powstała baza:**
   - W katalogu pojawi się plik `warframe_market.sqlite3`.

9. **(Opcjonalnie) sprawdź zawartość bazy:**
   - Jeśli masz zainstalowane `sqlite3`:
     ```bash
     sqlite3 warframe_market.sqlite3 "SELECT COUNT(*) FROM items;"
     sqlite3 warframe_market.sqlite3 "SELECT COUNT(*) FROM orders;"
     ```

### Najczęstsze problemy i rozwiązania

- **Błąd 404 z API (`https://api.warframe.market/v1/items`)**
  - Sprawdź, czy masz połączenie z internetem.
  - Użyj innego bazowego adresu API:
    ```bash
    python warframe_market_fetcher.py --api-base https://api.warframe.market/v1
    ```
  - Jeśli wciąż występuje błąd, spróbuj bezpośrednio:
    ```bash
    python warframe_market_fetcher.py --api-base https://api.warframe.market
    ```
  - Sprawdź, czy URL działa w przeglądarce:
    - https://api.warframe.market/v1/items
  - Jeśli w przeglądarce również widzisz błąd, to znaczy, że sieć/proxy blokuje dostęp.
  - W sieciach firmowych lub szkolnych API może być blokowane przez proxy lub firewall.

- **Brak komendy `python` w systemie**
  - Zainstaluj Pythona ponownie i upewnij się, że zaznaczono opcję *Add Python to PATH*.

- **Problemy z aktywacją venv**
  - Upewnij się, że używasz właściwego terminala (PowerShell vs CMD).
  - W PowerShell ustaw `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
