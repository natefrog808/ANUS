"""
Web3 Ecosystem Integration for Anus AI

This module extends the Anus AI framework with Web3 capabilities, 
allowing AI agents to interact with blockchain networks, smart contracts,
decentralized applications, and other Web3 technologies.
"""

import os
from typing import Dict, Any, List, Optional, Union
import json

from anus.tools import BaseTool
from anus.agents import Agent
from anus.core import memory
from anus.society import Society


# ================= Web3 Core Tools =================

class Web3BaseTool(BaseTool):
    """Base class for all Web3-related tools in Anus AI."""
    
    def __init__(self):
        super().__init__()
        self.category = "web3"


class Web3ConnectionTool(Web3BaseTool):
    """Tool for managing connections to various blockchain networks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.name = "web3_connection"
        self.description = "Connects to blockchain networks like Ethereum, Solana, etc."
        self.config = config or {}
        self._connections = {}
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the connection tool with the given parameters."""
        network = params.get("network", "ethereum")
        
        if network not in self._connections:
            # Import appropriate web3 library based on the network
            if network == "ethereum":
                from web3 import Web3
                # Connect to the specified network
                provider_url = params.get("provider_url", self.config.get("ethereum_provider", "https://eth-mainnet.alchemyapi.io/v2/your-api-key"))
                self._connections[network] = Web3(Web3.HTTPProvider(provider_url))
            elif network == "solana":
                from solana.rpc.api import Client
                provider_url = params.get("provider_url", self.config.get("solana_provider", "https://api.mainnet-beta.solana.com"))
                self._connections[network] = Client(provider_url)
            # Add support for other networks as needed
            
        return {
            "status": "connected" if self._is_connected(network) else "failed",
            "network": network,
            "block_number": self._get_block_number(network) if self._is_connected(network) else None
        }
    
    def _is_connected(self, network: str) -> bool:
        """Check if connected to the specified network."""
        if network not in self._connections:
            return False
        
        try:
            if network == "ethereum":
                return self._connections[network].is_connected()
            elif network == "solana":
                return self._connections[network].is_connected()
            # Add checks for other networks
            return False
        except Exception:
            return False
    
    def _get_block_number(self, network: str) -> Optional[int]:
        """Get the current block number for the specified network."""
        if not self._is_connected(network):
            return None
        
        try:
            if network == "ethereum":
                return self._connections[network].eth.block_number
            elif network == "solana":
                return self._connections[network].get_block_height().get("result")
            # Add support for other networks
            return None
        except Exception:
            return None


