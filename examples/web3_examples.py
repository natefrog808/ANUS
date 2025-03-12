"""
Anus AI Web3 Integration - Usage Examples

This module provides examples of how to use the Web3 integration with Anus AI.
"""

# ================= Basic Web3 Agent Usage Examples =================

def example_wallet_balance():
    """Example: Check wallet balance."""
    from anus.web3 import Web3Agent

    # Initialize Web3 agent with configuration
    agent = Web3Agent({
        "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    })

    # Connect to Ethereum network
    connection = agent.connect_wallet("ethereum")
    print(f"Connection status: {connection['status']}")

    # Check wallet balance
    address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"  # vitalik.eth
    balance = agent.token_balance(address)
    print(f"ETH Balance: {balance['balance']} {balance['symbol']}")

    # Check ERC-20 token balance (e.g., USDC)
    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC contract
    token_balance = agent.token_balance(address, usdc_address)
    if "error" not in token_balance:
        print(f"Token Balance: {token_balance['balance']} {token_balance['symbol']}")
    else:
        print(f"Error checking token balance: {token_balance['error']}")

    # Resolve ENS name
    ens_result = agent.resolve_ens("vitalik.eth")
    if "error" not in ens_result:
        print(f"ENS Resolution: vitalik.eth => {ens_result['address']}")
    else:
        print(f"Error resolving ENS: {ens_result['error']}")


def example_nft_metadata():
    """Example: Get NFT metadata."""
    from anus.web3 import Web3Agent

    # Initialize Web3 agent
    agent = Web3Agent({
        "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    })

    # Connect to Ethereum network
    agent.connect_wallet("ethereum")

    # Check NFT metadata (e.g., CryptoPunk #7804)
    contract_address = "0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB"  # CryptoPunks
    token_id = 7804
    nft_info = agent.nft_info(contract_address, token_id)

    if "error" not in nft_info:
        print(f"NFT Owner: {nft_info['owner']}")
        print(f"Token URI: {nft_info['token_uri']}")
        if nft_info.get('metadata'):
            print(f"Name: {nft_info['metadata'].get('name')}")
            print(f"Description: {nft_info['metadata'].get('description')}")
            print(f"Image: {nft_info['metadata'].get('image')}")
    else:
        print(f"Error getting NFT info: {nft_info['error']}")


def example_smart_contract_interaction():
    """Example: Interact with a smart contract."""
    from anus.web3 import Web3Agent

    # Initialize Web3 agent
    agent = Web3Agent({
        "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    })

    # Connect to Ethereum network
    agent.connect_wallet("ethereum")

    # Example: Read total supply of USDC
    usdc_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    abi_fragment = [
        {
            "constant": True,
            "inputs": [],
            "name": "totalSupply",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        }
    ]

    # Get total supply
    result = agent.run_tool("smart_contract", {
        "network": "ethereum",
        "action": "read",
        "contract_address": usdc_address,
        "contract_abi": abi_fragment,
        "method_name": "totalSupply",
        "args": []
    })

    # Get decimals
    decimals_result = agent.run_tool("smart_contract", {
        "network": "ethereum",
        "action": "read",
        "contract_address": usdc_address,
        "contract_abi": abi_fragment,
        "method_name": "decimals",
        "args": []
    })

    if "error" not in result and "error" not in decimals_result:
        decimals = decimals_result["result"]
        total_supply = result["result"] / (10 ** decimals)
        print(f"USDC Total Supply: {total_supply:,.2f} USDC")
    else:
        print(f"Error reading contract: {result.get('error') or decimals_result.get('error')}")


def example_ipfs_content():
    """Example: Retrieve content from IPFS."""
    from anus.web3 import Web3Agent, IPFSTool

    # Initialize IPFS tool directly
    ipfs_tool = IPFSTool()

    # Get content from IPFS (e.g., a JSON metadata file)
    # Using the IPFS CID for the "Hello World" example
    result = ipfs_tool._execute({
        "action": "get",
        "cid": "QmZ4tDuvesekSs4qM5ZBKpXiZGun7S2CYtEZRB3DYXkjGx"
    })

    if "error" not in result:
        print(f"Content Type: {result.get('content_type')}")
        print(f"Content: {result.get('content')}")
    else:
        print(f"Error retrieving IPFS content: {result['error']}")


# ================= Advanced Web3 Integration Examples =================

def example_web3_society():
    """Example: Create a Web3-capable agent society."""
    from anus.web3 import Web3Agent
    from anus.agents import Agent
    from anus.society import Society

    # Create specialized agents
    web3_agent = Web3Agent({
        "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    })
    
    research_agent = Agent(role="researcher", tools=["search", "browser"])
    analysis_agent = Agent(role="analyst", tools=["code", "document"])
    
    # Create a society with these agents
    society = Society(
        agents=[web3_agent, research_agent, analysis_agent],
        coordination_strategy="consensus"
    )
    
    # Example task that requires Web3 capabilities and research
    response = society.run(
        "Research the impact of Ethereum's move to Proof of Stake on energy consumption, "
        "analyze the data, and check the current total validators on the Ethereum network."
    )
    
    print(response)


def example_token_transfer():
    """Example: Transfer tokens (WARNING: This would use real funds if used with a valid private key)."""
    from anus.web3 import Web3Agent

    # Initialize Web3 agent
    agent = Web3Agent({
        "ethereum_provider": "https://eth-goerli.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"  # Using testnet!
    })

    # Connect to Ethereum Goerli testnet
    agent.connect_wallet("ethereum")

    # WARNING: This is just an example, never put real private keys in code
    # For educational purposes only - this is not a real private key
    address = "0xYourTestnetAddress"
    private_key = "0xYourTestnetPrivateKey" 
    to_address = "0xRecipientTestnetAddress"
    
    # Check balance before transfer
    balance_before = agent.token_balance(address)
    print(f"Balance before transfer: {balance_before['balance']} ETH")
    
    # Transfer a small amount of ETH (on testnet)
    result = agent.run_tool("token", {
        "network": "ethereum",
        "action": "transfer",
        "address": address,
        "to_address": to_address,
        "amount": "0.001",  # Small amount for testing
        "private_key": private_key
    })
    
    if "error" not in result:
        print(f"Transfer successful! Transaction hash: {result['transaction_hash']}")
        print(f"From: {result['from']}")
        print(f"To: {result['to']}")
        print(f"Amount: {result['amount']} {result['symbol']}")
    else:
        print(f"Transfer failed: {result['error']}")


def example_cli_usage():
    """Example of how to use Web3 integration from the command line."""
    # This would be implemented in the CLI module
    """
    # Check wallet balance
    anus web3 balance --address 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045
    
    # Resolve ENS name
    anus web3 ens-resolve --name vitalik.eth
    
    # Get NFT metadata
    anus web3 nft-info --contract 0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB --token-id 7804
    
    # Interactive Web3 mode
    anus web3 interactive
    """
    print("CLI examples (for documentation purposes)")


# ================= Web3 Task Automation Examples =================

def example_defi_monitoring():
    """Example: Monitoring DeFi positions."""
    from anus.web3 import Web3Agent
    import time
    
    def monitor_position(agent, address, price_threshold, check_interval=60):
        """Monitor a DeFi position and alert if conditions are met."""
        print(f"Starting position monitoring for {address}...")
        print(f"Will alert if price drops below {price_threshold}")
        
        while True:
            # This is a simplified example - real implementation would:
            # 1. Check actual price from a DEX or oracle
            # 2. Calculate position health
            # 3. Send alerts if thresholds are crossed
            
            # Simulate price check (in real scenario, would query Uniswap, Chainlink, etc.)
            current_price = 1800  # Simulated ETH price
            position_health = "good"
            
            print(f"Current price: ${current_price}, Position health: {position_health}")
            
            if current_price < price_threshold:
                print(f"ALERT: Price below threshold! Current: ${current_price}")
                # In a real implementation:
                # - Send notification (email, SMS, etc.)
                # - Take automated action (e.g., adjust position)
                break
                
            # Wait for next check
            print(f"Waiting {check_interval} seconds until next check...")
            time.sleep(check_interval)
    
    # Initialize Web3 agent
    agent = Web3Agent({
        "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    })
    
    # Connect to Ethereum
    agent.connect_wallet("ethereum")
    
    # Start monitoring with 5 second intervals (for demo purposes)
    # In a real scenario, would use longer intervals
    monitor_position(agent, "0xYourAddress", 1500, check_interval=5)


def example_event_monitoring():
    """Example: Monitoring blockchain events."""
    from anus.web3 import Web3Agent
    
    # Initialize Web3 agent
    agent = Web3Agent({
        "ethereum_provider": "https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY"
    })
    
    # Connect to Ethereum
    connection = agent.connect_wallet("ethereum")
    
    # In a real implementation, we would set up event filters and listeners
    # This is a placeholder for illustration purposes
    print("Setting up event monitoring...")
    print("Would monitor for Transfer events on specific contracts")
    print("Would set up listeners for new blocks")
    
    # Example event handler function
    def handle_transfer_event(from_address, to_address, amount):
        print(f"Transfer detected: {amount} from {from_address} to {to_address}")
        # Analyze the transfer, update database, send alert, etc.


# ================= Main Example Runner =================

def run_examples():
    """Run selected examples."""
    print("=== Web3 Integration Examples ===\n")
    
    # Run basic examples that don't require actual API keys
    print("\n--- Wallet Balance Example (Simulated Output) ---")
    print("Connection status: connected")
    print("ETH Balance: 279.356 ETH")
    print("Token Balance: 124.85 USDC")
    print("ENS Resolution: vitalik.eth => 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")
    
    print("\n--- NFT Metadata Example (Simulated Output) ---")
    print("NFT Owner: 0x6611fE9CdEF940A2714a4C6fF75985AB66bC90f8")
    print("Token URI: ipfs://QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/7804")
    print("Name: CryptoPunk #7804")
    print("Description: One of 10,000 unique CryptoPunks")
    print("Image: ipfs://QmcJMTboitFVH7TxRrQ6cZQdQPkpfLZTCqLsP6viJfmzWw")
    
    print("\n--- Smart Contract Example (Simulated Output) ---")
    print("USDC Total Supply: 49,975,437,518.27 USDC")
    
    print("\n--- IPFS Example (Simulated Output) ---")
    print("Content Type: text/plain")
    print("Content: Hello, IPFS!")
    
    print("\n=== Examples Completed ===")


if __name__ == "__main__":
    run_examples()
