# Binance Futures Leaderboard Scraper

A simple Python bot to scrape trader data from the Binance Futures Leaderboard using the Scrapling library.

## Features

- Extracts trader nickname and statistics
- Collects position history data
- Saves data in both JSON and CSV formats
- Uses Scrapling's StealthyFetcher for stealthy web scraping
- Adaptive scraping that survives website design changes

## Requirements

- Python 3.7+

## Installation

1. Clone this repository
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script with the encrypted UID of the trader you want to scrape:

```bash
python binance_scraper.py --uid 14EA12E7412DC5A21DFF5E7EAC6013B9
```

### Command-line Arguments (Basic Scraper)

- `--uid`: (Required) Encrypted UID of the trader to scrape
- `--output`: (Optional) Output filename prefix (default: "trader_data")

Example:

```bash
python binance_scraper.py --uid 14EA12E7412DC5A21DFF5E7EAC6013B9 --output trader1
```

### Advanced Scraper

For more features, use the advanced scraper:

```bash
python advanced_scraper.py --uids 14EA12E7412DC5A21DFF5E7EAC6013B9 --schedule 6
```

### Command-line Arguments (Advanced Scraper)

- `--uids`: List of encrypted UIDs to scrape
- `--uid-file`: File containing encrypted UIDs (one per line)
- `--output-dir`: Output directory for data files (default: "data")
- `--schedule`: Schedule scraping every N hours

Example:

```bash
python advanced_scraper.py --uids 14EA12E7412DC5A21DFF5E7EAC6013B9 ANOTHER_UID --output-dir results --schedule 12
```

## Output

The script generates two files:
- `trader_data.json`: Complete trader data including profile and positions
- `trader_data_positions.csv`: Position history in CSV format for easy analysis

## How It Works

The scraper uses Scrapling's StealthyFetcher with adaptive mode enabled:

```python
from scrapling.fetchers import StealthyFetcher
StealthyFetcher.adaptive = True

# Fetch website content stealthily
page = StealthyFetcher.fetch('https://example.com', headless=True, network_idle=True)

# Extract data with auto_save for resilience against site changes
elements = page.css('.some-class', auto_save=True)
```

## Notes

- The script includes a delay between requests to avoid rate limiting
- Adaptive scraping helps survive website design changes
- Error handling is implemented to catch and report issues during scraping

## Disclaimer

This tool is for educational purposes only. Please respect Binance's terms of service and rate limits when using this scraper.