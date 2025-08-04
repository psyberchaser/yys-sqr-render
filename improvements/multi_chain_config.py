# Multi-Chain Configuration for YYS-SQR

NETWORKS = {
    'sepolia': {
        'name': 'Sepolia Testnet',
        'chain_id': 11155111,
        'rpc_url': 'https://sepolia.infura.io/v3/7d8b2ce49fe24184b30beb42dc1fa791',
        'contract_address': '0xd8b934580fcE35a11B58C6D73aDeE468a2833fa8',
        'explorer_url': 'https://sepolia.etherscan.io',
        'gas_price': 10,  # gwei
        'is_testnet': True
    },
    'ethereum': {
        'name': 'Ethereum Mainnet',
        'chain_id': 1,
        'rpc_url': 'https://mainnet.infura.io/v3/YOUR_KEY',
        'contract_address': '0x...',  # Deploy to mainnet
        'explorer_url': 'https://etherscan.io',
        'gas_price': 20,  # gwei
        'is_testnet': False
    },
    'polygon': {
        'name': 'Polygon',
        'chain_id': 137,
        'rpc_url': 'https://polygon-rpc.com',
        'contract_address': '0x...',  # Deploy to Polygon
        'explorer_url': 'https://polygonscan.com',
        'gas_price': 30,  # gwei
        'is_testnet': False
    },
    'base': {
        'name': 'Base',
        'chain_id': 8453,
        'rpc_url': 'https://mainnet.base.org',
        'contract_address': '0x...',  # Deploy to Base
        'explorer_url': 'https://basescan.org',
        'gas_price': 1,  # gwei
        'is_testnet': False
    }
}

def get_network_config(network_name):
    """Get configuration for specified network"""
    return NETWORKS.get(network_name, NETWORKS['sepolia'])

def get_available_networks():
    """Get list of available networks"""
    return list(NETWORKS.keys())