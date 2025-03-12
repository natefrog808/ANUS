"""
Anus AI - Web3 Module
=====================

This module extends the Anus AI framework with Web3 capabilities, allowing AI agents to interact
with blockchain networks, smart contracts, decentralized applications, and other Web3 technologies.

Components:
- Web3 Tools: Specialized tools for blockchain interactions
- Web3Agent: Agent class specialized for Web3 operations
- Web3Society: Multi-agent society for complex Web3 tasks

Supported Networks:
- Ethereum (full support)
- Solana (partial support)
- More networks coming soon

Usage:
    from anus.web3 import Web3Agent
    
    agent = Web3Agent({
        "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
    })
    
    balance = agent.token_balance("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    print(f"ETH Balance: {balance['balance']} {balance['symbol']}")
"""

# Version info
__version__ = "0.1.0"

# Import main components for easier access
from anus.web3.tools import (
    Web3ConnectionTool,
    SmartContractTool,
    TokenTool,
    NFTTool,
    DeFiTool,
    ENSTool,
    IPFSTool,
)

from anus.web3.agent import (
    Web3Agent,
)

from anus.web3.society import (
    Web3Society,
)

# Define what's available when using "from anus.web3 import *"
__all__ = [
    # Tools
    "Web3ConnectionTool",
    "SmartContractTool",
    "TokenTool",
    "NFTTool", 
    "DeFiTool",
    "ENSTool", 
    "IPFSTool",
    
    # Agent
    "Web3Agent",
    
    # Society
    "Web3Society",
]

# Module metadata
__author__ = "Anus AI Team"
__email__ = "contact@anus-ai.org"
__description__ = "Web3 ecosystem integration for the Anus AI framework"

# Define default network providers - users should override these with their own values
DEFAULT_PROVIDERS = {
    "ethereum": {
        "mainnet": "https://eth-mainnet.public.blastapi.io",  # Public endpoint, rate-limited
        "sepolia": "https://ethereum-sepolia.publicnode.com",  # Testnet public endpoint
    },
    "solana": {
        "mainnet": "https://api.mainnet-beta.solana.com",  # Public Solana endpoint
        "devnet": "https://api.devnet.solana.com",          # Solana devnet
    }
}

# Define supported networks and their capabilities
SUPPORTED_NETWORKS = {
    "ethereum": {
        "status": "full",
        "tools": ["connection", "contract", "token", "nft", "defi", "ens"],
    },
    "solana": {
        "status": "partial",
        "tools": ["connection"],
    },
    "polygon": {
        "status": "planned",
        "tools": [],
    },
    "arbitrum": {
        "status": "planned",
        "tools": [],
    },
    "optimism": {
        "status": "planned",
        "tools": [],
    },
    "base": {
        "status": "planned",
        "tools": [],
    }
}
