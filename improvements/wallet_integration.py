# Enhanced Wallet Integration for YYS-SQR

import json
import os
from web3 import Web3
from eth_account import Account

class WalletManager:
    """Enhanced wallet management with multiple wallet support"""
    
    def __init__(self):
        self.wallets = {}
        self.active_wallet = None
        self.wallet_file = "wallets.json"
        self.load_wallets()
    
    def add_wallet(self, name, private_key):
        """Add a new wallet"""
        try:
            account = Account.from_key(private_key)
            self.wallets[name] = {
                'address': account.address,
                'private_key': private_key  # In production, encrypt this!
            }
            self.save_wallets()
            return True
        except Exception as e:
            print(f"Error adding wallet: {e}")
            return False
    
    def set_active_wallet(self, name):
        """Set the active wallet"""
        if name in self.wallets:
            self.active_wallet = name
            return True
        return False
    
    def get_active_wallet(self):
        """Get active wallet info"""
        if self.active_wallet and self.active_wallet in self.wallets:
            return self.wallets[self.active_wallet]
        return None
    
    def get_wallet_balance(self, network_config, wallet_name=None):
        """Get wallet balance on specified network"""
        wallet_name = wallet_name or self.active_wallet
        if not wallet_name or wallet_name not in self.wallets:
            return 0
        
        try:
            w3 = Web3(Web3.HTTPProvider(network_config['rpc_url']))
            address = self.wallets[wallet_name]['address']
            balance_wei = w3.eth.get_balance(address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0
    
    def estimate_gas_cost(self, network_config):
        """Estimate gas cost for a transaction"""
        try:
            w3 = Web3(Web3.HTTPProvider(network_config['rpc_url']))
            gas_price = w3.to_wei(network_config['gas_price'], 'gwei')
            gas_limit = 200000  # Estimated gas limit
            cost_wei = gas_price * gas_limit
            cost_eth = w3.from_wei(cost_wei, 'ether')
            return float(cost_eth)
        except Exception as e:
            print(f"Error estimating gas: {e}")
            return 0
    
    def save_wallets(self):
        """Save wallets to file (WARNING: Private keys in plaintext!)"""
        # In production, encrypt the private keys!
        with open(self.wallet_file, 'w') as f:
            json.dump(self.wallets, f, indent=2)
    
    def load_wallets(self):
        """Load wallets from file"""
        if os.path.exists(self.wallet_file):
            try:
                with open(self.wallet_file, 'r') as f:
                    self.wallets = json.load(f)
            except Exception as e:
                print(f"Error loading wallets: {e}")
                self.wallets = {}

class MetaMaskConnector:
    """Connect to MetaMask via browser extension (future enhancement)"""
    
    def __init__(self):
        self.connected = False
        self.account = None
    
    def connect(self):
        """Connect to MetaMask (placeholder for future implementation)"""
        # This would require a web interface or browser integration
        # For now, we'll use private key input
        pass
    
    def sign_transaction(self, transaction):
        """Sign transaction with MetaMask"""
        # Future implementation for MetaMask integration
        pass

class HardwareWalletConnector:
    """Connect to hardware wallets like Ledger/Trezor"""
    
    def __init__(self):
        self.connected = False
        self.device_type = None
    
    def connect_ledger(self):
        """Connect to Ledger device"""
        # Future implementation
        pass
    
    def connect_trezor(self):
        """Connect to Trezor device"""
        # Future implementation
        pass