#!/usr/bin/env python3
"""
Meta Ads Manager account name updater using Facebook Marketing API.
Requires Facebook Marketing API setup and access tokens.
"""

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.exceptions import FacebookRequestError
import json
import time
from typing import List, Dict
from update_account_names import update_account_name

class MetaAdsUpdater:
    def __init__(self, access_token: str, app_id: str, app_secret: str):
        """
        Initialize Meta Ads API connection.
        
        Args:
            access_token: Facebook Marketing API access token
            app_id: Facebook app ID
            app_secret: Facebook app secret
        """
        self.access_token = access_token
        FacebookAdsApi.init(app_id, app_secret, access_token)
        self.api = FacebookAdsApi.get_default_api()
    
    def get_all_ad_accounts(self) -> List[Dict]:
        """
        Retrieve all accessible ad accounts.
        
        Returns:
            List of ad account dictionaries with id and name
        """
        try:
            # Get accounts accessible by the current user
            me = self.api.get_default_api().call(
                'GET',
                '/me/adaccounts',
                {'fields': 'id,name,account_status'}
            )
            
            accounts = []
            for account_data in me['data']:
                if account_data.get('account_status') == 1:  # Active accounts only
                    accounts.append({
                        'id': account_data['id'],
                        'name': account_data['name']
                    })
            
            return accounts
            
        except FacebookRequestError as e:
            print(f"Error retrieving ad accounts: {e}")
            return []
    
    def update_account_name(self, account_id: str, new_name: str) -> bool:
        """
        Update an ad account's name.
        
        Args:
            account_id: Ad account ID (format: act_XXXXXXXXX)
            new_name: New name for the account
            
        Returns:
            True if successful, False otherwise
        """
        try:
            account = AdAccount(account_id)
            account.update(params={'name': new_name})
            return True
            
        except FacebookRequestError as e:
            print(f"Error updating account {account_id}: {e}")
            return False
    
    def process_all_accounts(self, dry_run: bool = True) -> Dict:
        """
        Process all accounts and update names according to the new structure.
        
        Args:
            dry_run: If True, only show what would be changed without making updates
            
        Returns:
            Dictionary with processing results
        """
        accounts = self.get_all_ad_accounts()
        results = {
            'total_accounts': len(accounts),
            'changed': 0,
            'unchanged': 0,
            'errors': 0,
            'changes': []
        }
        
        print(f"Found {len(accounts)} active ad accounts")
        print("=" * 50)
        
        for account in accounts:
            original_name = account['name']
            updated_name = update_account_name(original_name)
            
            if original_name != updated_name:
                print(f"WOULD CHANGE: {original_name} -> {updated_name}")
                
                if not dry_run:
                    success = self.update_account_name(account['id'], updated_name)
                    if success:
                        print(f"✓ Successfully updated {account['id']}")
                        results['changed'] += 1
                    else:
                        print(f"✗ Failed to update {account['id']}")
                        results['errors'] += 1
                    
                    # Rate limiting - pause between API calls
                    time.sleep(1)
                else:
                    results['changed'] += 1
                
                results['changes'].append({
                    'account_id': account['id'],
                    'original_name': original_name,
                    'updated_name': updated_name
                })
            else:
                print(f"NO CHANGE: {original_name}")
                results['unchanged'] += 1
        
        return results

def main():
    """Main function - requires configuration."""
    print("Meta Ads Manager Account Name Updater")
    print("====================================")
    print()
    print("This script requires:")
    print("1. Facebook Marketing API access token")
    print("2. Facebook app ID and app secret")
    print("3. Proper permissions on the ad accounts")
    print()
    
    # Configuration - replace with your actual values
    ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"
    APP_ID = "YOUR_APP_ID_HERE" 
    APP_SECRET = "YOUR_APP_SECRET_HERE"
    
    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("Please configure your Facebook Marketing API credentials first!")
        print("Update the ACCESS_TOKEN, APP_ID, and APP_SECRET variables.")
        return
    
    updater = MetaAdsUpdater(ACCESS_TOKEN, APP_ID, APP_SECRET)
    
    # First run as dry run to see what would change
    print("Running DRY RUN - no changes will be made:")
    print("-" * 50)
    results = updater.process_all_accounts(dry_run=True)
    
    print(f"\nDRY RUN RESULTS:")
    print(f"Total accounts: {results['total_accounts']}")
    print(f"Would change: {results['changed']}")
    print(f"No change needed: {results['unchanged']}")
    
    if results['changed'] > 0:
        response = input(f"\nProceed with updating {results['changed']} accounts? (y/N): ")
        if response.lower() == 'y':
            print("\nProcessing actual updates:")
            print("-" * 50)
            final_results = updater.process_all_accounts(dry_run=False)
            
            print(f"\nFINAL RESULTS:")
            print(f"Successfully updated: {final_results['changed']}")
            print(f"Errors: {final_results['errors']}")

if __name__ == "__main__":
    main()