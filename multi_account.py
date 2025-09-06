#!/usr/bin/env python3
"""
Multi-account support for Substack API
Handles loading/saving environment variables for different Substack accounts
"""

import os
import glob
from typing import Dict, Optional, List
from dotenv import load_dotenv, set_key

ENV_DIR = "env"

def get_all_account_files() -> List[str]:
    """Get list of all .account*.env files"""
    return glob.glob(os.path.join(ENV_DIR, ".account*.env"))

def find_account_by_user_id(user_id: str) -> Optional[str]:
    """
    Find the env file that contains the given user_id
    Returns the env file path or None if not found
    """
    account_files = get_all_account_files()
    
    for env_file in account_files:
        try:
            # Load this specific env file temporarily
            from dotenv import dotenv_values
            env_vars = dotenv_values(env_file)
            
            if env_vars.get('USER_ID') == user_id:
                return env_file
        except:
            continue
    
    return None

def load_account_env(user_id: str) -> Dict[str, str]:
    """
    Load environment variables for a specific user_id
    Returns dict with all env vars or raises exception if not found
    """
    env_file = find_account_by_user_id(user_id)
    
    if not env_file:
        raise ValueError(f"No account found with USER_ID: {user_id}")
    
    from dotenv import dotenv_values
    return dotenv_values(env_file)

def save_account_env(user_id: str, env_vars: Dict[str, str]) -> str:
    """
    Save environment variables for a specific user_id
    Returns the env file path that was updated
    """
    env_file = find_account_by_user_id(user_id)
    
    if not env_file:
        # Create new account file
        account_files = get_all_account_files()
        next_num = len(account_files) + 1
        env_file = os.path.join(ENV_DIR, f".account{next_num}.env")
    
    # Ensure env_vars contains the user_id
    env_vars['USER_ID'] = user_id
    
    # Write all variables to the file
    for key, value in env_vars.items():
        set_key(env_file, key, value)
    
    return env_file

def list_all_accounts() -> List[Dict[str, str]]:
    """
    List basic info about all accounts
    Returns list of dicts with user_id, publication_url, env_file
    """
    accounts = []
    account_files = get_all_account_files()
    
    for env_file in account_files:
        try:
            from dotenv import dotenv_values
            env_vars = dotenv_values(env_file)
            
            accounts.append({
                'user_id': env_vars.get('USER_ID', 'unknown'),
                'publication_url': env_vars.get('PUBLICATION_URL', 'unknown'),
                'env_file': env_file
            })
        except:
            continue
    
    return accounts

def set_active_account_env(user_id: str):
    """
    Load environment variables for the specified account into os.environ
    This makes the account active for the current session
    """
    env_vars = load_account_env(user_id)
    
    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value

def create_sample_account(account_num: int = 2) -> str:
    """
    Create a sample account env file for testing
    Returns the created file path
    """
    env_file = os.path.join(ENV_DIR, f".account{account_num}.env")
    
    sample_vars = {
        'PUBLICATION_URL': f'https://account{account_num}.substack.com',
        'USER_ID': f'user{account_num}',
        'SID': f'sample_sid_{account_num}',
        'SUBSTACK_SID': f'sample_substack_sid_{account_num}',
        'SUBSTACK_LLI': f'sample_lli_{account_num}'
    }
    
    for key, value in sample_vars.items():
        set_key(env_file, key, value)
    
    return env_file

if __name__ == "__main__":
    # Test the functions
    print("Available accounts:")
    accounts = list_all_accounts()
    for acc in accounts:
        print(f"- User ID: {acc['user_id']}, URL: {acc['publication_url']}")
    
    # Create sample account if needed
    if len(accounts) < 2:
        print("\nCreating sample account...")
        sample_file = create_sample_account()
        print(f"Created: {sample_file}")