class SmartContractTool(Web3BaseTool):
    """Tool for interacting with smart contracts on various blockchains."""
    
    def __init__(self, connection_tool: Web3ConnectionTool):
        super().__init__()
        self.name = "smart_contract"
        self.description = "Interacts with smart contracts on blockchain networks"
        self.connection_tool = connection_tool
        self._contracts = {}
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute smart contract interactions."""
        network = params.get("network", "ethereum")
        action = params.get("action", "read")
        contract_address = params.get("contract_address")
        contract_abi = params.get("contract_abi")
        method_name = params.get("method_name")
        args = params.get("args", [])
        
        if not contract_address or not contract_abi or not method_name:
            return {"error": "Missing required parameters: contract_address, contract_abi, and method_name are required"}
        
        # Ensure connection to the network
        connection_result = self.connection_tool._execute({"network": network})
        if connection_result.get("status") != "connected":
            return {"error": f"Failed to connect to {network}"}
        
        # Create contract instance if it doesn't exist
        contract_key = f"{network}:{contract_address}"
        if contract_key not in self._contracts:
            try:
                if network == "ethereum":
                    web3 = self.connection_tool._connections[network]
                    self._contracts[contract_key] = web3.eth.contract(
                        address=web3.to_checksum_address(contract_address), 
                        abi=contract_abi
                    )
                # Add support for other networks
            except Exception as e:
                return {"error": f"Failed to create contract instance: {str(e)}"}
        
        # Interact with the contract
        try:
            contract = self._contracts[contract_key]
            
            if action == "read":
                # Call a read method (view/pure function)
                if network == "ethereum":
                    method = getattr(contract.functions, method_name)
                    result = method(*args).call()
                    # Convert complex objects to JSON-serializable format
                    if isinstance(result, (bytes, bytearray)):
                        result = "0x" + result.hex()
                    return {"result": result}
                # Add support for other networks
                
            elif action == "write":
                # Call a write method (transaction)
                if network == "ethereum":
                    # Additional parameters for transactions
                    from_address = params.get("from_address")
                    private_key = params.get("private_key")
                    
                    if not from_address or not private_key:
                        return {"error": "Missing required parameters for write action: from_address and private_key"}
                    
                    web3 = self.connection_tool._connections[network]
                    method = getattr(contract.functions, method_name)
                    
                    # Build the transaction
                    tx = method(*args).build_transaction({
                        'from': from_address,
                        'nonce': web3.eth.get_transaction_count(from_address),
                        'gas': params.get("gas", 2000000),
                        'gasPrice': params.get("gas_price", web3.eth.gas_price)
                    })
                    
                    # Sign and send the transaction
                    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    
                    return {
                        "transaction_hash": tx_hash.hex(),
                        "status": "pending"
                    }
                # Add support for other networks
                
        except Exception as e:
            return {"error": f"Contract interaction failed: {str(e)}"}
        
        return {"error": f"Unsupported action '{action}' or network '{network}'"}


class TokenTool(Web3BaseTool):
    """Tool for token-related operations like balances, transfers, and approvals."""
    
    def __init__(self, connection_tool: Web3ConnectionTool, contract_tool: SmartContractTool):
        super().__init__()
        self.name = "token"
        self.description = "Manages token operations like checking balances and transfers"
        self.connection_tool = connection_tool
        self.contract_tool = contract_tool
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute token operations."""
        network = params.get("network", "ethereum")
        action = params.get("action", "balance")
        token_address = params.get("token_address")
        address = params.get("address")
        
        if not address:
            return {"error": "Missing required parameter: address"}
        
        # Ensure connection to the network
        connection_result = self.connection_tool._execute({"network": network})
        if connection_result.get("status") != "connected":
            return {"error": f"Failed to connect to {network}"}
        
        try:
            if network == "ethereum":
                web3 = self.connection_tool._connections[network]
                
                if action == "native_balance":
                    # Get native token (ETH) balance
                    balance = web3.eth.get_balance(address)
                    return {
                        "address": address,
                        "balance": web3.from_wei(balance, "ether"),
                        "symbol": "ETH"
                    }
                
                elif action == "token_balance":
                    if not token_address:
                        return {"error": "Missing required parameter: token_address"}
                    
                    # Load ERC20 ABI for token balance check
                    erc20_abi = [
                        {
                            "constant": True,
                            "inputs": [{"name": "_owner", "type": "address"}],
                            "name": "balanceOf",
                            "outputs": [{"name": "balance", "type": "uint256"}],
                            "type": "function"
                        },
                        {
                            "constant": True,
                            "inputs": [],
                            "name": "decimals",
                            "outputs": [{"name": "", "type": "uint8"}],
                            "type": "function"
                        },
                        {
                            "constant": True,
                            "inputs": [],
                            "name": "symbol",
                            "outputs": [{"name": "", "type": "string"}],
                            "type": "function"
                        }
                    ]
                    
                    # Get token balance
                    balance_result = self.contract_tool._execute({
                        "network": network,
                        "action": "read",
                        "contract_address": token_address,
                        "contract_abi": erc20_abi,
                        "method_name": "balanceOf",
                        "args": [address]
                    })
                    
                    if "error" in balance_result:
                        return balance_result
                    
                    # Get token decimals
                    decimals_result = self.contract_tool._execute({
                        "network": network,
                        "action": "read",
                        "contract_address": token_address,
                        "contract_abi": erc20_abi,
                        "method_name": "decimals",
                        "args": []
                    })
                    
                    # Get token symbol
                    symbol_result = self.contract_tool._execute({
                        "network": network,
                        "action": "read",
                        "contract_address": token_address,
                        "contract_abi": erc20_abi,
                        "method_name": "symbol",
                        "args": []
                    })
                    
                    decimals = 18  # Default to 18 if we can't get decimals
                    if "error" not in decimals_result:
                        decimals = decimals_result["result"]
                    
                    symbol = "???"  # Default symbol if we can't get it
                    if "error" not in symbol_result:
                        symbol = symbol_result["result"]
                    
                    # Calculate human-readable balance
                    raw_balance = balance_result["result"]
                    balance = raw_balance / (10 ** decimals)
                    
                    return {
                        "address": address,
                        "token_address": token_address,
                        "balance": balance,
                        "raw_balance": str(raw_balance),
                        "symbol": symbol,
                        "decimals": decimals
                    }
                
                elif action == "transfer":
                    # Transfer tokens
                    to_address = params.get("to_address")
                    amount = params.get("amount")
                    private_key = params.get("private_key")
                    
                    if not to_address or not amount or not private_key:
                        return {"error": "Missing required parameters for transfer: to_address, amount, and private_key"}
                    
                    if token_address:
                        # ERC20 token transfer
                        erc20_abi = [
                            {
                                "constant": False,
                                "inputs": [
                                    {"name": "_to", "type": "address"},
                                    {"name": "_value", "type": "uint256"}
                                ],
                                "name": "transfer",
                                "outputs": [{"name": "", "type": "bool"}],
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
                        
                        # Get token decimals
                        decimals_result = self.contract_tool._execute({
                            "network": network,
                            "action": "read",
                            "contract_address": token_address,
                            "contract_abi": erc20_abi,
                            "method_name": "decimals",
                            "args": []
                        })
                        
                        decimals = 18  # Default to 18 if we can't get decimals
                        if "error" not in decimals_result:
                            decimals = decimals_result["result"]
                        
                        # Convert amount to token units
                        amount_in_units = int(float(amount) * (10 ** decimals))
                        
                        # Execute the transfer
                        return self.contract_tool._execute({
                            "network": network,
                            "action": "write",
                            "contract_address": token_address,
                            "contract_abi": erc20_abi,
                            "method_name": "transfer",
                            "args": [to_address, amount_in_units],
                            "from_address": address,
                            "private_key": private_key
                        })
                    else:
                        # Native token (ETH) transfer
                        amount_in_wei = web3.to_wei(amount, "ether")
                        
                        # Build the transaction
                        tx = {
                            'from': address,
                            'to': to_address,
                            'value': amount_in_wei,
                            'nonce': web3.eth.get_transaction_count(address),
                            'gas': params.get("gas", 21000),
                            'gasPrice': params.get("gas_price", web3.eth.gas_price)
                        }
                        
                        # Sign and send the transaction
                        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                        
                        return {
                            "transaction_hash": tx_hash.hex(),
                            "status": "pending",
                            "from": address,
                            "to": to_address,
                            "amount": amount,
                            "symbol": "ETH"
                        }
            
            # Add support for other networks
            
        except Exception as e:
            return {"error": f"Token operation failed: {str(e)}"}
        
        return {"error": f"Unsupported action '{action}' or network '{network}'"}


class NFTTool(Web3BaseTool):
    """Tool for NFT-related operations."""
    
    def __init__(self, connection_tool: Web3ConnectionTool, contract_tool: SmartContractTool):
        super().__init__()
        self.name = "nft"
        self.description = "Manages NFT operations like viewing metadata and transfers"
        self.connection_tool = connection_tool
        self.contract_tool = contract_tool
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NFT operations."""
        network = params.get("network", "ethereum")
        action = params.get("action", "get_owned")
        address = params.get("address")
        contract_address = params.get("contract_address")
        token_id = params.get("token_id")
        
        if not address:
            return {"error": "Missing required parameter: address"}
        
        # Ensure connection to the network
        connection_result = self.connection_tool._execute({"network": network})
        if connection_result.get("status") != "connected":
            return {"error": f"Failed to connect to {network}"}
        
        try:
            if network == "ethereum":
                if action == "get_metadata":
                    if not contract_address or token_id is None:
                        return {"error": "Missing required parameters: contract_address and token_id"}
                    
                    # Load ERC721 ABI for metadata
                    erc721_abi = [
                        {
                            "constant": True,
                            "inputs": [{"name": "tokenId", "type": "uint256"}],
                            "name": "tokenURI",
                            "outputs": [{"name": "", "type": "string"}],
                            "type": "function"
                        },
                        {
                            "constant": True,
                            "inputs": [{"name": "tokenId", "type": "uint256"}],
                            "name": "ownerOf",
                            "outputs": [{"name": "", "type": "address"}],
                            "type": "function"
                        }
                    ]
                    
                    # Get token URI
                    uri_result = self.contract_tool._execute({
                        "network": network,
                        "action": "read",
                        "contract_address": contract_address,
                        "contract_abi": erc721_abi,
                        "method_name": "tokenURI",
                        "args": [int(token_id)]
                    })
                    
                    if "error" in uri_result:
                        return uri_result
                    
                    # Get token owner
                    owner_result = self.contract_tool._execute({
                        "network": network,
                        "action": "read",
                        "contract_address": contract_address,
                        "contract_abi": erc721_abi,
                        "method_name": "ownerOf",
                        "args": [int(token_id)]
                    })
                    
                    token_uri = uri_result["result"]
                    
                    # Fetch metadata if URI is available
                    metadata = None
                    if token_uri:
                        if token_uri.startswith("ipfs://"):
                            # Convert IPFS URI to HTTP gateway URL
                            ipfs_cid = token_uri.replace("ipfs://", "")
                            token_uri = f"https://ipfs.io/ipfs/{ipfs_cid}"
                        
                        import requests
                        try:
                            response = requests.get(token_uri)
                            if response.status_code == 200:
                                metadata = response.json()
                        except Exception:
                            metadata = {"error": "Failed to fetch metadata"}
                    
                    return {
                        "contract_address": contract_address,
                        "token_id": token_id,
                        "token_uri": token_uri,
                        "owner": owner_result.get("result") if "error" not in owner_result else None,
                        "metadata": metadata
                    }
                
                elif action == "transfer":
                    if not contract_address or token_id is None:
                        return {"error": "Missing required parameters: contract_address and token_id"}
                    
                    to_address = params.get("to_address")
                    private_key = params.get("private_key")
                    
                    if not to_address or not private_key:
                        return {"error": "Missing required parameters for transfer: to_address and private_key"}
                    
                    # Load ERC721 ABI for transfer
                    erc721_abi = [
                        {
                            "constant": False,
                            "inputs": [
                                {"name": "from", "type": "address"},
                                {"name": "to", "type": "address"},
                                {"name": "tokenId", "type": "uint256"}
                            ],
                            "name": "transferFrom",
                            "outputs": [],
                            "type": "function"
                        }
                    ]
                    
                    # Execute the transfer
                    return self.contract_tool._execute({
                        "network": network,
                        "action": "write",
                        "contract_address": contract_address,
                        "contract_abi": erc721_abi,
                        "method_name": "transferFrom",
                        "args": [address, to_address, int(token_id)],
                        "from_address": address,
                        "private_key": private_key
                    })
            
            # Add support for other networks
            
        except Exception as e:
            return {"error": f"NFT operation failed: {str(e)}"}
        
        return {"error": f"Unsupported action '{action}' or network '{network}'"}


class DeFiTool(Web3BaseTool):
    """Tool for DeFi operations like swaps, lending, and liquidity provision."""
    
    def __init__(self, connection_tool: Web3ConnectionTool, contract_tool: SmartContractTool, token_tool: TokenTool):
        super().__init__()
        self.name = "defi"
        self.description = "Performs DeFi operations like swaps, lending, and liquidity management"
        self.connection_tool = connection_tool
        self.contract_tool = contract_tool
        self.token_tool = token_tool
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DeFi operations."""
        network = params.get("network", "ethereum")
        action = params.get("action")
        protocol = params.get("protocol", "uniswap")
        address = params.get("address")
        
        if not action or not address:
            return {"error": "Missing required parameters: action and address"}
        
        # Ensure connection to the network
        connection_result = self.connection_tool._execute({"network": network})
        if connection_result.get("status") != "connected":
            return {"error": f"Failed to connect to {network}"}
        
        try:
            if network == "ethereum":
                if action == "swap" and protocol == "uniswap":
                    token_in = params.get("token_in")
                    token_out = params.get("token_out")
                    amount_in = params.get("amount_in")
                    private_key = params.get("private_key")
                    
                    if not token_in or not token_out or not amount_in or not private_key:
                        return {"error": "Missing required parameters for swap: token_in, token_out, amount_in, and private_key"}
                    
                    # This is a simplified example - a real implementation would include:
                    # 1. Getting the actual Uniswap router address
                    # 2. Approving the router to spend tokens
                    # 3. Calling the swapExactTokensForTokens or similar function
                    # 4. Handling slippage, deadlines, etc.
                    
                    # For demonstration purposes, we'll return a placeholder
                    return {
                        "status": "not_implemented",
                        "message": "Swap functionality requires a complete DeFi protocol integration",
                        "details": {
                            "operation": "swap",
                            "protocol": protocol,
                            "token_in": token_in,
                            "token_out": token_out,
                            "amount_in": amount_in
                        }
                    }
                
                # Add other DeFi operations like lending, borrowing, staking, etc.
            
            # Add support for other networks
            
        except Exception as e:
            return {"error": f"DeFi operation failed: {str(e)}"}
        
        return {"error": f"Unsupported action '{action}', protocol '{protocol}', or network '{network}'"}


# ================= Web3 Advanced Tools =================

class ENSTool(Web3BaseTool):
    """Tool for Ethereum Name Service (ENS) operations."""
    
    def __init__(self, connection_tool: Web3ConnectionTool):
        super().__init__()
        self.name = "ens"
        self.description = "Handles Ethereum Name Service (ENS) operations"
        self.connection_tool = connection_tool
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ENS operations."""
        action = params.get("action", "resolve")
        name = params.get("name")
        address = params.get("address")
        
        if action == "resolve" and not name:
            return {"error": "Missing required parameter: name"}
        
        if action == "lookup" and not address:
            return {"error": "Missing required parameter: address"}
        
        # Ensure connection to Ethereum
        connection_result = self.connection_tool._execute({"network": "ethereum"})
        if connection_result.get("status") != "connected":
            return {"error": "Failed to connect to Ethereum"}
        
        try:
            web3 = self.connection_tool._connections["ethereum"]
            
            if action == "resolve":
                # Resolve ENS name to address
                address = web3.ens.address(name)
                if address and address != "0x0000000000000000000000000000000000000000":
                    return {
                        "name": name,
                        "address": address
                    }
                else:
                    return {"error": f"Could not resolve ENS name: {name}"}
            
            elif action == "lookup":
                # Lookup address to find ENS name
                ens_name = web3.ens.name(address)
                if ens_name:
                    return {
                        "address": address,
                        "name": ens_name
                    }
                else:
                    return {"error": f"No ENS name found for address: {address}"}
            
        except Exception as e:
            return {"error": f"ENS operation failed: {str(e)}"}
        
        return {"error": f"Unsupported action: {action}"}


class IPFSTool(Web3BaseTool):
    """Tool for IPFS operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.name = "ipfs"
        self.description = "Handles IPFS operations like content retrieval and pinning"
        self.config = config or {}
        self._client = None
        
    def _get_client(self):
        """Get or create an IPFS client."""
        if self._client is None:
            # First try to connect to local IPFS daemon
            try:
                import ipfshttpclient
                self._client = ipfshttpclient.connect()
                return self._client
            except Exception:
                pass
            
            # If local connection fails, use HTTP gateway for read operations
            self._client = "gateway"
        
        return self._client
    
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute IPFS operations."""
        action = params.get("action", "get")
        
        try:
            client = self._get_client()
            
            if action == "get":
                cid = params.get("cid")
                if not cid:
                    return {"error": "Missing required parameter: cid"}
                
                if client == "gateway":
                    # Use HTTP gateway
                    import requests
                    gateway_url = self.config.get("gateway_url", "https://ipfs.io/ipfs/")
                    url = f"{gateway_url}{cid}"
                    response = requests.get(url)
                    
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "")
                        
                        if "application/json" in content_type:
                            return {"content": response.json(), "content_type": content_type}
                        elif "text/" in content_type:
                            return {"content": response.text, "content_type": content_type}
                        else:
                            # Binary data
                            return {
                                "content": "Binary data (not displayed)",
                                "content_type": content_type,
                                "size": len(response.content)
                            }
                    else:
                        return {"error": f"Failed to retrieve content: HTTP {response.status_code}"}
                else:
                    # Use IPFS client
                    content = client.cat(cid)
                    
                    try:
                        # Try to parse as JSON
                        json_content = json.loads(content)
                        return {"content": json_content, "content_type": "application/json"}
                    except Exception:
                        # Not JSON, return as text if not too large
                        if len(content) > 1024 * 10:  # 10KB
                            return {
                                "content": "Binary or large text data (not displayed)",
                                "size": len(content)
                            }
                        else:
                            try:
                                text_content = content.decode("utf-8")
                                return {"content": text_content, "content_type": "text/plain"}
                            except Exception:
                                return {
                                    "content": "Binary data (not displayed)",
                                    "size": len(content)
                                }
            
            elif action == "add" and client != "gateway":
                data = params.get("data")
                if not data:
                    return {"error": "Missing required parameter: data"}
                
                # Add content to IPFS
                result = client.add_str(json.dumps(data) if isinstance(data, dict) else str(data))
                return {"cid": result["Hash"]}
            
            elif action == "pin" and client != "gateway":
                cid = params.get("cid")
                if not cid:
                    return {"error": "Missing required parameter: cid"}
                
                # Pin content to IPFS node
                client.pin.add(cid)
                return {"status": "pinned", "cid": cid}
            
        except Exception as e:
            return {"error": f"IPFS operation failed: {str(e)}"}
        
        return {"error": f"Unsupported action '{action}' or client type"}


# ================= Web3 Agent Integration =================

class Web3Agent(Agent):
    """An agent specialized in Web3 interactions."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Initialize the Web3 tools
        connection_tool = Web3ConnectionTool(config)
        contract_tool = SmartContractTool(connection_tool)
        token_tool = TokenTool(connection_tool, contract_tool)
        nft_tool = NFTTool(connection_tool, contract_tool)
        defi_tool = DeFiTool(connection_tool, contract_tool, token_tool)
        ens_tool = ENSTool(connection_tool)
        ipfs_tool = IPFSTool(config)
        
        # Create list of tools
        web3_tools = [
            connection_tool,
            contract_tool,
            token_tool,
            nft_tool,
            defi_tool,
            ens_tool,
            ipfs_tool
        ]
        
        # Initialize the agent with Web3 tools
        super().__init__(
            role="web3_specialist",
            tools=web3_tools,
            memory_config={
                "type": "persistent",
                "path": config.get("memory_path", "./web3_agent_memory") if config else "./web3_agent_memory"
            },
            config=config
        )
        
        # Store connection tool for direct access
        self.connection_tool = connection_tool
    
    def wallet_status(self, address: str, networks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive wallet status across multiple networks."""
        if networks is None:
            networks = ["ethereum"]  # Default to Ethereum
        
        results = {}
        for network in networks:
            # Get native balance
            native_balance = self.run_tool("token", {
                "network": network,
                "action": "native_balance",
                "address": address
            })
            
            results[network] = {
                "native_balance": native_balance if "error" not in native_balance else None
            }
            
            # For Ethereum, get ENS name if available
            if network == "ethereum":
                ens_lookup = self.run_tool("ens", {
                    "action": "lookup",
                    "address": address
                })
                
                if "error" not in ens_lookup:
                    results[network]["ens_name"] = ens_lookup["name"]
        
        return results
    
    def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific Web3 tool directly."""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool._execute(params)
        
        return {"error": f"Tool not found: {tool_name}"}
    
    def connect_wallet(self, network: str, provider_url: Optional[str] = None) -> Dict[str, Any]:
        """Connect to a specific blockchain network."""
        params = {"network": network}
        if provider_url:
            params["provider_url"] = provider_url
        
        return self.run_tool("web3_connection", params)
    
    def token_balance(self, address: str, token_address: Optional[str] = None, network: str = "ethereum") -> Dict[str, Any]:
        """Get token balance for an address."""
        params = {
            "network": network,
            "address": address
        }
        
        if token_address:
            params["action"] = "token_balance"
            params["token_address"] = token_address
        else:
            params["action"] = "native_balance"
        
        return self.run_tool("token", params)
    
    def nft_info(self, contract_address: str, token_id: Union[int, str], network: str = "ethereum") -> Dict[str, Any]:
        """Get NFT information including metadata."""
        params = {
            "network": network,
            "action": "get_metadata",
            "contract_address": contract_address,
            "token_id": token_id
        }
        
        return self.run_tool("nft", params)
    
    def resolve_ens(self, name: str) -> Dict[str, Any]:
        """Resolve ENS name to address."""
        params = {
            "action": "resolve",
            "name": name
        }
        
        return self.run_tool("ens", params)
