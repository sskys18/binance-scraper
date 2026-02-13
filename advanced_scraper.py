#!/usr/bin/env python3
"""
Advanced Binance Futures Leaderboard Scraper using Scrapling

This script provides enhanced functionality for scraping multiple traders
and scheduling regular data collection using the Scrapling library.
"""

import os
import time
import json
import csv
import argparse
import schedule
from datetime import datetime
from scrapling.fetchers import StealthyFetcher


class AdvancedBinanceScraper:
    def __init__(self, output_dir="data"):
        """Initialize the scraper with Scrapling's StealthyFetcher and output directory"""
        # Enable adaptive mode for better detection avoidance
        StealthyFetcher.adaptive = True
        
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
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
    
    def scrape_multiple_users(self, user_ids):
        """Scrape data for multiple users"""
        results = {}
        
        for uid in user_ids:
            print(f"Scraping data for user: {uid}")
            data = self.scrape_user_data(uid)
            if data:
                results[uid] = data
            
            # Add a delay between requests to avoid rate limiting
            time.sleep(3)
        
        return results
    
    def save_to_json(self, data, filename):
        """Save the scraped data to a JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filepath}")
        return filepath
    
    def save_to_csv(self, data, filename):
        """Save the positions data to a CSV file without using pandas"""
        filepath = os.path.join(self.output_dir, filename)
        
        if isinstance(data, dict) and len(data) > 0:
            # For multiple users
            all_positions = []
            for uid, user_data in data.items():
                if "positions" in user_data and user_data["positions"]:
                    for pos in user_data["positions"]:
                        pos_with_user = pos.copy()
                        pos_with_user["user_id"] = uid
                        pos_with_user["nickname"] = user_data.get("nickname", "Unknown")
                        all_positions.append(pos_with_user)
            
            if all_positions:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    # Get field names from the first position
                    fieldnames = list(all_positions[0].keys())
                    
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for position in all_positions:
                        writer.writerow(position)
                    
                    print(f"Positions data saved to {filepath}")
                    return filepath
        
        elif data and "positions" in data and data["positions"]:
            # For single user
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                # Get field names from the first position
                fieldnames = list(data["positions"][0].keys())
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for position in data["positions"]:
                    writer.writerow(position)
                
                print(f"Positions data saved to {filepath}")
                return filepath
        
        print("No positions data to save")
        return None
    
    def scheduled_scraping(self, user_ids, interval_hours=6):
        """Set up scheduled scraping at regular intervals"""
        def job():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            print(f"\n--- Starting scheduled scraping at {timestamp} ---")
            
            data = self.scrape_multiple_users(user_ids)
            
            if data:
                self.save_to_json(data, f"traders_data_{timestamp}.json")
                self.save_to_csv(data, f"traders_positions_{timestamp}.csv")
            
            print(f"--- Completed scheduled scraping at {datetime.now().strftime('%Y%m%d_%H%M%S')} ---\n")
        
        # Run once immediately
        job()
        
        # Schedule to run at regular intervals
        schedule.every(interval_hours).hours.do(job)
        
        print(f"Scheduled scraping every {interval_hours} hours. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("Scheduled scraping stopped.")


def main():
    parser = argparse.ArgumentParser(description='Advanced scraper for Binance Futures Leaderboard')
    parser.add_argument('--uids', type=str, nargs='+', help='List of encrypted UIDs to scrape')
    parser.add_argument('--uid-file', type=str, help='File containing encrypted UIDs (one per line)')
    parser.add_argument('--output-dir', type=str, default='data', help='Output directory for data files')
    parser.add_argument('--schedule', type=int, help='Schedule scraping every N hours')
    
    args = parser.parse_args()
    
    # Get user IDs from arguments or file
    user_ids = []
    if args.uids:
        user_ids.extend(args.uids)
    
    if args.uid_file:
        try:
            with open(args.uid_file, 'r') as f:
                file_ids = [line.strip() for line in f if line.strip()]
                user_ids.extend(file_ids)
        except Exception as e:
            print(f"Error reading UID file: {e}")
    
    if not user_ids:
        # Default UID if none provided
        user_ids = ["14EA12E7412DC5A21DFF5E7EAC6013B9"]
        print(f"No UIDs provided. Using default UID: {user_ids[0]}")
    
    # Remove duplicates
    user_ids = list(set(user_ids))
    
    scraper = AdvancedBinanceScraper(output_dir=args.output_dir)
    
    try:
        if args.schedule:
            scraper.scheduled_scraping(user_ids, interval_hours=args.schedule)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if len(user_ids) == 1:
                # Single user mode
                data = scraper.scrape_user_data(user_ids[0])
                if data:
                    scraper.save_to_json(data, f"trader_data_{user_ids[0]}_{timestamp}.json")
                    scraper.save_to_csv(data, f"trader_positions_{user_ids[0]}_{timestamp}.csv")
            else:
                # Multiple users mode
                data = scraper.scrape_multiple_users(user_ids)
                if data:
                    scraper.save_to_json(data, f"traders_data_{timestamp}.json")
                    scraper.save_to_csv(data, f"traders_positions_{timestamp}.csv")
    except KeyboardInterrupt:
        print("Scraping stopped by user.")


if __name__ == "__main__":
    main()