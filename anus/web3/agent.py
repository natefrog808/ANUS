"""
Web3Agent for Anus AI

This module implements a specialized agent for Web3 operations, providing
a high-level interface for blockchain interactions, smart contract operations,
token management, and more.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
from decimal import Decimal

from anus.agents import Agent
from anus.tools import BaseTool
from anus.utils.logging import get_logger
from anus.core.config import ConfigDict

from anus.web3.tools import (
    Web3ConnectionTool,
    SmartContractTool,
    TokenTool,
    NFTTool,
    DeFiTool,
    ENSTool,
    IPFSTool
)

# Setup logger
logger = get_logger("anus.web3.agent")


class Web3Agent(Agent):
    """An agent specialized in Web3 interactions.
    
    The Web3Agent extends the base Agent class with specialized capabilities
    for interacting with blockchain networks, smart contracts, tokens, NFTs,
    and decentralized finance protocols.
    
    Attributes:
        connection_tool: Tool for managing blockchain network connections
        config: Configuration dictionary for the agent
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a Web3Agent with specialized Web3 tools.
        
        Args:
            config: Configuration dictionary for the agent and its tools
        """
        # Process configuration
        self.config = config or {}
        
        # Initialize the Web3 tools
        self.connection_tool = Web3ConnectionTool(self.config)
        self.contract_tool = SmartContractTool(self.connection_tool)
        self.token_tool = TokenTool(self.connection_tool, self.contract_tool)
        self.nft_tool = NFTTool(self.connection_tool, self.contract_tool)
        self.defi_tool = DeFiTool(self.connection_tool, self.contract_tool, self.token_tool)
        self.ens_tool = ENSTool(self.connection_tool)
        self.ipfs_tool = IPFSTool(self.config)
        
        # Create list of tools
        web3_tools = [
            self.connection_tool,
            self.contract_tool,
            self.token_tool,
            self.nft_tool,
            self.defi_tool,
            self.ens_tool,
            self.ipfs_tool
        ]
        
        # Set up memory configuration
        memory_config = {
            "type": self.config.get("memory_type", "persistent"),
            "path": self.config.get("memory_path", "./web3_agent_memory")
        }
        
        # Initialize the agent with Web3 tools
        super().__init__(
            role="web3_specialist",
            tools=web3_tools,
            memory_config=memory_config,
            config=self.config
        )
        
        # Set agent description
        self.description = (
            "Specialized agent for blockchain and Web3 interactions, capable of managing "
            "crypto wallets, interacting with smart contracts, analyzing tokens and NFTs, "
            "and executing DeFi operations."
        )
        
        logger.info("Web3Agent initialized with %d tools", len(web3_tools))
    
    def wallet_status(self, address: str, networks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive wallet status across multiple networks.
        
        Args:
            address: The wallet address to check
            networks: List of networks to check (defaults to ["ethereum"])
            
        Returns:
            Dict containing wallet status information for each network
        """
        if networks is None:
            networks = ["ethereum"]  # Default to Ethereum
        
        logger.info("Getting wallet status for %s on %s", address, ", ".join(networks))
        
        results = {}
        for network in networks:
            network_result = {}
            
            # Connect to network first
            connect_result = self.connect_wallet(network)
            if "error" in connect_result:
                network_result["status"] = "error"
                network_result["error"] = connect_result["error"]
                results[network] = network_result
                continue
            
            # Get native balance
            native_balance = self.run_tool("token", {
                "network": network,
                "action": "native_balance",
                "address": address
            })
            
            if "error" not in native_balance:
                network_result["native_balance"] = native_balance
            
            # For Ethereum, get ENS name if available
            if network == "ethereum":
                try:
                    ens_lookup = self.run_tool("ens", {
                        "action": "lookup",
                        "address": address
                    })
                    
                    if "error" not in ens_lookup:
                        network_result["ens_name"] = ens_lookup["name"]
                except Exception:
                    pass  # Ignore ENS errors
            
            results[network] = network_result
        
        return results
    
    def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific Web3 tool directly.
        
        Args:
            tool_name: The name of the tool to run
            params: The parameters to pass to the tool
            
        Returns:
            The result of the tool execution
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool._execute(params)
        
        logger.error("Tool not found: %s", tool_name)
        return {"error": f"Tool not found: {tool_name}"}
    
    def connect_wallet(self, network: str, network_type: str = "mainnet", provider_url: Optional[str] = None) -> Dict[str, Any]:
        """Connect to a specific blockchain network.
        
        Args:
            network: The blockchain network to connect to (e.g., "ethereum", "solana")
            network_type: The network type (e.g., "mainnet", "testnet")
            provider_url: Optional custom provider URL
            
        Returns:
            Connection result information
        """
        params = {
            "network": network,
            "network_type": network_type
        }
        
        if provider_url:
            params["provider_url"] = provider_url
        
        logger.info("Connecting to %s %s", network, network_type)
        return self.run_tool("web3_connection", params)
    
    def token_balance(self, address: str, token_address: Optional[str] = None, network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
        """Get token balance for an address.
        
        Args:
            address: The wallet address to check
            token_address: Optional ERC-20 token address (if None, gets native token balance)
            network: The blockchain network
            network_type: The network type
            
        Returns:
            Balance information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "address": address
        }
        
        if token_address:
            params["action"] = "token_balance"
            params["token_address"] = token_address
        else:
            params["action"] = "native_balance"
        
        logger.info(
            "Getting %s balance for %s on %s", 
            f"token {token_address}" if token_address else "native", 
            address, 
            network
        )
        return self.run_tool("token", params)
    
    def token_info(self, token_address: str, network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
        """Get detailed information about a token.
        
        Args:
            token_address: The token contract address
            network: The blockchain network
            network_type: The network type
            
        Returns:
            Token information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "token_info",
            "token_address": token_address
        }
        
        logger.info("Getting token info for %s on %s", token_address, network)
        return self.run_tool("token", params)
    
    def transfer_tokens(
        self, 
        from_address: str, 
        to_address: str, 
        amount: Union[str, float], 
        private_key: str,
        token_address: Optional[str] = None,
        network: str = "ethereum",
        network_type: str = "mainnet",
        **kwargs
    ) -> Dict[str, Any]:
        """Transfer tokens between addresses.
        
        Args:
            from_address: The sending address
            to_address: The receiving address
            amount: The amount to transfer
            private_key: The private key for the sending address
            token_address: Optional token address (if None, transfers native token)
            network: The blockchain network
            network_type: The network type
            **kwargs: Additional parameters for the transfer
            
        Returns:
            Transfer result information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "transfer",
            "address": from_address,
            "to_address": to_address,
            "amount": str(amount),
            "private_key": private_key
        }
        
        if token_address:
            params["token_address"] = token_address
        
        # Add any additional parameters
        for key, value in kwargs.items():
            params[key] = value
        
        token_type = f"token {token_address}" if token_address else "native"
        logger.info("Transferring %s %s from %s to %s on %s", amount, token_type, from_address, to_address, network)
        return self.run_tool("token", params)
    
    def approve_tokens(
        self,
        address: str,
        spender_address: str,
        amount: Union[str, float],
        token_address: str,
        private_key: str,
        network: str = "ethereum",
        network_type: str = "mainnet",
        **kwargs
    ) -> Dict[str, Any]:
        """Approve a spender to use tokens.
        
        Args:
            address: The token owner address
            spender_address: The address to approve
            amount: The amount to approve (or "unlimited")
            token_address: The token address
            private_key: The private key for the token owner
            network: The blockchain network
            network_type: The network type
            **kwargs: Additional parameters for the approval
            
        Returns:
            Approval result information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "approve",
            "address": address,
            "spender_address": spender_address,
            "amount": str(amount),
            "token_address": token_address,
            "private_key": private_key
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            params[key] = value
        
        logger.info("Approving %s tokens for spender %s on %s", amount, spender_address, network)
        return self.run_tool("token", params)
    
    def check_allowance(
        self,
        owner_address: str,
        spender_address: str,
        token_address: str,
        network: str = "ethereum",
        network_type: str = "mainnet"
    ) -> Dict[str, Any]:
        """Check token allowance for a spender.
        
        Args:
            owner_address: The token owner address
            spender_address: The spender address
            token_address: The token address
            network: The blockchain network
            network_type: The network type
            
        Returns:
            Allowance information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "allowance",
            "address": owner_address,
            "spender_address": spender_address,
            "token_address": token_address
        }
        
        logger.info("Checking allowance for %s to spend %s tokens", spender_address, token_address)
        return self.run_tool("token", params)
    
    def nft_info(
        self, 
        contract_address: str, 
        token_id: Union[int, str], 
        network: str = "ethereum", 
        network_type: str = "mainnet",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Get NFT information including metadata.
        
        Args:
            contract_address: The NFT contract address
            token_id: The token ID
            network: The blockchain network
            network_type: The network type
            force_refresh: Whether to force refresh cached data
            
        Returns:
            NFT information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "get_metadata",
            "contract_address": contract_address,
            "token_id": token_id,
            "force_refresh": force_refresh
        }
        
        logger.info("Getting NFT info for %s token ID %s on %s", contract_address, token_id, network)
        return self.run_tool("nft", params)
    
    def nft_owner(self, contract_address: str, token_id: Union[int, str], network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
        """Get the owner of an NFT.
        
        Args:
            contract_address: The NFT contract address
            token_id: The token ID
            network: The blockchain network
            network_type: The network type
            
        Returns:
            Owner information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "get_owner",
            "contract_address": contract_address,
            "token_id": token_id
        }
        
        logger.info("Getting NFT owner for %s token ID %s on %s", contract_address, token_id, network)
        return self.run_tool("nft", params)
    
    def transfer_nft(
        self,
        from_address: str,
        to_address: str,
        contract_address: str,
        token_id: Union[int, str],
        private_key: str,
        token_standard: str = "ERC721",
        network: str = "ethereum",
        network_type: str = "mainnet",
        **kwargs
    ) -> Dict[str, Any]:
        """Transfer an NFT.
        
        Args:
            from_address: The sending address
            to_address: The receiving address
            contract_address: The NFT contract address
            token_id: The token ID
            private_key: The private key for the sending address
            token_standard: The token standard (ERC721 or ERC1155)
            network: The blockchain network
            network_type: The network type
            **kwargs: Additional parameters for the transfer
            
        Returns:
            Transfer result information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "transfer",
            "address": from_address,
            "to_address": to_address,
            "contract_address": contract_address,
            "token_id": token_id,
            "private_key": private_key,
            "token_standard": token_standard
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            params[key] = value
        
        logger.info(
            "Transferring NFT %s token ID %s from %s to %s on %s", 
            contract_address, token_id, from_address, to_address, network
        )
        return self.run_tool("nft", params)
    
    def resolve_ens(self, name: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Resolve ENS name to address.
        
        Args:
            name: The ENS name to resolve
            force_refresh: Whether to force refresh cached data
            
        Returns:
            Resolution result
        """
        # Ensure connection to Ethereum mainnet
        self.connect_wallet("ethereum", "mainnet")
        
        params = {
            "action": "resolve",
            "name": name,
            "force_refresh": force_refresh
        }
        
        logger.info("Resolving ENS name %s", name)
        return self.run_tool("ens", params)
    
    def lookup_ens(self, address: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Lookup address to find ENS name.
        
        Args:
            address: The address to lookup
            force_refresh: Whether to force refresh cached data
            
        Returns:
            Lookup result
        """
        # Ensure connection to Ethereum mainnet
        self.connect_wallet("ethereum", "mainnet")
        
        params = {
            "action": "lookup",
            "address": address,
            "force_refresh": force_refresh
        }
        
        logger.info("Looking up ENS name for address %s", address)
        return self.run_tool("ens", params)
    
    def get_ipfs_content(self, cid: str, path: str = "", force_refresh: bool = False) -> Dict[str, Any]:
        """Get content from IPFS.
        
        Args:
            cid: The IPFS CID
            path: Optional path within the CID
            force_refresh: Whether to force refresh cached data
            
        Returns:
            Content information
        """
        params = {
            "action": "get",
            "cid": cid,
            "path": path,
            "force_refresh": force_refresh
        }
        
        logger.info("Getting IPFS content for CID %s", cid)
        return self.run_tool("ipfs", params)
    
    def add_to_ipfs(self, data: Any) -> Dict[str, Any]:
        """Add content to IPFS.
        
        Args:
            data: The data to add
            
        Returns:
            Result information
        """
        params = {
            "action": "add",
            "data": data
        }
        
        logger.info("Adding content to IPFS")
        return self.run_tool("ipfs", params)
    
    def swap_tokens(
        self,
        address: str,
        private_key: str,
        token_in: str,
        token_out: str,
        amount_in: Union[str, float],
        slippage: float = 0.5,
        protocol: str = "uniswap_v2",
        network: str = "ethereum",
        network_type: str = "mainnet",
        **kwargs
    ) -> Dict[str, Any]:
        """Swap tokens using a DEX.
        
        Args:
            address: The user address
            private_key: The private key
            token_in: The input token (address or symbol)
            token_out: The output token (address or symbol)
            amount_in: The input amount
            slippage: The allowed slippage percentage
            protocol: The DEX protocol to use
            network: The blockchain network
            network_type: The network type
            **kwargs: Additional parameters for the swap
            
        Returns:
            Swap result information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "swap",
            "protocol": protocol,
            "address": address,
            "private_key": private_key,
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": str(amount_in),
            "slippage": slippage
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            params[key] = value
        
        logger.info(
            "Swapping %s %s for %s on %s using %s", 
            amount_in, token_in, token_out, network, protocol
        )
        return self.run_tool("defi", params)
    
    def get_swap_quote(
        self,
        token_in: str,
        token_out: str,
        amount_in: Union[str, float],
        protocol: str = "uniswap_v2",
        network: str = "ethereum",
        network_type: str = "mainnet"
    ) -> Dict[str, Any]:
        """Get a swap quote from a DEX.
        
        Args:
            token_in: The input token (address or symbol)
            token_out: The output token (address or symbol)
            amount_in: The input amount
            protocol: The DEX protocol to use
            network: The blockchain network
            network_type: The network type
            
        Returns:
            Quote information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "get_swap_quote",
            "protocol": protocol,
            "token_in": token_in,
            "token_out": token_out,
            "amount_in": str(amount_in)
        }
        
        logger.info(
            "Getting swap quote for %s %s to %s on %s using %s", 
            amount_in, token_in, token_out, network, protocol
        )
        return self.run_tool("defi", params)
    
    def call_contract(
        self,
        contract_address: str,
        method_name: str,
        args: List[Any],
        contract_abi: List[Dict[str, Any]],
        network: str = "ethereum",
        network_type: str = "mainnet"
    ) -> Dict[str, Any]:
        """Call a smart contract read method.
        
        Args:
            contract_address: The contract address
            method_name: The method name to call
            args: The arguments to pass to the method
            contract_abi: The contract ABI
            network: The blockchain network
            network_type: The network type
            
        Returns:
            Call result information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "read",
            "contract_address": contract_address,
            "contract_abi": contract_abi,
            "method_name": method_name,
            "args": args
        }
        
        logger.info(
            "Calling contract %s method %s on %s", 
            contract_address, method_name, network
        )
        return self.run_tool("smart_contract", params)
    
    def send_contract_transaction(
        self,
        contract_address: str,
        method_name: str,
        args: List[Any],
        contract_abi: List[Dict[str, Any]],
        from_address: str,
        private_key: str,
        network: str = "ethereum",
        network_type: str = "mainnet",
        **kwargs
    ) -> Dict[str, Any]:
        """Send a smart contract write transaction.
        
        Args:
            contract_address: The contract address
            method_name: The method name to call
            args: The arguments to pass to the method
            contract_abi: The contract ABI
            from_address: The sender address
            private_key: The private key for the sender
            network: The blockchain network
            network_type: The network type
            **kwargs: Additional parameters for the transaction
            
        Returns:
            Transaction result information
        """
        # Ensure connection to the network
        self.connect_wallet(network, network_type)
        
        params = {
            "network": network,
            "network_type": network_type,
            "action": "write",
            "contract_address": contract_address,
            "contract_abi": contract_abi,
            "method_name": method_name,
            "args": args,
            "from_address": from_address,
            "private_key": private_key
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            params[key] = value
        
        logger.info(
            "Sending contract transaction to %s method %s on %s", 
            contract_address, method_name, network
        )
        return self.run_tool("smart_contract", params)
    
    def analyze_wallet(self, address: str, networks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform a comprehensive analysis of a wallet.
        
        Args:
            address: The wallet address to analyze
            networks: List of networks to analyze (defaults to ["ethereum"])
            
        Returns:
            Analysis information
        """
        if networks is None:
            networks = ["ethereum"]
        
        logger.info("Analyzing wallet %s on %s", address, ", ".join(networks))
        
        # Get basic status for all networks
        status = self.wallet_status(address, networks)
        
        # For Ethereum, perform additional analysis
        if "ethereum" in networks and "ethereum" in status:
            eth_status = status["ethereum"]
            
            # Get ENS name if available
            if "ens_name" in eth_status:
                eth_status["display_name"] = eth_status["ens_name"]
            else:
                # Format address for display
                eth_status["display_name"] = f"{address[:6]}...{address[-4:]}"
            
            # Add wallet age if possible (using first transaction timestamp)
            # This would require an external API or significant indexing capabilities
            
            # Add transaction count if possible
            # This would require an external API or significant indexing capabilities
        
        return {
            "address": address,
            "networks": networks,
            "status": status,
            "timestamp": int(time.time())
        }
