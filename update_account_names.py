#!/usr/bin/env python3
"""
Script to update Meta Ads Manager account names for LDS Church organizational changes.
Updates area designations from old structure to new structure.
"""

import re
import csv
from typing import Dict, List, Tuple

def create_area_mapping() -> Dict[str, str]:
    """Create mapping of old area names to new area names."""
    return {
        "North America West": "United States West",
        "North America East": "United States East", 
        "North America Central": "United States Central",
        "North America Southwest": "United States Southwest",
        "North America Southeast": "United States Southeast",
        "North America Northeast": "United States Northeast"
    }

def update_account_name(account_name: str) -> str:
    """
    Update a single account name based on the new organizational structure.
    
    Args:
        account_name: Original account name
        
    Returns:
        Updated account name
    """
    area_mapping = create_area_mapping()
    
    # Check if this is a Canada account
    if "Canada" in account_name:
        # Replace any North America area with "Canada Area"
        for old_area in area_mapping.keys():
            if old_area in account_name:
                return account_name.replace(old_area + " Area", "Canada Area")
        return account_name
    
    # For non-Canada accounts, apply the standard mapping
    for old_area, new_area in area_mapping.items():
        if old_area in account_name:
            return account_name.replace(old_area, new_area)
    
    return account_name

def process_accounts_from_csv(input_file: str, output_file: str) -> None:
    """
    Process account names from a CSV file and output updated names.
    
    Args:
        input_file: Path to input CSV file with account names
        output_file: Path to output CSV file with updated names
    """
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Original Name', 'Updated Name'])
            
            for row in reader:
                if row:  # Skip empty rows
                    original_name = row[0]
                    updated_name = update_account_name(original_name)
                    writer.writerow([original_name, updated_name])
                    
                    if original_name != updated_name:
                        print(f"CHANGED: {original_name} -> {updated_name}")
                    else:
                        print(f"NO CHANGE: {original_name}")

def process_accounts_from_list(account_names: List[str]) -> List[Tuple[str, str]]:
    """
    Process a list of account names and return original/updated pairs.
    
    Args:
        account_names: List of original account names
        
    Returns:
        List of (original_name, updated_name) tuples
    """
    results = []
    for name in account_names:
        updated = update_account_name(name)
        results.append((name, updated))
        
        if name != updated:
            print(f"CHANGED: {name} -> {updated}")
        else:
            print(f"NO CHANGE: {name}")
    
    return results

def main():
    """Main function with example usage."""
    print("LDS Church Account Name Update Script")
    print("=====================================")
    
    # Example account names for testing
    test_accounts = [
        "Canada Vancouver Mission - North America West Area",
        "Washington Yakima Mission - North America West Area",
        "California Los Angeles Mission - North America West Area",
        "Canada Toronto Mission - North America East Area",
        "New York Mission - North America Northeast Area",
        "Texas Houston Mission - North America Southwest Area"
    ]
    
    print("\nTesting with example accounts:")
    print("-" * 50)
    
    results = process_accounts_from_list(test_accounts)
    
    print(f"\nProcessed {len(results)} accounts")
    print(f"Changed: {sum(1 for orig, upd in results if orig != upd)} accounts")
    print(f"Unchanged: {sum(1 for orig, upd in results if orig == upd)} accounts")

if __name__ == "__main__":
    main()