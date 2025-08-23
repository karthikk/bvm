#!/usr/bin/env python3
"""
Generate data.json from Classes.csv for Brahma Vidya Mandir website
"""

import csv
import json
from collections import defaultdict
from datetime import datetime

def create_batch_structure():
    """Create the base structure for each batch"""
    return {
        "name": "",
        "description": "",
        "categories": {}
    }

def create_category_structure():
    """Create the base structure for each category"""
    return {
        "name": "",
        "description": "",
        "texts": {}
    }

def get_batch_info(batch_name):
    """Get batch metadata"""
    batch_info = {
        "Dhanyosi": {
            "name": "Dhanyosi Batch",
            "description": "2021-2025"
        },
        "Tattvamasi": {
            "name": "Tattvamasi Batch",
            "description": "Coimbatore Batch"
        },
        "Jignasu": {
            "name": "Jignasu Batch", 
            "description": "2024-2028"
        },
        "Miscellaneous": {
            "name": "Miscellaneous",
            "description": "Special programs and general spiritual content"
        }
    }
    return batch_info.get(batch_name, {"name": batch_name, "description": ""})

def get_category_info(category_name):
    """Get category metadata"""
    category_info = {
        "Upanishad": {
            "name": "Upanishads",
            "description": "Ancient wisdom texts - the culmination of Vedic knowledge"
        },
        "Bhagawad Gita": {
            "name": "Bhagavad Gita", 
            "description": "The song of the Lord - practical spirituality"
        },
        "Prakaranam": {
            "name": "Prakaranam",
            "description": "Introductory and foundational texts"
        },
        "Brahmasutram": {
            "name": "Brahmasutram",
            "description": "The aphorisms of Brahman - systematic philosophy"
        },
        "Satsang": {
            "name": "Satsang",
            "description": "Question and answer sessions, discussions"
        }
    }
    return category_info.get(category_name, {"name": category_name, "description": ""})

def normalize_key(name):
    """Convert name to lowercase key format"""
    return name.lower().replace(" ", "_").replace("-", "_").replace("|", "").replace(".", "").strip()

def generate_data_json():
    """Generate data.json from Classes.csv"""
    
    # Initialize data structure
    data = {
        "site_info": {
            "title": "Brahma Vidya Mandir",
            "description": "Learning Portal", 
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        },
        "batches": {},
        "metadata": {}
    }
    
    # Read CSV and organize data
    with open('Classes.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            batch_name = row['Batch'].strip()
            category_name = row['Category'].strip()
            text_name = row['Text'].strip()
            video_count = int(row['Video Count'].strip()) if row['Video Count'].strip() else 0
            playlist_id = row['Playlist'].strip()
            is_ongoing = row['Is Ongoing'].strip().lower() == 'yes'
            latest_link = row['Latest Link'].strip() if row['Latest Link'].strip() else None
            
            # Create batch if it doesn't exist
            batch_key = normalize_key(batch_name)
            if batch_key not in data['batches']:
                data['batches'][batch_key] = create_batch_structure()
                batch_info = get_batch_info(batch_name)
                data['batches'][batch_key].update(batch_info)
            
            # Determine categories - ongoing texts go in BOTH their natural category AND ongoing
            categories_to_add = []
            
            # Always add to natural category
            natural_category_key = normalize_key(category_name)
            natural_category_info = get_category_info(category_name)
            categories_to_add.append({
                'key': natural_category_key,
                'name': natural_category_info["name"],
                'description': natural_category_info["description"]
            })
            
            # If ongoing, also add to ongoing category
            if is_ongoing:
                categories_to_add.append({
                    'key': "ongoing",
                    'name': "Ongoing",
                    'description': "Current studies across different texts"
                })
            
            # Process each category
            for category_info in categories_to_add:
                category_key = category_info['key']
                
                # Create category if it doesn't exist
                if category_key not in data['batches'][batch_key]['categories']:
                    data['batches'][batch_key]['categories'][category_key] = create_category_structure()
                    data['batches'][batch_key]['categories'][category_key]['name'] = category_info['name']
                    data['batches'][batch_key]['categories'][category_key]['description'] = category_info['description']
                
                # Create text entry
                text_key = normalize_key(text_name)
                if text_key not in data['batches'][batch_key]['categories'][category_key]['texts']:
                    data['batches'][batch_key]['categories'][category_key]['texts'][text_key] = {
                        "name": text_name,
                        "description": f"{text_name} study",
                        "playlists": []
                    }
                
                # Create playlist entry
                playlist_entry = {
                    "name": text_name,
                    "playlist_id": playlist_id,
                    "description": f"{text_name} study",
                    "video_count": video_count
                }
                
                # Add latest video ID if it's ongoing and has a latest link (only for ongoing category)
                if is_ongoing and latest_link and category_key == "ongoing":
                    playlist_entry["latest_video_id"] = latest_link
                
                data['batches'][batch_key]['categories'][category_key]['texts'][text_key]['playlists'].append(playlist_entry)
    
    # Calculate metadata
    total_batches = len(data['batches'])
    total_categories = sum(len(batch['categories']) for batch in data['batches'].values())
    total_texts = sum(
        len(category['texts']) 
        for batch in data['batches'].values() 
        for category in batch['categories'].values()
    )
    total_playlists = sum(
        len(text['playlists'])
        for batch in data['batches'].values()
        for category in batch['categories'].values() 
        for text in category['texts'].values()
    )
    
    data['metadata'] = {
        "total_batches": total_batches,
        "total_categories": total_categories,
        "total_texts": total_texts,
        "total_playlists": total_playlists,
        "youtube_api_version": "v3",
        "cache_duration": 3600,
        "update_frequency": "daily"
    }
    
    # Write data.json
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    
    print(f"Generated data.json successfully!")
    print(f"Total batches: {total_batches}")
    print(f"Total categories: {total_categories}")
    print(f"Total texts: {total_texts}")
    print(f"Total playlists: {total_playlists}")

if __name__ == "__main__":
    generate_data_json()