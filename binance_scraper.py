#!/usr/bin/env python3
"""
Binance Futures Leaderboard Scraper using Scrapling

This script scrapes trader data from the Binance Futures Leaderboard
using the Scrapling library for stealthy web scraping.
"""

import time
import json
import csv
import argparse
from datetime import datetime
from scrapling.fetchers import StealthyFetcher


class BinanceLeaderboardScraper:
    def __init__(self):
        """Initialize the scraper with Scrapling's StealthyFetcher"""
        # Enable adaptive mode for better detection avoidance
        StealthyFetcher.adaptive = True
    
    def scrape_user_data(self, encrypted_uid):
        """Scrape data for a specific user from the leaderboard"""
        url = f"https://www.binance.com/en/futures-activity/leaderboard/user?encryptedUid={encrypted_uid}"
        
        print(f"Loading page for user: {encrypted_uid}")
        
        # Fetch the page with StealthyFetcher
        page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        
        if page.status != 200:
            print(f"Failed to load page. Status code: {page.status}")
            return None
        
        try:
            # Extract user profile data
            user_data = {
                "encrypted_uid": encrypted_uid,
                "timestamp": datetime.now().isoformat()
            }
            
            # Get user nickname
            try:
                nickname_element = page.css(".css-1qvxqpo", auto_save=True)
                if nickname_element:
                    user_data["nickname"] = nickname_element[0].text
                else:
                    user_data["nickname"] = "Unknown"
            except Exception as e:
                print(f"Error extracting nickname: {e}")
                user_data["nickname"] = "Unknown"
            
            # Get user statistics
            stats = {}
            try:
                stats_elements = page.css(".css-1uj8qtb", auto_save=True)
                for element in stats_elements:
                    try:
                        label = element.css(".css-1lv32l7")[0].text
                        value = element.css(".css-1qvxqpo")[0].text
                        stats[label] = value
                    except Exception as e:
                        print(f"Error extracting stat: {e}")
            except Exception as e:
                print(f"Error extracting stats: {e}")
            
            user_data["stats"] = stats
            
            # Get position history
            positions = []
            try:
                # Find position rows
                position_rows = page.css("table tbody tr", auto_save=True)
                
                for row in position_rows:
                    try:
                        cells = row.css("td")
                        if len(cells) >= 6:
                            position = {
                                "symbol": cells[0].text,
                                "entry_price": cells[1].text,
                                "mark_price": cells[2].text,
                                "pnl": cells[3].text,
                                "roe": cells[4].text,
                                "timestamp": cells[5].text
                            }
                            positions.append(position)
                    except Exception as e:
                        print(f"Error extracting position row: {e}")
            except Exception as e:
                print(f"Error extracting positions: {e}")
            
            user_data["positions"] = positions
            
            return user_data
            
        except Exception as e:
            print(f"Error scraping user data: {e}")
            return None
        
    def save_to_json(self, data, filename):
        """Save the scraped data to a JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")
    
    def save_to_csv(self, data, filename):
        """Save the positions data to a CSV file without using pandas"""
        if data and "positions" in data and data["positions"]:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # Get field names from the first position
                fieldnames = list(data["positions"][0].keys())
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for position in data["positions"]:
                    writer.writerow(position)
                
                print(f"Positions data saved to {filename}")
        else:
            print("No positions data to save")


def main():
    parser = argparse.ArgumentParser(description='Scrape data from Binance Futures Leaderboard')
    parser.add_argument('--uid', type=str, required=True, help='Encrypted UID of the trader')
    parser.add_argument('--output', type=str, default='trader_data', help='Output filename prefix (without extension)')
    
    args = parser.parse_args()
    
    scraper = BinanceLeaderboardScraper()
    
    data = scraper.scrape_user_data(args.uid)
    
    if data:
        # Save data to JSON
        scraper.save_to_json(data, f"{args.output}.json")
        
        # Save positions to CSV
        scraper.save_to_csv(data, f"{args.output}_positions.csv")


if __name__ == "__main__":
    main()