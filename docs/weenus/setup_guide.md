# Weenus AI Web3 Module Setup Guide

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
    "ipfs": {
        "gateway": "https://ipfs.io/ipfs/"
    },
    "memory_path": "./web3_agent_memory"
})
```

## Getting Blockchain Provider API Keys

For optimal performance and reliability, we recommend using dedicated blockchain provider services with API keys:

### Ethereum Providers

1. **Alchemy**
   - Visit [alchemy.com](https://www.alchemy.com/)
   - Sign up for a free account
   - Create a new app and select the Ethereum network
   - Copy the API key
   
2. **Infura**
   - Visit [infura.io](https://www.infura.io/)
   - Sign up for a free account
   - Create a new project
   - Copy the project ID or endpoint URL

3. **QuickNode**
   - Visit [quicknode.com](https://www.quicknode.com/)
   - Sign up for an account
   - Create a new endpoint for Ethereum
   - Copy the HTTP provider URL

### Solana Providers

1. **Helius**
   - Visit [helius.xyz](https://www.helius.xyz/)
   - Sign up for an account
   - Create an API key
   - Use the provided RPC URL

2. **QuickNode**
   - Visit [quicknode.com](https://www.quicknode.com/)
   - Sign up for an account
   - Create a new endpoint for Solana
   - Copy the HTTP provider URL

### Free Public Endpoints

If you're just testing or have low usage requirements, you can use public RPC endpoints:

- Ethereum Mainnet: `https://eth-mainnet.public.blastapi.io`
- Ethereum Sepolia: `https://ethereum-sepolia.publicnode.com`
- Solana Mainnet: `https://api.mainnet-beta.solana.com`
- Solana Devnet: `https://api.devnet.solana.com`

*Note: Public endpoints may have rate limits and reliability issues. For production use, we recommend dedicated providers.*

## Verifying Your Setup

To verify that your Web3 module is properly set up, you can run the following example:

```python
from anus.web3 import Web3Agent

def test_web3_setup():
    # Initialize Web3 agent with configuration
    agent = Web3Agent({
        "ethereum_provider": "YOUR_ETHEREUM_PROVIDER",
    })
    
    # Connect to Ethereum
    result = agent.connect_wallet("ethereum")
    print(f"Ethereum connection: {result.get('status', 'failed')}")
    print(f"Current block number: {result.get('block_number')}")
    
    # Check a wallet balance
    vitalik_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    balance = agent.token_balance(vitalik_address)
    print(f"Balance: {balance.get('balance')} ETH")
    
    return result["status"] == "connected"

if __name__ == "__main__":
    if test_web3_setup():
        print("Web3 setup successful!")
    else:
        print("Web3 setup failed. Check your configuration.")
```

## Setting Up Web3Society

The Web3Society provides multi-agent collaboration for complex Web3 tasks. To set it up:

```python
from anus.web3 import Web3Society

# Initialize Web3Society with configuration
society = Web3Society({
    "ethereum_provider": "YOUR_ETHEREUM_PROVIDER",
    "memory_path": "./web3_society_memory",
    "coordination_strategy": "hierarchical"  # or "consensus"
})

# Use the society for complex tasks
result = society.analyze_wallet("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
print(result["analysis"])
```

## Advanced Configuration

### Multiple Network Support

To support multiple networks and network types:

```yaml
web3:
  providers:
    ethereum:
      mainnet: "https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
      sepolia: "https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY"
      optimism: "https://opt-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
      arbitrum: "https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
      polygon: "https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
    solana:
      mainnet: "https://api.mainnet-beta.solana.com"
      devnet: "https://api.devnet.solana.com"
```

### IPFS Configuration

For IPFS operations, you can configure multiple gateways for redundancy:

```yaml
web3:
  ipfs:
    primary_gateway: "https://ipfs.io/ipfs/"
    backup_gateways:
      - "https://cloudflare-ipfs.com/ipfs/"
      - "https://gateway.pinata.cloud/ipfs/"
      - "https://ipfs.fleek.co/ipfs/"
    timeout: 10  # Timeout in seconds
```

### Memory Configuration

For persistent memory across sessions:

```yaml
web3:
  memory:
    type: "persistent"
    path: "./web3_memory"
    max_items: 1000
    ttl: 86400  # Time to live in seconds (24 hours)
```

## Troubleshooting

### Common Issues

#### Connection Problems

**Issue**: Cannot connect to blockchain networks
**Solution**:
1. Check your internet connection
2. Verify your API keys and provider URLs
3. Ensure your provider service is active and within usage limits
4. Try a different provider or public endpoint

#### Transaction Failures

**Issue**: Transactions fail or timeout
**Solution**:
1. Check wallet balance for sufficient funds
2. Verify gas parameters (limit, price)
3. Ensure private key is correct and has permissions
4. Check for network congestion and adjust gas accordingly

#### IPFS Content Not Loading

**Issue**: Cannot retrieve content from IPFS
**Solution**:
1. Verify the CID is correct
2. Try a different IPFS gateway
3. Check if the content is actually pinned on IPFS
4. Increase timeout settings

### Diagnostic Tools

The Web3 module includes several diagnostic tools:

```python
from anus.web3 import Web3Agent

agent = Web3Agent()

# Test provider connection
connection_test = agent.run_tool("web3_connection", {
    "network": "ethereum",
    "action": "diagnostic"
})
print(connection_test)

# Test IPFS connectivity
ipfs_test = agent.run_tool("ipfs", {
    "action": "test_gateway"
})
print(ipfs_test)
```

## Next Steps

Now that you have set up the Web3 module, you can:

1. Explore the [API Reference](api_reference.md) for detailed documentation of all features
2. Check out the example scripts in the `examples/web3/` directory
3. Try the tutorials for common Web3 tasks
4. Experiment with the Web3Society for complex blockchain tasks

For more information, see the [Web3 Integration Plan](integration_plan.md) to understand current and future capabilities of the module.

## Getting Help

If you encounter issues with the Web3 module:

1. Check this documentation and the API reference
2. Look for similar issues in the GitHub repository
3. Join the Discord community for real-time help
4. Open an issue on GitHub for bugs or feature requests
