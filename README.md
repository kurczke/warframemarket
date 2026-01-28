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
