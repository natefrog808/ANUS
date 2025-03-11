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
        network_type = params.get("network_type", "mainnet")
        action = params.get("action")
        protocol = params.get("protocol", "uniswap_v2")
        
        # Validate parameters
        if not action:
            return self._format_error("Missing required parameter: action")
        
        # Ensure connection to the network
        connection = self.connection_tool.get_connection(network, network_type)
        if not connection:
            return self._format_error(f"Failed to add content to IPFS: {str(e)}")
    
    def _pin_content(self, cid: str) -> Dict[str, Any]:
        """Pin content in IPFS."""
        try:
            # Get client
            client = self._get_client()
            
            # Only proceed if we have a local client
            if client == "gateway":
                return self._format_error("Pinning content requires a local IPFS node")
            
            # Pin the content
            client.pin.add(cid)
            
            return {
                "cid": cid,
                "status": "pinned",
                "gateway_url": f"{self._gateway_url}{cid}"
            }
        except Exception as e:
            return self._format_error(f"Failed to pin content: {str(e)}")
"Failed to connect to {network} {network_type}")
        
        # Execute the appropriate action
        if network == "ethereum":
            if action == "swap" and protocol == "uniswap_v2":
                return self._safe_execute(self._eth_uniswap_swap, connection, params)
            elif action == "get_swap_quote" and protocol == "uniswap_v2":
                return self._safe_execute(self._eth_uniswap_quote, connection, params)
            elif action == "add_liquidity" and protocol == "uniswap_v2":
                return self._format_error("Liquidity provision implementation coming soon")
            elif action == "get_reserves" and protocol == "uniswap_v2":
                return self._safe_execute(self._eth_uniswap_reserves, connection, params)
            elif action == "supply" and protocol == "aave":
                return self._format_error("Aave supply implementation coming soon")
            elif action == "borrow" and protocol == "aave":
                return self._format_error("Aave borrow implementation coming soon")
            elif action == "get_user_data" and protocol == "aave":
                return self._safe_execute(self._eth_aave_user_data, connection, params)
            else:
                return self._format_error(f"Unsupported action '{action}' or protocol '{protocol}' for {network}")
        else:
            return self._format_error(f"DeFi operations for {network} not implemented")
    
    def _eth_uniswap_swap(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a swap on Uniswap V2."""
        try:
            # Get required parameters
            from_address = params.get("address")
            private_key = params.get("private_key")
            token_in = params.get("token_in")
            token_out = params.get("token_out")
            amount_in = params.get("amount_in")
            slippage = params.get("slippage", 0.5)  # Default slippage: 0.5%
            deadline_mins = params.get("deadline_mins", 20)  # Default deadline: 20 minutes
            
            # Validate required parameters
            if not from_address or not private_key:
                return self._format_error("Missing required parameters: address and private_key")
            
            if not token_in or not token_out or not amount_in:
                return self._format_error("Missing required parameters: token_in, token_out, and amount_in")
            
            # Ensure addresses are checksum addresses
            from_address = connection.to_checksum_address(from_address)
            
            # Get router address
            router_address = self.PROTOCOL_ADDRESSES["ethereum"]["uniswap_v2_router"]
            router_address = connection.to_checksum_address(router_address)
            
            # Handle ETH as input or output token
            is_eth_in = token_in.upper() in ["ETH", "WETH"]
            is_eth_out = token_out.upper() in ["ETH", "WETH"]
            
            # Get WETH address (using a common WETH address, could get this from the router)
            weth_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH on Ethereum mainnet
            
            # Create the path
            if is_eth_in:
                token_in_address = weth_address
                path = [weth_address]
            else:
                token_in_address = connection.to_checksum_address(token_in)
                path = [token_in_address]
            
            if is_eth_out:
                token_out_address = weth_address
                path.append(weth_address)
            else:
                token_out_address = connection.to_checksum_address(token_out)
                path.append(token_out_address)
            
            # Get token info for token_in
            if is_eth_in:
                decimals_in = 18  # ETH has 18 decimals
                symbol_in = "ETH"
            else:
                token_info = self.token_tool._get_token_info(connection, token_in_address)
                decimals_in = token_info.get("decimals", 18)
                symbol_in = token_info.get("symbol", "???")
            
            # Convert amount_in to token units
            amount_in_units = int(float(amount_in) * (10 ** decimals_in))
            
            # Get swap quote
            quote_result = self._eth_uniswap_quote(connection, {
                "token_in": token_in,
                "token_out": token_out,
                "amount_in": amount_in
            })
            
            if "error" in quote_result:
                return quote_result
            
            # Calculate minimum amount out with slippage
            amount_out = quote_result["amount_out"]
            amount_out_units = quote_result["amount_out_units"]
            min_amount_out_units = int(amount_out_units * (1 - slippage / 100))
            
            # Calculate deadline timestamp
            deadline = int(time.time() + (deadline_mins * 60))
            
            # For ETH -> Token swaps
            if is_eth_in:
                # Build the swap transaction using swapExactETHForTokens
                router_contract = connection.eth.contract(
                    address=router_address,
                    abi=self.UNISWAP_V2_ROUTER_ABI
                )
                
                # Get method
                swap_method = router_contract.functions.swapExactETHForTokens(
                    min_amount_out_units,
                    path,
                    from_address,
                    deadline
                )
                
                # Build transaction
                tx = swap_method.build_transaction({
                    'from': from_address,
                    'value': amount_in_units,
                    'nonce': connection.eth.get_transaction_count(from_address),
                    'gas': params.get("gas", 250000),
                    'gasPrice': params.get("gas_price", connection.eth.gas_price)
                })
                
                # Sign and send transaction
                signed_tx = connection.eth.account.sign_transaction(tx, private_key)
                tx_hash = connection.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "pending",
                    "from": from_address,
                    "token_in": "ETH",
                    "token_out": token_out,
                    "amount_in": amount_in,
                    "expected_out": amount_out,
                    "min_amount_out": amount_out * (1 - slippage / 100),
                    "slippage": slippage,
                    "deadline": deadline,
                    "network": "ethereum"
                }
            
            # For Token -> ETH swaps
            elif is_eth_out:
                # First approve router to spend tokens
                approve_result = self.token_tool._eth_approve(connection, {
                    "address": from_address,
                    "spender_address": router_address,
                    "amount": amount_in,
                    "token_address": token_in_address,
                    "private_key": private_key
                })
                
                if "error" in approve_result:
                    return approve_result
                
                # Build the swap transaction using swapExactTokensForETH
                router_contract = connection.eth.contract(
                    address=router_address,
                    abi=self.UNISWAP_V2_ROUTER_ABI
                )
                
                # Get method
                swap_method = router_contract.functions.swapExactTokensForETH(
                    amount_in_units,
                    min_amount_out_units,
                    path,
                    from_address,
                    deadline
                )
                
                # Build transaction
                tx = swap_method.build_transaction({
                    'from': from_address,
                    'nonce': connection.eth.get_transaction_count(from_address),
                    'gas': params.get("gas", 250000),
                    'gasPrice': params.get("gas_price", connection.eth.gas_price)
                })
                
                # Sign and send transaction
                signed_tx = connection.eth.account.sign_transaction(tx, private_key)
                tx_hash = connection.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "pending",
                    "from": from_address,
                    "token_in": token_in,
                    "token_out": "ETH",
                    "amount_in": amount_in,
                    "expected_out": amount_out,
                    "min_amount_out": amount_out * (1 - slippage / 100),
                    "slippage": slippage,
                    "deadline": deadline,
                    "approval_tx": approve_result.get("transaction_hash"),
                    "network": "ethereum"
                }
            
            # For Token -> Token swaps
            else:
                # First approve router to spend tokens
                approve_result = self.token_tool._eth_approve(connection, {
                    "address": from_address,
                    "spender_address": router_address,
                    "amount": amount_in,
                    "token_address": token_in_address,
                    "private_key": private_key
                })
                
                if "error" in approve_result:
                    return approve_result
                
                # Build the swap transaction using swapExactTokensForTokens
                router_contract = connection.eth.contract(
                    address=router_address,
                    abi=self.UNISWAP_V2_ROUTER_ABI
                )
                
                # Get method
                swap_method = router_contract.functions.swapExactTokensForTokens(
                    amount_in_units,
                    min_amount_out_units,
                    path,
                    from_address,
                    deadline
                )
                
                # Build transaction
                tx = swap_method.build_transaction({
                    'from': from_address,
                    'nonce': connection.eth.get_transaction_count(from_address),
                    'gas': params.get("gas", 250000),
                    'gasPrice': params.get("gas_price", connection.eth.gas_price)
                })
                
                # Sign and send transaction
                signed_tx = connection.eth.account.sign_transaction(tx, private_key)
                tx_hash = connection.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "pending",
                    "from": from_address,
                    "token_in": token_in,
                    "token_out": token_out,
                    "amount_in": amount_in,
                    "expected_out": amount_out,
                    "min_amount_out": amount_out * (1 - slippage / 100),
                    "slippage": slippage,
                    "deadline": deadline,
                    "approval_tx": approve_result.get("transaction_hash"),
                    "network": "ethereum"
                }
        except Exception as e:
            return self._format_error(f"Uniswap swap failed: {str(e)}")
    
    def _eth_uniswap_quote(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a swap quote from Uniswap V2."""
        try:
            # Get required parameters
            token_in = params.get("token_in")
            token_out = params.get("token_out")
            amount_in = params.get("amount_in")
            
            # Validate required parameters
            if not token_in or not token_out or not amount_in:
                return self._format_error("Missing required parameters: token_in, token_out, and amount_in")
            
            # This should call the Uniswap V2 pair contract to get reserves and calculate the output amount
            # For simplicity, returning a placeholder. Real implementation would:
            # 1. Get the pair address from the factory
            # 2. Get the reserves from the pair
            # 3. Calculate the output amount using the constant product formula
            
            # Placeholder code - not actual implementation
            expected_out = float(amount_in) * 0.98  # Placeholder assuming 2% price impact
            expected_out_units = int(float(expected_out) * (10 ** 18))  # Assuming 18 decimals
            
            return {
                "token_in": token_in,
                "token_out": token_out,
                "amount_in": float(amount_in),
                "amount_out": expected_out,
                "amount_out_units": expected_out_units,
                "price_impact": "2.00%",  # Placeholder
                "fee": "0.30%",  # Standard Uniswap V2 fee
                "route": [token_in, token_out],
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get swap quote: {str(e)}")
    
    def _eth_uniswap_reserves(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get reserves for a Uniswap V2 pair."""
        try:
            # Get required parameters
            token_a = params.get("token_a")
            token_b = params.get("token_b")
            
            # Validate required parameters
            if not token_a or not token_b:
                return self._format_error("Missing required parameters: token_a and token_b")
            
            # This is a placeholder for getting pair reserves
            # Real implementation would:
            # 1. Get factory contract
            # 2. Get pair address from factory
            # 3. Get reserves from pair
            
            return {
                "token_a": token_a,
                "token_b": token_b,
                "reserve_a": 1000000,  # Placeholder
                "reserve_b": 500000,   # Placeholder
                "price_a_in_b": 0.5,   # Placeholder
                "price_b_in_a": 2.0,   # Placeholder
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get pair reserves: {str(e)}")
    
    def _eth_aave_user_data(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Aave user data."""
        try:
            # Get required parameters
            address = params.get("address")
            
            # Validate required parameters
            if not address:
                return self._format_error("Missing required parameter: address")
            
            # Placeholder for Aave user data
            # Real implementation would call Aave's Protocol Data Provider
            
            return {
                "address": address,
                "total_collateral_eth": 10.5,      # Placeholder
                "total_debt_eth": 5.2,             # Placeholder
                "available_borrows_eth": 3.1,      # Placeholder
                "current_liquidation_threshold": 80,  # Placeholder (%)
                "ltv": 65,                         # Placeholder (%)
                "health_factor": 2.0,              # Placeholder
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get Aave user data: {str(e)}")


class ENSTool(Web3BaseTool):
    """Tool for Ethereum Name Service (ENS) operations."""
    
    def __init__(self, connection_tool: Web3ConnectionTool):
        super().__init__()
        self.name = "ens"
        self.description = "Handles Ethereum Name Service (ENS) operations"
        self.connection_tool = connection_tool
        self._cache = {}
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ENS operations."""
        action = params.get("action", "resolve")
        network = params.get("network", "ethereum")
        network_type = params.get("network_type", "mainnet")
        
        # ENS only works on Ethereum mainnet
        if network != "ethereum" or network_type != "mainnet":
            return self._format_error("ENS operations are only supported on Ethereum mainnet")
        
        # Validate parameters based on action
        if action == "resolve":
            name = params.get("name")
            if not name:
                return self._format_error("Missing required parameter: name")
            
            return self._safe_execute(self._resolve_name, name, params.get("force_refresh", False))
                
        elif action == "lookup":
            address = params.get("address")
            if not address:
                return self._format_error("Missing required parameter: address")
            
            return self._safe_execute(self._lookup_address, address, params.get("force_refresh", False))
            
        elif action == "get_text_record":
            name = params.get("name")
            key = params.get("key")
            if not name or not key:
                return self._format_error("Missing required parameters: name and key")
            
            return self._safe_execute(self._get_text_record, name, key)
            
        elif action == "get_content_hash":
            name = params.get("name")
            if not name:
                return self._format_error("Missing required parameter: name")
            
            return self._safe_execute(self._get_content_hash, name)
            
        else:
            return self._format_error(f"Unsupported action: {action}")
    
    def _resolve_name(self, name: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Resolve ENS name to address."""
        try:
            # Normalize name
            normalized_name = name.lower()
            
            # Check cache
            cache_key = f"resolve:{normalized_name}"
            if not force_refresh and cache_key in self._cache:
                return self._cache[cache_key]
            
            # Get Ethereum connection
            connection = self.connection_tool.get_connection("ethereum", "mainnet")
            if not connection:
                return self._format_error("Failed to connect to Ethereum mainnet")
            
            # Resolve name
            address = connection.ens.address(normalized_name)
            
            # Validate result
            if not address or address == "0x0000000000000000000000000000000000000000":
                return self._format_error(f"Could not resolve ENS name: {name}")
            
            # Create result
            result = {
                "name": normalized_name,
                "address": address,
                "network": "ethereum"
            }
            
            # Cache the result
            self._cache[cache_key] = result
            
            return result
        except Exception as e:
            return self._format_error(f"ENS resolution failed: {str(e)}")
    
    def _lookup_address(self, address: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Lookup address to find ENS name."""
        try:
            # Convert address to checksum format
            connection = self.connection_tool.get_connection("ethereum", "mainnet")
            if not connection:
                return self._format_error("Failed to connect to Ethereum mainnet")
            
            checksum_address = connection.to_checksum_address(address)
            
            # Check cache
            cache_key = f"lookup:{checksum_address}"
            if not force_refresh and cache_key in self._cache:
                return self._cache[cache_key]
            
            # Lookup name
            ens_name = connection.ens.name(checksum_address)
            
            # Validate result
            if not ens_name:
                return self._format_error(f"No ENS name found for address: {address}")
            
            # Create result
            result = {
                "address": checksum_address,
                "name": ens_name,
                "network": "ethereum"
            }
            
            # Cache the result
            self._cache[cache_key] = result
            
            return result
        except Exception as e:
            return self._format_error(f"ENS lookup failed: {str(e)}")
    
    def _get_text_record(self, name: str, key: str) -> Dict[str, Any]:
        """Get text record for an ENS name."""
        try:
            # Normalize name
            normalized_name = name.lower()
            
            # Get Ethereum connection
            connection = self.connection_tool.get_connection("ethereum", "mainnet")
            if not connection:
                return self._format_error("Failed to connect to Ethereum mainnet")
            
            # Get text record
            value = connection.ens.get_text(normalized_name, key)
            
            # Validate result
            if not value:
                return self._format_error(f"No text record found for {key} on {name}")
            
            return {
                "name": normalized_name,
                "key": key,
                "value": value,
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get text record: {str(e)}")
    
    def _get_content_hash(self, name: str) -> Dict[str, Any]:
        """Get content hash for an ENS name."""
        try:
            # Normalize name
            normalized_name = name.lower()
            
            # Get Ethereum connection
            connection = self.connection_tool.get_connection("ethereum", "mainnet")
            if not connection:
                return self._format_error("Failed to connect to Ethereum mainnet")
            
            # Get content hash
            # Note: This is a placeholder as web3.py might not directly support this
            # Real implementation would use the ENS resolver contract
            
            return {
                "name": normalized_name,
                "content_hash": "Content hash retrieval not implemented yet",
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get content hash: {str(e)}")


class IPFSTool(Web3BaseTool):
    """Tool for IPFS operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.name = "ipfs"
        self.description = "Handles IPFS operations like content retrieval and pinning"
        self.config = config or {}
        self._client = None
        self._gateway_url = self.config.get("gateway_url", "https://ipfs.io/ipfs/")
        self._cache = {}
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute IPFS operations."""
        action = params.get("action", "get")
        
        if action == "get":
            cid = params.get("cid")
            if not cid:
                return self._format_error("Missing required parameter: cid")
            
            return self._safe_execute(
                self._get_content, 
                cid, 
                params.get("path", ""), 
                params.get("force_refresh", False)
            )
            
        elif action == "add":
            data = params.get("data")
            if data is None:
                return self._format_error("Missing required parameter: data")
            
            return self._safe_execute(self._add_content, data)
            
        elif action == "pin":
            cid = params.get("cid")
            if not cid:
                return self._format_error("Missing required parameter: cid")
            
            return self._safe_execute(self._pin_content, cid)
            
        else:
            return self._format_error(f"Unsupported action: {action}")
    
    def _get_client(self):
        """Get or create an IPFS client."""
        if self._client is None:
            # Try to connect to local IPFS daemon
            try:
                import ipfshttpclient
                self._client = ipfshttpclient.connect()
                return self._client
            except Exception:
                # If local connection fails, use HTTP gateway for read operations
                self._client = "gateway"
        
        return self._client
    
    def _get_content(self, cid: str, path: str = "", force_refresh: bool = False) -> Dict[str, Any]:
        """Get content from IPFS."""
        try:
            # Normalize CID and path
            if path and not path.startswith("/"):
                path = "/" + path
            
            # Create cache key
            cache_key = f"{cid}{path}"
            
            # Check cache
            if not force_refresh and cache_key in self._cache:
                return self._cache[cache_key]
            
            # Get client
            client = self._get_client()
            
            # Handle gateway mode
            if client == "gateway":
                import requests
                
                # Prepare URL
                gateway_url = self._gateway_url
                if not gateway_url.endswith("/"):
                    gateway_url += "/"
                
                url = f"{gateway_url}{cid}{path}"
                
                # Fetch content
                response = requests.get(url, timeout=30)
                
                if response.status_code != 200:
                    return self._format_error(f"Failed to retrieve content: HTTP {response.status_code}")
                
                # Process response based on content type
                content_type = response.headers.get("content-type", "")
                
                result = {
                    "cid": cid,
                    "path": path,
                    "content_type": content_type,
                    "gateway_url": url,
                    "size": len(response.content)
                }
                
                # Process content based on type
                if "application/json" in content_type:
                    result["content"] = response.json()
                elif "text/" in content_type or "application/xml" in content_type:
                    result["content"] = response.text
                else:
                    # Binary data - just indicate it was retrieved
                    result["content"] = "[Binary data not displayed]"
                
                # Cache the result
                self._cache[cache_key] = result
                
                return result
            
            # Handle local IPFS client
            else:
                # Fetch from IPFS
                full_path = f"{cid}{path}"
                content = client.cat(full_path)
                
                # Try to determine content type and process accordingly
                result = {
                    "cid": cid,
                    "path": path,
                    "size": len(content)
                }
                
                # Try to parse as JSON
                try:
                    json_content = json.loads(content)
                    result["content"] = json_content
                    result["content_type"] = "application/json"
                except Exception:
                    # Try to decode as UTF-8
                    try:
                        text_content = content.decode("utf-8")
                        result["content"] = text_content
                        result["content_type"] = "text/plain"
                    except Exception:
                        # Binary data
                        result["content"] = "[Binary data not displayed]"
                        result["content_type"] = "application/octet-stream"
                
                # Cache the result
                self._cache[cache_key] = result
                
                return result
                
        except Exception as e:
            return self._format_error(f"Failed to get IPFS content: {str(e)}")
    
    def _add_content(self, data: Any) -> Dict[str, Any]:
        """Add content to IPFS."""
        try:
            # Get client
            client = self._get_client()
            
            # Only proceed if we have a local client
            if client == "gateway":
                return self._format_error("Adding content requires a local IPFS node")
            
            # Prepare data
            if isinstance(data, dict) or isinstance(data, list):
                # Convert to JSON string
                content = json.dumps(data).encode("utf-8")
            elif isinstance(data, str):
                # Convert string to bytes
                content = data.encode("utf-8")
            elif isinstance(data, bytes):
                # Already bytes
                content = data
            else:
                # Convert to string
                content = str(data).encode("utf-8")
            
            # Add to IPFS
            result = client.add_bytes(content)
            
            return {
                "cid": result,
                "size": len(content),
                "gateway_url": f"{self._gateway_url}{result}"
            }
        except Exception as e:
            return self._format_error(f"""
Web3 Tools for Anus AI

This module provides specialized tools for interacting with Web3 technologies,
including blockchain networks, smart contracts, tokens, NFTs, and more.

Each tool extends the BaseTool class from the Anus AI framework, implementing
the specific functionality needed for Web3 interactions.
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
from decimal import Decimal
from functools import lru_cache
from urllib.parse import urlparse

from anus.tools import BaseTool
from anus.utils.logging import get_logger
from anus.core.config import ConfigDict

# Setup logger
logger = get_logger("anus.web3.tools")


class Web3BaseTool(BaseTool):
    """Base class for all Web3-related tools in Anus AI."""
    
    def __init__(self):
        super().__init__()
        self.category = "web3"
        
    def _format_error(self, message: str, details: Optional[Any] = None) -> Dict[str, Any]:
        """Format error responses consistently."""
        error_dict = {"error": message}
        if details:
            error_dict["details"] = details
        logger.error(f"Web3 tool error: {message}")
        return error_dict
    
    def _safe_execute(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Safely execute a function with error handling."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            return self._format_error(str(e), traceback.format_exc())


class Web3ConnectionTool(Web3BaseTool):
    """Tool for managing connections to various blockchain networks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.name = "web3_connection"
        self.description = "Connects to blockchain networks like Ethereum, Solana, etc."
        self.config = config or {}
        self._connections = {}
        self._connection_status = {}
        self._connection_times = {}
        self._providers = self._setup_providers()
        
    def _setup_providers(self) -> Dict[str, Dict[str, str]]:
        """Setup provider URLs from config or use defaults."""
        from anus.web3 import DEFAULT_PROVIDERS
        
        providers = DEFAULT_PROVIDERS.copy()
        
        # Override with user-provided providers
        if "providers" in self.config:
            for network, network_providers in self.config["providers"].items():
                if network not in providers:
                    providers[network] = {}
                
                if isinstance(network_providers, str):
                    # Handle case where provider is a single string
                    providers[network]["mainnet"] = network_providers
                elif isinstance(network_providers, dict):
                    # Handle case where provider is a dict of networks
                    for net, url in network_providers.items():
                        providers[network][net] = url
        
        # Handle legacy config format for backward compatibility
        for network in ["ethereum", "solana"]:
            legacy_key = f"{network}_provider"
            if legacy_key in self.config:
                if network not in providers:
                    providers[network] = {}
                providers[network]["mainnet"] = self.config[legacy_key]
        
        return providers
    
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the connection tool with the given parameters."""
        network = params.get("network", "ethereum")
        network_type = params.get("network_type", "mainnet")
        force_reconnect = params.get("force_reconnect", False)
        
        # Check if network is supported
        if network not in self._providers:
            return self._format_error(f"Unsupported network: {network}")
        
        # Check if network type is available
        if network_type not in self._providers[network]:
            return self._format_error(
                f"Network type '{network_type}' not available for {network}. " 
                f"Available types: {', '.join(self._providers[network].keys())}"
            )
        
        # Create connection key
        connection_key = f"{network}:{network_type}"
        
        # Check if connection exists and is valid
        if not force_reconnect and connection_key in self._connections and self._is_connected(network, network_type):
            return {
                "status": "connected",
                "network": network,
                "network_type": network_type,
                "block_number": self._get_block_number(network, network_type),
                "connection_time": self._connection_times.get(connection_key),
                "provider": self._mask_provider_url(self._providers[network][network_type])
            }
        
        # Get provider URL
        provider_url = params.get("provider_url", self._providers[network][network_type])
        
        # Create new connection
        return self._safe_execute(self._create_connection, network, network_type, provider_url)
    
    def _create_connection(self, network: str, network_type: str, provider_url: str) -> Dict[str, Any]:
        """Create a new connection to the specified network."""
        connection_key = f"{network}:{network_type}"
        
        try:
            if network == "ethereum":
                from web3 import Web3
                
                # Connect to the specified network
                if provider_url.startswith(("http://", "https://")):
                    self._connections[connection_key] = Web3(Web3.HTTPProvider(provider_url))
                elif provider_url.startswith("ws://") or provider_url.startswith("wss://"):
                    self._connections[connection_key] = Web3(Web3.WebsocketProvider(provider_url))
                else:
                    # Try to connect to local node (IPC)
                    self._connections[connection_key] = Web3(Web3.IPCProvider(provider_url))
                    
                # Test connection by getting block number
                block_number = self._connections[connection_key].eth.block_number
                
            elif network == "solana":
                from solana.rpc.api import Client
                
                # Connect to Solana network
                self._connections[connection_key] = Client(provider_url)
                
                # Test connection by getting block height
                result = self._connections[connection_key].get_block_height()
                if "result" not in result:
                    raise Exception(f"Failed to connect to Solana network: {result}")
                block_number = result["result"]
                
            else:
                return self._format_error(f"Network {network} implementation not available")
            
            # Store connection time
            self._connection_times[connection_key] = time.time()
            
            # Store connection status
            self._connection_status[connection_key] = True
            
            # Return success
            return {
                "status": "connected",
                "network": network,
                "network_type": network_type,
                "block_number": block_number,
                "connection_time": self._connection_times[connection_key],
                "provider": self._mask_provider_url(provider_url)
            }
            
        except Exception as e:
            # Clean up failed connection
            if connection_key in self._connections:
                del self._connections[connection_key]
            
            self._connection_status[connection_key] = False
            
            return self._format_error(f"Failed to connect to {network} {network_type}: {str(e)}")
    
    def _is_connected(self, network: str, network_type: str = "mainnet") -> bool:
        """Check if connected to the specified network."""
        connection_key = f"{network}:{network_type}"
        
        if connection_key not in self._connections:
            return False
        
        # If we checked recently, use cached status
        if connection_key in self._connection_status:
            last_check_time = self._connection_times.get(connection_key, 0)
            if time.time() - last_check_time < 60:  # Cache connection status for 60 seconds
                return self._connection_status[connection_key]
        
        try:
            if network == "ethereum":
                is_connected = self._connections[connection_key].is_connected()
                self._connection_status[connection_key] = is_connected
                return is_connected
                
            elif network == "solana":
                # For Solana, try to get a simple RPC response
                result = self._connections[connection_key].get_health()
                is_connected = result.get("result") == "ok"
                self._connection_status[connection_key] = is_connected
                return is_connected
                
            return False
        except Exception:
            self._connection_status[connection_key] = False
            return False
    
    def _get_block_number(self, network: str, network_type: str = "mainnet") -> Optional[int]:
        """Get the current block number for the specified network."""
        connection_key = f"{network}:{network_type}"
        
        if not self._is_connected(network, network_type):
            return None
        
        try:
            if network == "ethereum":
                return self._connections[connection_key].eth.block_number
                
            elif network == "solana":
                result = self._connections[connection_key].get_block_height()
                return result.get("result")
                
            return None
        except Exception:
            return None
    
    def _mask_provider_url(self, provider_url: str) -> str:
        """Mask API keys in provider URLs for security."""
        try:
            parsed_url = urlparse(provider_url)
            
            # Check if URL contains an API key
            if "key" in parsed_url.query or "apikey" in parsed_url.query.lower():
                # Return with masked API key
                path = parsed_url.path
                if path and len(path) > 5:
                    path = path[:3] + "..." + path[-2:]
                return f"{parsed_url.scheme}://{parsed_url.netloc}{path}?...API_KEY_HIDDEN..."
            
            return provider_url
        except Exception:
            return provider_url
    
    def get_connection(self, network: str, network_type: str = "mainnet") -> Any:
        """Get the connection object for the specified network."""
        connection_key = f"{network}:{network_type}"
        
        if connection_key not in self._connections or not self._is_connected(network, network_type):
            result = self._execute({
                "network": network,
                "network_type": network_type,
            })
            
            if "error" in result:
                logger.error(f"Failed to get connection: {result['error']}")
                return None
        
        return self._connections.get(connection_key)


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
        network_type = params.get("network_type", "mainnet")
        action = params.get("action", "read")
        contract_address = params.get("contract_address")
        contract_abi = params.get("contract_abi")
        method_name = params.get("method_name")
        args = params.get("args", [])
        
        # Validate required parameters
        if not contract_address:
            return self._format_error("Missing required parameter: contract_address")
        
        if not contract_abi:
            return self._format_error("Missing required parameter: contract_abi")
        
        if not method_name:
            return self._format_error("Missing required parameter: method_name")
        
        # Ensure connection to the network
        connection = self.connection_tool.get_connection(network, network_type)
        if not connection:
            return self._format_error(f"Failed to connect to {network} {network_type}")
        
        # Create contract instance if it doesn't exist
        contract_key = f"{network}:{network_type}:{contract_address}"
        if contract_key not in self._contracts:
            try:
                if network == "ethereum":
                    # Create Ethereum contract instance
                    self._contracts[contract_key] = connection.eth.contract(
                        address=connection.to_checksum_address(contract_address), 
                        abi=contract_abi
                    )
                elif network == "solana":
                    # Solana contracts would need a different approach
                    return self._format_error("Solana smart contract support coming soon")
                else:
                    return self._format_error(f"Smart contract support for {network} not implemented")
            except Exception as e:
                return self._format_error(f"Failed to create contract instance: {str(e)}")
        
        # Get the contract instance
        contract = self._contracts[contract_key]
        
        # Execute the appropriate action
        if action == "read":
            return self._safe_execute(self._read_contract, contract, method_name, args, network)
        elif action == "write":
            # Additional required parameters for write operations
            from_address = params.get("from_address")
            if not from_address:
                return self._format_error("Missing required parameter for write action: from_address")
            
            # Execute write operation
            return self._safe_execute(
                self._write_contract,
                contract, 
                method_name, 
                args, 
                network, 
                network_type,
                connection, 
                from_address,
                params
            )
        else:
            return self._format_error(f"Unsupported action: {action}")
    
    def _read_contract(self, contract, method_name: str, args: List[Any], network: str) -> Dict[str, Any]:
        """Read data from a smart contract."""
        if network == "ethereum":
            # Get the method from the contract
            method = getattr(contract.functions, method_name)
            
            # Call the method with provided arguments
            result = method(*args).call()
            
            # Process the result to ensure it's JSON-serializable
            processed_result = self._process_contract_result(result)
            
            return {"result": processed_result}
        else:
            return self._format_error(f"Contract read for {network} not implemented")
    
    def _write_contract(
        self, 
        contract, 
        method_name: str, 
        args: List[Any], 
        network: str,
        network_type: str,
        connection,
        from_address: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write data to a smart contract (send transaction)."""
        if network == "ethereum":
            # Check for either private key or wallet connection
            private_key = params.get("private_key")
            use_wallet = params.get("use_wallet", False)
            
            if not private_key and not use_wallet:
                return self._format_error("Either private_key or use_wallet=True is required for write operations")
            
            # Get the method from the contract
            method = getattr(contract.functions, method_name)
            
            # Build transaction parameters
            tx_params = {
                'from': from_address,
                'nonce': connection.eth.get_transaction_count(from_address),
            }
            
            # Add gas parameters if provided
            if "gas" in params:
                tx_params["gas"] = params["gas"]
            
            if "gas_price" in params:
                tx_params["gasPrice"] = params["gas_price"]
            elif "max_fee_per_gas" in params:
                # EIP-1559 parameters
                tx_params["maxFeePerGas"] = params["max_fee_per_gas"]
                tx_params["maxPriorityFeePerGas"] = params.get("max_priority_fee_per_gas", 
                                                             params["max_fee_per_gas"] // 2)
            
            # Build the transaction
            tx = method(*args).build_transaction(tx_params)
            
            # Sign and send transaction
            if private_key:
                # Using provided private key
                signed_tx = connection.eth.account.sign_transaction(tx, private_key)
                tx_hash = connection.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "pending",
                    "from": from_address,
                    "network": network,
                    "network_type": network_type
                }
            elif use_wallet:
                # Using wallet connection (this would typically require a browser or other interface)
                # This is a placeholder - actual implementation would depend on the environment
                return self._format_error("Wallet connection for transactions not implemented in this context")
        else:
            return self._format_error(f"Contract write for {network} not implemented")
    
    def _process_contract_result(self, result: Any) -> Any:
        """Process contract call result to ensure it's JSON-serializable."""
        if isinstance(result, (int, float, str, bool, type(None))):
            return result
        elif isinstance(result, bytes):
            # Convert bytes to hex string
            return "0x" + result.hex()
        elif isinstance(result, Decimal):
            # Convert Decimal to string to preserve precision
            return str(result)
        elif isinstance(result, list):
            # Process each item in the list
            return [self._process_contract_result(item) for item in result]
        elif isinstance(result, tuple):
            # Convert named tuples to dictionaries
            if hasattr(result, '_asdict'):
                return {k: self._process_contract_result(v) for k, v in result._asdict().items()}
            # Convert regular tuples to lists
            return [self._process_contract_result(item) for item in result]
        elif hasattr(result, '__dict__'):
            # Convert objects to dictionaries
            return {k: self._process_contract_result(v) for k, v in result.__dict__.items() 
                    if not k.startswith('_')}
        else:
            # For any other type, convert to string
            return str(result)


class TokenTool(Web3BaseTool):
    """Tool for token-related operations like balances, transfers, and approvals."""
    
    # Common ABI fragments for token operations
    ERC20_ABI = [
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
        },
        {
            "constant": True,
            "inputs": [],
            "name": "name",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
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
            "constant": False,
            "inputs": [
                {"name": "_spender", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [
                {"name": "_owner", "type": "address"},
                {"name": "_spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        }
    ]
    
    def __init__(self, connection_tool: Web3ConnectionTool, contract_tool: SmartContractTool):
        super().__init__()
        self.name = "token"
        self.description = "Manages token operations like checking balances and transfers"
        self.connection_tool = connection_tool
        self.contract_tool = contract_tool
        self._token_cache = {}  # Cache for token metadata
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute token operations."""
        network = params.get("network", "ethereum")
        network_type = params.get("network_type", "mainnet")
        action = params.get("action", "native_balance")
        address = params.get("address")
        
        # Validate required parameters
        if not address:
            return self._format_error("Missing required parameter: address")
        
        # Ensure connection to the network
        connection = self.connection_tool.get_connection(network, network_type)
        if not connection:
            return self._format_error(f"Failed to connect to {network} {network_type}")
        
        # Execute the appropriate action
        if network == "ethereum":
            if action == "native_balance":
                return self._safe_execute(self._eth_native_balance, connection, address)
            elif action == "token_balance":
                token_address = params.get("token_address")
                if not token_address:
                    return self._format_error("Missing required parameter: token_address")
                return self._safe_execute(self._eth_token_balance, connection, address, token_address)
            elif action == "transfer":
                return self._safe_execute(self._eth_transfer, connection, params)
            elif action == "approve":
                return self._safe_execute(self._eth_approve, connection, params)
            elif action == "allowance":
                return self._safe_execute(self._eth_allowance, connection, params)
            elif action == "token_info":
                token_address = params.get("token_address")
                if not token_address:
                    return self._format_error("Missing required parameter: token_address")
                return self._safe_execute(self._eth_token_info, connection, token_address)
            else:
                return self._format_error(f"Unsupported action for {network}: {action}")
        elif network == "solana":
            if action == "native_balance":
                return self._safe_execute(self._sol_native_balance, connection, address)
            else:
                return self._format_error(f"Action {action} not implemented for Solana yet")
        else:
            return self._format_error(f"Token operations for {network} not implemented")
    
    def _eth_native_balance(self, connection, address: str) -> Dict[str, Any]:
        """Get native ETH balance."""
        try:
            # Ensure address is checksum address
            checksummed_address = connection.to_checksum_address(address)
            
            # Get balance in Wei
            balance_wei = connection.eth.get_balance(checksummed_address)
            
            # Convert to ETH
            balance_eth = connection.from_wei(balance_wei, "ether")
            
            return {
                "address": checksummed_address,
                "balance": float(balance_eth),
                "balance_wei": str(balance_wei),
                "symbol": "ETH",
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get ETH balance: {str(e)}")
    
    def _eth_token_balance(self, connection, address: str, token_address: str) -> Dict[str, Any]:
        """Get ERC-20 token balance."""
        try:
            # Ensure addresses are checksum addresses
            checksummed_address = connection.to_checksum_address(address)
            checksummed_token = connection.to_checksum_address(token_address)
            
            # Get token info (cached)
            token_info = self._get_token_info(connection, checksummed_token)
            
            # Get token balance
            balance_result = self.contract_tool._execute({
                "network": "ethereum",
                "action": "read",
                "contract_address": checksummed_token,
                "contract_abi": self.ERC20_ABI,
                "method_name": "balanceOf",
                "args": [checksummed_address]
            })
            
            if "error" in balance_result:
                return balance_result
            
            # Calculate human-readable balance
            raw_balance = balance_result["result"]
            decimals = token_info.get("decimals", 18)
            balance = raw_balance / (10 ** decimals)
            
            return {
                "address": checksummed_address,
                "token_address": checksummed_token,
                "token_name": token_info.get("name", "Unknown Token"),
                "token_symbol": token_info.get("symbol", "???"),
                "balance": balance,
                "balance_raw": str(raw_balance),
                "decimals": decimals,
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get token balance: {str(e)}")
    
    @lru_cache(maxsize=100)
    def _get_token_info(self, connection, token_address: str) -> Dict[str, Any]:
        """Get token information (cached)."""
        token_key = f"ethereum:{token_address}"
        
        # Check cache first
        if token_key in self._token_cache:
            return self._token_cache[token_key]
        
        # Get token symbol
        symbol_result = self.contract_tool._execute({
            "network": "ethereum",
            "action": "read",
            "contract_address": token_address,
            "contract_abi": self.ERC20_ABI,
            "method_name": "symbol",
            "args": []
        })
        
        # Get token name
        name_result = self.contract_tool._execute({
            "network": "ethereum",
            "action": "read",
            "contract_address": token_address,
            "contract_abi": self.ERC20_ABI,
            "method_name": "name",
            "args": []
        })
        
        # Get token decimals
        decimals_result = self.contract_tool._execute({
            "network": "ethereum",
            "action": "read",
            "contract_address": token_address,
            "contract_abi": self.ERC20_ABI,
            "method_name": "decimals",
            "args": []
        })
        
        # Extract values or use defaults
        symbol = "???" if "error" in symbol_result else symbol_result["result"]
        name = "Unknown Token" if "error" in name_result else name_result["result"]
        decimals = 18 if "error" in decimals_result else decimals_result["result"]
        
        # Create token info
        token_info = {
            "address": token_address,
            "symbol": symbol,
            "name": name,
            "decimals": decimals
        }
        
        # Cache the result
        self._token_cache[token_key] = token_info
        
        return token_info
    
    def _eth_token_info(self, connection, token_address: str) -> Dict[str, Any]:
        """Get detailed token information."""
        try:
            # Ensure address is checksum address
            checksummed_token = connection.to_checksum_address(token_address)
            
            # Get basic token info
            token_info = self._get_token_info(connection, checksummed_token)
            
            # Get total supply if possible
            supply_result = self.contract_tool._execute({
                "network": "ethereum",
                "action": "read",
                "contract_address": checksummed_token,
                "contract_abi": [
                    {
                        "constant": True,
                        "inputs": [],
                        "name": "totalSupply",
                        "outputs": [{"name": "", "type": "uint256"}],
                        "type": "function"
                    }
                ],
                "method_name": "totalSupply",
                "args": []
            })
            
            # Add total supply to token info if available
            if "error" not in supply_result:
                raw_supply = supply_result["result"]
                decimals = token_info.get("decimals", 18)
                formatted_supply = raw_supply / (10 ** decimals)
                token_info["total_supply"] = formatted_supply
                token_info["total_supply_raw"] = str(raw_supply)
            
            return token_info
        except Exception as e:
            return self._format_error(f"Failed to get token info: {str(e)}")
    
    def _eth_transfer(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer ETH or ERC-20 tokens."""
        try:
            # Get required parameters
            from_address = params.get("address")
            to_address = params.get("to_address")
            amount = params.get("amount")
            private_key = params.get("private_key")
            token_address = params.get("token_address")  # Optional for ERC-20 transfers
            
            # Validate required parameters
            if not to_address or not amount:
                return self._format_error("Missing required parameters: to_address and amount")
            
            if not private_key:
                return self._format_error("Missing required parameter: private_key")
            
            # Ensure addresses are checksum addresses
            from_address = connection.to_checksum_address(from_address)
            to_address = connection.to_checksum_address(to_address)
            
            if token_address:
                # ERC-20 token transfer
                token_address = connection.to_checksum_address(token_address)
                
                # Get token info for decimals
                token_info = self._get_token_info(connection, token_address)
                decimals = token_info.get("decimals", 18)
                
                # Convert amount to token units
                amount_in_units = int(float(amount) * (10 ** decimals))
                
                # Execute the transfer via contract tool
                return self.contract_tool._execute({
                    "network": "ethereum",
                    "action": "write",
                    "contract_address": token_address,
                    "contract_abi": self.ERC20_ABI,
                    "method_name": "transfer",
                    "args": [to_address, amount_in_units],
                    "from_address": from_address,
                    "private_key": private_key,
                    **{k: v for k, v in params.items() if k in ["gas", "gas_price", "max_fee_per_gas", "max_priority_fee_per_gas"]}
                })
            else:
                # Native ETH transfer
                amount_in_wei = connection.to_wei(amount, "ether")
                
                # Build the transaction
                tx = {
                    'from': from_address,
                    'to': to_address,
                    'value': amount_in_wei,
                    'nonce': connection.eth.get_transaction_count(from_address),
                }
                
                # Add gas parameters if provided
                if "gas" in params:
                    tx["gas"] = params["gas"]
                else:
                    tx["gas"] = 21000  # Standard gas for ETH transfers
                
                if "gas_price" in params:
                    tx["gasPrice"] = params["gas_price"]
                elif "max_fee_per_gas" in params:
                    # EIP-1559 parameters
                    tx["maxFeePerGas"] = params["max_fee_per_gas"]
                    tx["maxPriorityFeePerGas"] = params.get("max_priority_fee_per_gas", 
                                                         params["max_fee_per_gas"] // 2)
                
                # Sign and send the transaction
                signed_tx = connection.eth.account.sign_transaction(tx, private_key)
                tx_hash = connection.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "pending",
                    "from": from_address,
                    "to": to_address,
                    "amount": amount,
                    "amount_wei": str(amount_in_wei),
                    "symbol": "ETH",
                    "network": "ethereum"
                }
        except Exception as e:
            return self._format_error(f"Transfer failed: {str(e)}")
    
    def _eth_approve(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Approve spender to use tokens."""
        try:
            # Get required parameters
            from_address = params.get("address")
            spender_address = params.get("spender_address")
            amount = params.get("amount")
            token_address = params.get("token_address")
            private_key = params.get("private_key")
            
            # Validate required parameters
            if not from_address or not spender_address or not amount or not token_address:
                return self._format_error("Missing required parameters: address, spender_address, amount, and token_address")
            
            if not private_key:
                return self._format_error("Missing required parameter: private_key")
            
            # Ensure addresses are checksum addresses
            from_address = connection.to_checksum_address(from_address)
            spender_address = connection.to_checksum_address(spender_address)
            token_address = connection.to_checksum_address(token_address)
            
            # Get token info for decimals
            token_info = self._get_token_info(connection, token_address)
            decimals = token_info.get("decimals", 18)
            
            # Convert amount to token units (or use max uint256 for "unlimited" approval)
            if amount.lower() == "unlimited" or amount.lower() == "infinite":
                amount_in_units = 2**256 - 1  # Max uint256 value
            else:
                amount_in_units = int(float(amount) * (10 ** decimals))
            
            # Execute the approval via contract tool
            return self.contract_tool._execute({
                "network": "ethereum",
                "action": "write",
                "contract_address": token_address,
                "contract_abi": self.ERC20_ABI,
                "method_name": "approve",
                "args": [spender_address, amount_in_units],
                "from_address": from_address,
                "private_key": private_key,
                **{k: v for k, v in params.items() if k in ["gas", "gas_price", "max_fee_per_gas", "max_priority_fee_per_gas"]}
            })
        except Exception as e:
            return self._format_error(f"Approval failed: {str(e)}")
    
    def _eth_allowance(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check token allowance."""
        try:
            # Get required parameters
            owner_address = params.get("address")
            spender_address = params.get("spender_address")
            token_address = params.get("token_address")
            
            # Validate required parameters
            if not owner_address or not spender_address or not token_address:
                return self._format_error("Missing required parameters: address, spender_address, and token_address")
            
            # Ensure addresses are checksum addresses
            owner_address = connection.to_checksum_address(owner_address)
            spender_address = connection.to_checksum_address(spender_address)
            token_address = connection.to_checksum_address(token_address)
            
            # Get token info for decimals and symbol
            token_info = self._get_token_info(connection, token_address)
            
            # Check allowance
            allowance_result = self.contract_tool._execute({
                "network": "ethereum",
                "action": "read",
                "contract_address": token_address,
                "contract_abi": self.ERC20_ABI,
                "method_name": "allowance",
                "args": [owner_address, spender_address]
            })
            
            if "error" in allowance_result:
                return allowance_result
            
            # Calculate human-readable allowance
            raw_allowance = allowance_result["result"]
            decimals = token_info.get("decimals", 18)
            allowance = raw_allowance / (10 ** decimals)
            
            # Check if it's "unlimited" approval
            is_unlimited = raw_allowance > 2**250  # Close enough to max uint256
            
            return {
                "owner": owner_address,
                "spender": spender_address,
                "token_address": token_address,
                "token_symbol": token_info.get("symbol", "???"),
                "allowance": "Unlimited" if is_unlimited else allowance,
                "allowance_raw": str(raw_allowance),
                "unlimited": is_unlimited,
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to check allowance: {str(e)}")
    
    def _sol_native_balance(self, connection, address: str) -> Dict[str, Any]:
        """Get native SOL balance."""
        try:
            # Query Solana balance
            result = connection.get_balance({"pubkey": address})
            
            if "error" in result:
                return self._format_error(f"Failed to get SOL balance: {result['error']}")
            
            # Extract balance in lamports
            balance_lamports = result.get("result", {}).get("value", 0)
            
            # Convert to SOL (1 SOL = 10^9 lamports)
            balance_sol = balance_lamports / 1_000_000_000
            
            return {
                "address": address,
                "balance": balance_sol,
                "balance_lamports": balance_lamports,
                "symbol": "SOL",
                "network": "solana"
            }
        except Exception as e:
            return self._format_error(f"Failed to get SOL balance: {str(e)}")


class NFTTool(Web3BaseTool):
    """Tool for NFT-related operations."""
    
    # Common ABI fragments for NFT operations
    ERC721_ABI = [
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
        },
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
        },
        {
            "constant": True,
            "inputs": [{"name": "owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "approved", "type": "bool"}
            ],
            "name": "setApprovalForAll",
            "outputs": [],
            "type": "function"
        }
    ]
    
    # Common ABI for ERC1155
    ERC1155_ABI = [
        {
            "constant": True,
            "inputs": [
                {"name": "account", "type": "address"},
                {"name": "id", "type": "uint256"}
            ],
            "name": "balanceOf",
            "outputs": [{"name": "", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "", "type": "uint256"}],
            "name": "uri",
            "outputs": [{"name": "", "type": "string"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "id", "type": "uint256"},
                {"name": "value", "type": "uint256"},
                {"name": "data", "type": "bytes"}
            ],
            "name": "safeTransferFrom",
            "outputs": [],
            "type": "function"
        }
    ]
    
    def __init__(self, connection_tool: Web3ConnectionTool, contract_tool: SmartContractTool):
        super().__init__()
        self.name = "nft"
        self.description = "Manages NFT operations like viewing metadata and transfers"
        self.connection_tool = connection_tool
        self.contract_tool = contract_tool
        self._metadata_cache = {}
        
    def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NFT operations."""
        network = params.get("network", "ethereum")
        network_type = params.get("network_type", "mainnet")
        action = params.get("action", "get_metadata")
        
        # Ensure connection to the network
        connection = self.connection_tool.get_connection(network, network_type)
        if not connection:
            return self._format_error(f"Failed to connect to {network} {network_type}")
        
        # Execute the appropriate action
        if network == "ethereum":
            if action == "get_metadata":
                contract_address = params.get("contract_address")
                token_id = params.get("token_id")
                
                if not contract_address or token_id is None:
                    return self._format_error("Missing required parameters: contract_address and token_id")
                
                return self._safe_execute(
                    self._eth_get_metadata, 
                    connection, 
                    contract_address, 
                    token_id,
                    params.get("force_refresh", False)
                )
            elif action == "get_owner":
                contract_address = params.get("contract_address")
                token_id = params.get("token_id")
                
                if not contract_address or token_id is None:
                    return self._format_error("Missing required parameters: contract_address and token_id")
                
                return self._safe_execute(self._eth_get_owner, connection, contract_address, token_id)
            elif action == "transfer":
                return self._safe_execute(self._eth_transfer_nft, connection, params)
            elif action == "owned_by":
                address = params.get("address")
                contract_address = params.get("contract_address")
                
                if not address:
                    return self._format_error("Missing required parameter: address")
                
                if contract_address:
                    return self._safe_execute(
                        self._eth_owned_tokens, 
                        connection, 
                        address, 
                        contract_address
                    )
                else:
                    return self._format_error("Contract address required for owned_by action")
            else:
                return self._format_error(f"Unsupported action for {network}: {action}")
        else:
            return self._format_error(f"NFT operations for {network} not implemented")
    
    def _eth_get_metadata(self, connection, contract_address: str, token_id: Union[int, str], force_refresh: bool = False) -> Dict[str, Any]:
        """Get NFT metadata."""
        try:
            # Ensure address is checksum address
            checksummed_address = connection.to_checksum_address(contract_address)
            
            # Convert token_id to int if it's a string
            if isinstance(token_id, str):
                token_id = int(token_id)
            
            # Create cache key
            cache_key = f"ethereum:{checksummed_address}:{token_id}"
            
            # Check cache first if not forcing refresh
            if not force_refresh and cache_key in self._metadata_cache:
                return self._metadata_cache[cache_key]
            
            # Get token URI
            uri_result = self.contract_tool._execute({
                "network": "ethereum",
                "action": "read",
                "contract_address": checksummed_address,
                "contract_abi": self.ERC721_ABI,
                "method_name": "tokenURI",
                "args": [token_id]
            })
            
            # If tokenURI fails, try ERC1155 uri
            if "error" in uri_result:
                uri_result = self.contract_tool._execute({
                    "network": "ethereum",
                    "action": "read",
                    "contract_address": checksummed_address,
                    "contract_abi": self.ERC1155_ABI,
                    "method_name": "uri",
                    "args": [token_id]
                })
            
            # Get token owner (only for ERC721)
            owner_result = self.contract_tool._execute({
                "network": "ethereum",
                "action": "read",
                "contract_address": checksummed_address,
                "contract_abi": self.ERC721_ABI,
                "method_name": "ownerOf",
                "args": [token_id]
            })
            
            # Initialize the result
            result = {
                "contract_address": checksummed_address,
                "token_id": token_id,
                "token_standard": "ERC721" if "error" not in owner_result else "ERC1155",
                "network": "ethereum"
            }
            
            # Add owner if available
            if "error" not in owner_result:
                result["owner"] = owner_result["result"]
            
            # Add token URI if available
            if "error" not in uri_result:
                token_uri = uri_result["result"]
                result["token_uri"] = token_uri
                
                # Fetch metadata if URI is available
                if token_uri:
                    # Handle various URI formats
                    metadata = self._fetch_metadata_from_uri(token_uri, token_id)
                    if metadata:
                        result["metadata"] = metadata
            
            # Cache the result
            self._metadata_cache[cache_key] = result
            
            return result
        except Exception as e:
            return self._format_error(f"Failed to get NFT metadata: {str(e)}")
    
    def _fetch_metadata_from_uri(self, token_uri: str, token_id: int) -> Optional[Dict[str, Any]]:
        """Fetch metadata from a token URI."""
        try:
            import requests
            
            # Process URI
            if "{id}" in token_uri:
                # Handle ERC1155 URI format with ID placeholder
                # Convert ID to hex and remove '0x' prefix for URI
                hex_id = hex(token_id)[2:]
                # Pad to even length
                if len(hex_id) % 2 == 1:
                    hex_id = "0" + hex_id
                
                # Replace {id} with the token ID in hex format, with leading zeros
                token_uri = token_uri.replace("{id}", hex_id)
            
            # Handle IPFS URIs
            if token_uri.startswith("ipfs://"):
                ipfs_cid = token_uri.replace("ipfs://", "").split("/")[0]
                path = token_uri.replace(f"ipfs://{ipfs_cid}", "")
                token_uri = f"https://ipfs.io/ipfs/{ipfs_cid}{path}"
            # Handle Arweave URIs
            elif token_uri.startswith("ar://"):
                ar_id = token_uri.replace("ar://", "")
                token_uri = f"https://arweave.net/{ar_id}"
            
            # Fetch the metadata
            response = requests.get(token_uri, timeout=10)
            
            if response.status_code == 200:
                try:
                    # Try parsing as JSON
                    return response.json()
                except json.JSONDecodeError:
                    # Return as text if not JSON
                    return {"raw_content": response.text}
            else:
                logger.warning(f"Failed to fetch metadata from {token_uri}: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Error fetching metadata: {str(e)}")
            return None
    
    def _eth_get_owner(self, connection, contract_address: str, token_id: Union[int, str]) -> Dict[str, Any]:
        """Get NFT owner."""
        try:
            # Ensure address is checksum address
            checksummed_address = connection.to_checksum_address(contract_address)
            
            # Convert token_id to int if it's a string
            if isinstance(token_id, str):
                token_id = int(token_id)
            
            # Get token owner
            owner_result = self.contract_tool._execute({
                "network": "ethereum",
                "action": "read",
                "contract_address": checksummed_address,
                "contract_abi": self.ERC721_ABI,
                "method_name": "ownerOf",
                "args": [token_id]
            })
            
            if "error" in owner_result:
                return owner_result
            
            return {
                "contract_address": checksummed_address,
                "token_id": token_id,
                "owner": owner_result["result"],
                "network": "ethereum"
            }
        except Exception as e:
            return self._format_error(f"Failed to get NFT owner: {str(e)}")
    
    def _eth_transfer_nft(self, connection, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer an NFT."""
        try:
            # Get required parameters
            from_address = params.get("address")
            to_address = params.get("to_address")
            token_id = params.get("token_id")
            contract_address = params.get("contract_address")
            private_key = params.get("private_key")
            token_standard = params.get("token_standard", "ERC721")
            
            # Validate required parameters
            if not from_address or not to_address or token_id is None or not contract_address:
                return self._format_error("Missing required parameters: address, to_address, token_id, and contract_address")
            
            if not private_key:
                return self._format_error("Missing required parameter: private_key")
            
            # Ensure addresses are checksum addresses
            from_address = connection.to_checksum_address(from_address)
            to_address = connection.to_checksum_address(to_address)
            contract_address = connection.to_checksum_address(contract_address)
            
            # Convert token_id to int if it's a string
            if isinstance(token_id, str):
                token_id = int(token_id)
            
            if token_standard.upper() == "ERC721":
                # Transfer ERC721 NFT
                return self.contract_tool._execute({
                    "network": "ethereum",
                    "action": "write",
                    "contract_address": contract_address,
                    "contract_abi": self.ERC721_ABI,
                    "method_name": "transferFrom",
                    "args": [from_address, to_address, token_id],
                    "from_address": from_address,
                    "private_key": private_key,
                    **{k: v for k, v in params.items() if k in ["gas", "gas_price", "max_fee_per_gas", "max_priority_fee_per_gas"]}
                })
            elif token_standard.upper() == "ERC1155":
                # Transfer ERC1155 NFT
                amount = params.get("amount", 1)  # Default to 1 for ERC1155
                
                return self.contract_tool._execute({
                    "network": "ethereum",
                    "action": "write",
                    "contract_address": contract_address,
                    "contract_abi": self.ERC1155_ABI,
                    "method_name": "safeTransferFrom",
                    "args": [from_address, to_address, token_id, amount, "0x"],
                    "from_address": from_address,
                    "private_key": private_key,
                    **{k: v for k, v in params.items() if k in ["gas", "gas_price", "max_fee_per_gas", "max_priority_fee_per_gas"]}
                })
            else:
                return self._format_error(f"Unsupported token standard: {token_standard}")
        except Exception as e:
            return self._format_error(f"NFT transfer failed: {str(e)}")
    
    def _eth_owned_tokens(self, connection, address: str, contract_address: str) -> Dict[str, Any]:
        """Get tokens owned by an address for a specific contract."""
        try:
            # Ensure addresses are checksum addresses
            checksummed_address = connection.to_checksum_address(address)
            checksummed_contract = connection.to_checksum_address(contract_address)
            
            # First check if it's ERC721 by getting balance
            balance_result = self.contract_tool._execute({
                "network": "ethereum",
                "action": "read",
                "contract_address": checksummed_contract,
                "contract_abi": self.ERC721_ABI,
                "method_name": "balanceOf",
                "args": [checksummed_address]
            })
            
            if "error" in balance_result:
                return balance_result
            
            balance = balance_result["result"]
            
            return {
                "address": checksummed_address,
                "contract_address": checksummed_contract,
                "token_balance": balance,
                "network": "ethereum",
                "note": "Token enumeration is not supported directly through the contract. Use an indexer service for complete token list."
            }
        except Exception as e:
            return self._format_error(f"Failed to get owned tokens: {str(e)}")


class DeFiTool(Web3BaseTool):
    """Tool for DeFi operations like swaps, lending, and liquidity provision."""
    
    # Common ABIs for DeFi protocols
    UNISWAP_V2_ROUTER_ABI = [
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactETHForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "payable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForETH",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    # Protocol addresses
    PROTOCOL_ADDRESSES = {
        "ethereum": {
            "uniswap_v2_router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "sushiswap_router": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
            "aave_v2_lending_pool": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
            "compound_comptroller": "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B"
        }
    }
