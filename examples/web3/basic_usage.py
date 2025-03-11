"""
Anus AI Web3 Module - Basic Usage Examples

This script demonstrates basic usage of the Anus AI Web3 module,
including connecting to blockchain networks, querying token balances,
interacting with smart contracts, and using ENS services.

Usage:
    python basic_usage.py

Note: You need appropriate API keys for blockchain providers in your configuration.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union

# Add the parent directory to the path to allow running this script directly
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.append(parent_dir)

# Import Anus AI components
from anus.web3 import Web3Agent
from anus.web3.utils import wei_to_eth, eth_to_wei, is_eth_address

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# Configuration
# =========================

# You can provide configuration here or use a config file
CONFIG = {
    "ethereum_provider": os.environ.get("ETHEREUM_PROVIDER", "https://eth-mainnet.g.alchemy.com/v2/demo"),
    "solana_provider": os.environ.get("SOLANA_PROVIDER", "https://api.mainnet-beta.solana.com"),
    "ipfs": {
        "gateway": "https://ipfs.io/ipfs/"
    },
    "memory_path": "./web3_agent_memory"
}

# =========================
# Example Functions
# =========================

def example_connect_to_networks():
    """Example: Connect to different blockchain networks."""
    logger.info("=== Example: Connect to Networks ===")
    
    # Initialize Web3 agent
    agent = Web3Agent(CONFIG)
    
    # Connect to Ethereum Mainnet
    eth_result = agent.connect_wallet("ethereum")
    logger.info(f"Ethereum connection: {eth_result.get('status', 'failed')}")
    logger.info(f"Current Ethereum block: {eth_result.get('block_number')}")
    
    # Connect to Ethereum Sepolia testnet
    sepolia_result = agent.connect_wallet("ethereum", "sepolia")
    logger.info(f"Sepolia testnet connection: {sepolia_result.get('status', 'failed')}")
    
    # Connect to Solana
    sol_result = agent.connect_wallet("solana")
    logger.info(f"Solana connection: {sol_result.get('status', 'failed')}")
    
    return agent

def example_check_balances(agent: Web3Agent):
    """Example: Check token balances."""
    logger.info("\n=== Example: Check Balances ===")
    
    # Vitalik's address (example)
    vitalik_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    # Check ETH balance
    eth_balance = agent.token_balance(vitalik_address)
    if "error" not in eth_balance:
        logger.info(f"ETH Balance: {eth_balance['balance']} ETH")
    else:
        logger.error(f"Error getting ETH balance: {eth_balance['error']}")
    
    # Check USDC balance (USDC contract: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48)
    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    usdc_balance = agent.token_balance(vitalik_address, usdc_address)
    if "error" not in usdc_balance:
        logger.info(f"USDC Balance: {usdc_balance['balance']} USDC")
    else:
        logger.error(f"Error getting USDC balance: {usdc_balance['error']}")
    
    return {
        "address": vitalik_address,
        "eth_balance": eth_balance,
        "usdc_balance": usdc_balance
    }

def example_token_info(agent: Web3Agent):
    """Example: Get token information."""
    logger.info("\n=== Example: Token Information ===")
    
    # USDC token contract
    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    
    # Get token info
    token_info = agent.token_info(usdc_address)
    if "error" not in token_info:
        logger.info(f"Token Name: {token_info.get('name')}")
        logger.info(f"Token Symbol: {token_info.get('symbol')}")
        logger.info(f"Token Decimals: {token_info.get('decimals')}")
        logger.info(f"Token Supply: {token_info.get('total_supply')}")
    else:
        logger.error(f"Error getting token info: {token_info['error']}")
    
    return token_info

def example_ens_operations(agent: Web3Agent):
    """Example: ENS operations."""
    logger.info("\n=== Example: ENS Operations ===")
    
    # Resolve ENS name
    ens_name = "vitalik.eth"
    resolve_result = agent.resolve_ens(ens_name)
    if "error" not in resolve_result:
        logger.info(f"Resolved {ens_name} to: {resolve_result['address']}")
    else:
        logger.error(f"Error resolving ENS name: {resolve_result['error']}")
    
    # Lookup ENS name for address
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    lookup_result = agent.lookup_ens(address)
    if "error" not in lookup_result:
        logger.info(f"Address {address} has ENS name: {lookup_result['name']}")
    else:
        logger.error(f"Error looking up ENS name: {lookup_result['error']}")
    
    return {
        "resolve": resolve_result,
        "lookup": lookup_result
    }

def example_contract_interaction(agent: Web3Agent):
    """Example: Smart contract interaction."""
    logger.info("\n=== Example: Contract Interaction ===")
    
    # USDC contract address
    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    
    # Simple ERC20 ABI (only for totalSupply and decimals)
    abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    # Call totalSupply function
    supply_result = agent.call_contract(
        contract_address=usdc_address,
        method_name="totalSupply",
        args=[],
        contract_abi=abi
    )
    
    # Call decimals function
    decimals_result = agent.call_contract(
        contract_address=usdc_address,
        method_name="decimals",
        args=[],
        contract_abi=abi
    )
    
    if "error" not in supply_result and "error" not in decimals_result:
        # Format total supply
        decimals = decimals_result["result"]
        total_supply = supply_result["result"] / (10 ** decimals)
        logger.info(f"USDC Total Supply: {total_supply:,.2f} USDC")
    else:
        error = supply_result.get("error") or decimals_result.get("error")
        logger.error(f"Error calling contract: {error}")
    
    return {
        "supply_result": supply_result,
        "decimals_result": decimals_result
    }

def example_ipfs_content(agent: Web3Agent):
    """Example: Retrieve content from IPFS."""
    logger.info("\n=== Example: IPFS Content ===")
    
    # Example CID for the IPFS docs
    cid = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"
    
    # Get content
    result = agent.get_ipfs_content(cid)
    
    if "error" not in result:
        logger.info(f"Retrieved content from IPFS (size: {result.get('size', 0)} bytes)")
        logger.info(f"Content type: {result.get('content_type')}")
        
        # Display a preview of the content
        content = result.get("content")
        if isinstance(content, dict):
            logger.info(f"Content (JSON): {json.dumps(content, indent=2)[:200]}...")
        elif isinstance(content, str):
            logger.info(f"Content (text): {content[:200]}...")
        else:
            logger.info(f"Content: [binary data or unknown format]")
    else:
        logger.error(f"Error retrieving IPFS content: {result['error']}")
    
    return result

def example_wallet_analysis(agent: Web3Agent):
    """Example: Analyze a wallet."""
    logger.info("\n=== Example: Wallet Analysis ===")
    
    # Vitalik's address (example)
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    
    # Get wallet status across networks
    wallet_status = agent.wallet_status(address, networks=["ethereum"])
    
    # Display the results
    logger.info(f"Wallet analysis for {address}:")
    for network, status in wallet_status.items():
        logger.info(f"  Network: {network}")
        
        if "native_balance" in status and status["native_balance"]:
            balance = status["native_balance"].get("balance")
            symbol = status["native_balance"].get("symbol")
            logger.info(f"  Native Balance: {balance} {symbol}")
        
        if "ens_name" in status:
            logger.info(f"  ENS Name: {status['ens_name']}")
    
    return wallet_status

# =========================
# Main Function
# =========================

def main():
    """Run all examples."""
    try:
        # Connect to networks
        agent = example_connect_to_networks()
        
        # Run basic examples
        example_check_balances(agent)
        example_token_info(agent)
        example_ens_operations(agent)
        example_contract_interaction(agent)
        example_ipfs_content(agent)
        example_wallet_analysis(agent)
        
        logger.info("\nAll examples completed successfully!")
    except Exception as e:
        logger.error(f"Error running examples: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
