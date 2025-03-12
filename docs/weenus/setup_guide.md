# Weenus Web3 Module Setup Guide

This guide will help you set up and configure the Web3 module for Anus AI, enabling interaction with blockchain networks, smart contracts, tokens, NFTs, and decentralized finance applications.

## Prerequisites

Before setting up the Web3 module, ensure you have:

1. Anus AI framework installed (version 0.7.0 or later)
2. Python 3.11 or later
3. Basic familiarity with blockchain concepts
4. API keys for blockchain providers (optional but recommended)

## Installation

### Option 1: Install with Web3 Support

If you're installing Anus AI for the first time and want Web3 support, use the following command:

```bash
pip install "anus-ai[web3]"
```

This will install Anus AI with all required Web3 dependencies.

### Option 2: Add Web3 Support to Existing Installation

If you already have Anus AI installed, you can add Web3 support by installing the required dependencies:

```bash
pip install "anus-ai[web3]"
```

### Option 3: Manual Installation of Dependencies

If you prefer to manually install dependencies or need to customize the installation, you can install the required packages individually:

```bash
# Core dependencies
pip install web3>=6.0.0 solana>=0.30.0 ipfshttpclient>=0.8.0

# Optional dependencies
pip install eth-brownie>=1.19.0  # For smart contract development
pip install eth-ape>=0.6.0       # For advanced contract interactions
```

## Configuration

The Web3 module requires configuration for blockchain providers, IPFS gateways, and other settings. You can configure these through:

1. Configuration file
2. Environment variables
3. Programmatic configuration

### Configuration File

Create or update your Anus AI configuration file (default location: `.anus/config.yaml`) with the following Web3 section:

```yaml
web3:
  providers:
    ethereum:
      mainnet: "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
      sepolia: "https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY"
    solana:
      mainnet: "https://api.mainnet-beta.solana.com"
      devnet: "https://api.devnet.solana.com"
  
  ipfs:
    gateway: "https://ipfs.io/ipfs/"
    
  memory_path: "./web3_agent_memory"
  coordination_strategy: "hierarchical"
```

### Environment Variables

You can also use environment variables to configure the Web3 module:

```bash
# Ethereum provider
export ETHEREUM_PROVIDER="https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"

# Solana provider
export SOLANA_PROVIDER="https://api.mainnet-beta.solana.com"

# IPFS gateway
export IPFS_GATEWAY="https://ipfs.io/ipfs/"
```

### Programmatic Configuration

When initializing Web3 components in your code, you can provide configuration directly:

```python
from anus.web3 import Web3Agent

# Create Web3Agent with configuration
agent = Web3Agent({
    "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY",
    "solana_provider": "https://api.mainnet-beta.solana.com",
    "
