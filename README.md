# John's Estate Assistant — Projektová dokumentace

---

## Úvod

**John's Estate Assistant** je webová aplikace postavená na Pythonu (Flask), která slouží k predikci cen nemovitostí pomocí umělé inteligence, výpočtu hypoték, správě historie a registraci uživatelů.

Aplikace využívá neuronovou síť, která byla natrénována na reálných datech z českého realitního trhu.

---

## Cíle projektu

- Predikce cen nemovitostí na základě parametrů (dispozice, metráž, lokalita, stav, energetická náročnost)
    
- Výpočet měsíční splátky hypotéky
    
- Ukládání historie výpočtů a predikcí
    
- Uživatelské účty a správa
    
- Backend i frontend validace
    
- Logging, testování a pokrytí kódu
    

---

## Použité technologie

|Oblast|Nástroje|
|---|---|
|Backend|Python 3.12, Flask|
|Frontend|HTML5, CSS3, Vanilla JS|
|AI / ML|TensorFlow (Keras), pandas, pickle|
|Databáze|MySQL|
|Testování|Pytest, coverage|
|Logging|logging (UTF-8, do souboru `logs/`)|
|Ostatní|Blueprinty, JSON, Bootstrap (volitelně)|

---

### Ai

Cílem bylo vytvořit **regresní model**, který na základě údajů o nemovitosti **predikuje její přibližnou cenu** (v Kč). Model byl natrénován na reálných datech z českého trhu.

Použitý model:

Model byl vytvořen a trénován pomocí **Keras** (součást knihovny TensorFlow).
### Vstupní parametry modelu

Každá nemovitost je popsána následujícími číselnými parametry:

|Parametr|Popis|
|---|---|
|`metraz`|Výměra bytu v metrech čtverečních (normalizováno /10)|
|`rozloha`|Počet místností (např. `3+kk` → `3`)|
|`energeticka_narocnost`|Hodnota A–G převedená na čísla 1–7|
|`stav`|Stav nemovitosti (před rekonstrukcí → novostavba: 1–5)|
|`lokalita`|Číselná reprezentace kraje (každý kraj má své ID)|

> Tyto hodnoty jsou mapovány pomocí `*.pkl` souborů a scaleru.


---
## Struktura projektu

omegaNemovitosti/
├── app.py                  # Inicializace Flask aplikace
├── config.json             # Konfigurace (port, modely, DB)
├── db.py                   # Připojení k databázi (MySQL)
├── logs/                   # Logy (logování výjimek, přístupů)
├── models/                 # Uložené AI modely a scaler
├── routes/                 # Flask routy (main.py, hypoteka.py, auth.py)
├── static/                 # JS, CSS, JSON s úroky
├── templates/              # HTML šablony (Jinja2)
├── tests/                  # Testovací jednotky (Pytest)
├── utils/                  # AI predikční logika
└── requirements.txt        # Seznam závislostí

---

## Popis jednotlivých částí

### `app.py`

- Načítá model a scalery
    
- Registruje routy
    
- Nastavuje logger
    
- Spouští aplikaci
    

### `routes/`

- `main.py` – formulář na predikci, uložení, srovnání
    
- `hypoteka.py` – výpočet hypotéky
    
- `auth.py` – registrace, login, logout
    

### `utils/predictor.py`

- Převod vstupních dat na numerický formát
    
- Normalizace pomocí scaleru
    
- Výstup predikované ceny v Kč
    

### `templates/`

- `index.html`, `hypoteka.html`, `moje_predikce.html`, `login.html`, `register.html`
    
- Stylizované přes `style.css`
    

### `static/scripts/`

- Validace formulářů na frontend
    
- Dynamická práce s úrokovou sazbou podle fixace
    
- Export CSV tabulky
    

---

## Databázové schéma

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    metraz FLOAT,
    rozloha VARCHAR(10),
    energeticka VARCHAR(5),
    stav VARCHAR(50),
    lokalita VARCHAR(100),
    cena FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE hypoteka_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    uver FLOAT,
    urok FLOAT,
    mesice INT,
    fixace INT,
    vlastni FLOAT,
    splatka FLOAT,
    total FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

---

## Konfigurace (`config.json`)

{
  "host": "127.0.0.1",
  "port": 3020,
  "debug": true,

  "model_path": "models/neural_model.keras",
  "scaler_path": "models/scaler.pkl",
  "location_mapping_path": "models/location_mapping.pkl",
  "energy_mapping_path": "models/energy_mapping.pkl",
  "condition_mapping_path": "models/condition_mapping.pkl",
  "logger_file_path": "logs/app.log",

  "db_host": "sql.daniellinda.net",
  "db_user": "remote",
  "db_password": "hm3C4iLL+",
  "db_name": "omega_poloch",
  "secret_key": "superSECRET"
}

---

## Spuštění projektu

1. Naklonuj repozitář
    
2. Vytvoř a aktivuj virtuální prostředí
    
python -m venv .venv
.venv\Scripts\activate

3. Nainstaluj závislosti:
    
pip install -r requirements.txt

4. v projektu(root slozce) zalozit slozku logs a v ni soubor app.log

logs/app.log

5. spustit samotnou aplikaci

python app.py

---

## Testování

Spuštění testů:

pytest

S pokrytím:

coverage run -m pytest

coverage report

---
### Linky

web - https://github.com/Najver/NemovitostiWeb

cista data - https://github.com/Najver/dataNaOmegu

crawler - https://github.com/Najver/crawlerNaOmegu

### chat
chat delal nejake html a stylovani
