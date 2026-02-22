import os
import yaml


def load_buyers():
    """
    Load buyers from app/config/buyers.yaml.
    Returns a list of buyer email addresses (lowercase).
    """
    config_dir = os.path.dirname(os.path.abspath(__file__))
    buyers_file = os.path.join(config_dir, 'buyers.yaml')

    if not os.path.exists(buyers_file):
        return []

    try:
        with open(buyers_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            buyers_list = data.get('buyers', [])
            return [buyer['email'].lower().strip() for buyer in buyers_list if 'email' in buyer]
    except Exception as e:
        print(f"Warning: Failed to load buyers from {buyers_file}: {e}")
        return []


def get_buyer_info(email):
    """
    Get full buyer information (name, department) by email.
    Returns dict with 'name' and 'department' keys, or None if not found.
    """
    config_dir = os.path.dirname(os.path.abspath(__file__))
    buyers_file = os.path.join(config_dir, 'buyers.yaml')

    if not os.path.exists(buyers_file):
        return None

    try:
        with open(buyers_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            buyers_list = data.get('buyers', [])
            for buyer in buyers_list:
                if buyer.get('email', '').lower().strip() == email.lower().strip():
                    return {
                        'name': buyer.get('name', ''),
                        'department': buyer.get('department', ''),
                    }
    except Exception as e:
        print(f"Warning: Failed to load buyer info from {buyers_file}: {e}")

    return None
