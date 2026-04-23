# Hackers Scraper

Proyecto en Python para extraer datos desde:

- `https://dorahacks.io/hackathon/boring-ai/hackers`

Actualmente el script obtiene **solo hackers con `BUIDL Submitted`** y guarda:

- Nombre de hacker
- URL completa del BUIDL (`https://dorahacks.io/buidl/<id>`)

## Requisitos

- Python 3.10+ (recomendado 3.11 o superior)
- Windows PowerShell (o terminal equivalente)

## Instalacion (entorno virtual)

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m playwright install chromium
```

## Ejecucion

```powershell
.\.venv\Scripts\python .\scrape_hackers.py
```

## Salida

El script genera:

- `hackers_buidl_submitted.txt`

Formato por linea:

```text
nombre_hacker | https://dorahacks.io/buidl/12345
```

## Archivos del proyecto

- `scrape_hackers.py`: script principal de scraping.
- `requirements.txt`: dependencias Python.
- `hackers_names.txt`: lista historica de nombres obtenida en una ejecucion anterior.
- `hackers_buidl_submitted.txt`: resultado actual filtrado por `BUIDL Submitted`.

## Nota tecnica

El sitio usa protecciones anti-bot, por eso el script utiliza `playwright` para abrir la pagina y consumir el endpoint interno paginado con una sesion valida del navegador.
