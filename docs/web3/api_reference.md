# Anus AI Weenus Module API Reference

This document provides detailed API documentation for the Web3 module components of the Anus AI framework.

## Table of Contents

- [Web3Agent](#web3agent)
- [Web3Society](#web3society)
- [Web3 Tools](#web3-tools)
  - [Web3ConnectionTool](#web3connectiontool)
  - [SmartContractTool](#smartcontracttool)
  - [TokenTool](#tokentool)
  - [NFTTool](#nfttool)
  - [DeFiTool](#defitool)
  - [ENSTool](#enstool)
  - [IPFSTool](#ipfstool)
- [Utility Functions](#utility-functions)
  - [Ethereum Utilities](#ethereum-utilities)
  - [Solana Utilities](#solana-utilities)
  - [IPFS Utilities](#ipfs-utilities)

---

## Web3Agent

The `Web3Agent` class is a specialized agent for Web3 operations, providing high-level methods for interacting with blockchain networks, smart contracts, and decentralized applications.

### Initialization

```python
from anus.web3 import Web3Agent

agent = Web3Agent(config=None)
```

**Parameters:**
- `config` (Optional[Dict[str, Any]]): Configuration dictionary with the following options:
  - `ethereum_provider` (str): Ethereum provider URL or API endpoint
  - `solana_provider` (str): Solana provider URL or API endpoint
  - `ipfs` (Dict): IPFS configuration options
  - `memory_path` (str): Path for agent memory storage

### Methods

#### Blockchain Connection

```python
def connect_wallet(self, network: str, network_type: str = "mainnet", provider_url: Optional[str] = None) -> Dict[str, Any]:
    """Connect to a specific blockchain network."""
```

**Parameters:**
- `network` (str): Blockchain network to connect to (e.g., "ethereum", "solana")
- `network_type` (str): Network type (e.g., "mainnet", "sepolia", "devnet")
- `provider_url` (Optional[str]): Custom provider URL

**Returns:**
- Dictionary with connection status and information

#### Token Operations

```python
def token_balance(self, address: str, token_address: Optional[str] = None, network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Get token balance for an address."""
```

**Parameters:**
- `address` (str): Wallet address to check
- `token_address` (Optional[str]): ERC-20 token address (if None, gets native token balance)
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with balance information

```python
def token_info(self, token_address: str, network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Get detailed information about a token."""
```

**Parameters:**
- `token_address` (str): Token contract address
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with token information

```python
def transfer_tokens(self, from_address: str, to_address: str, amount: Union[str, float], private_key: str, token_address: Optional[str] = None, network: str = "ethereum", network_type: str = "mainnet", **kwargs) -> Dict[str, Any]:
    """Transfer tokens between addresses."""
```

**Parameters:**
- `from_address` (str): Sender address
- `to_address` (str): Recipient address
- `amount` (Union[str, float]): Amount to transfer
- `private_key` (str): Private key for signing the transaction
- `token_address` (Optional[str]): Token address (if None, transfers native token)
- `network` (str): Blockchain network
- `network_type` (str): Network type
- `**kwargs`: Additional transaction parameters

**Returns:**
- Dictionary with transaction result

```python
def approve_tokens(self, address: str, spender_address: str, amount: Union[str, float], token_address: str, private_key: str, network: str = "ethereum", network_type: str = "mainnet", **kwargs) -> Dict[str, Any]:
    """Approve a spender to use tokens."""
```

**Parameters:**
- `address` (str): Token owner address
- `spender_address` (str): Address to approve
- `amount` (Union[str, float]): Amount to approve (or "unlimited")
- `token_address` (str): Token address
- `private_key` (str): Private key for signing
- `network` (str): Blockchain network
- `network_type` (str): Network type
- `**kwargs`: Additional transaction parameters

**Returns:**
- Dictionary with approval result

```python
def check_allowance(self, owner_address: str, spender_address: str, token_address: str, network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Check token allowance for a spender."""
```

**Parameters:**
- `owner_address` (str): Token owner address
- `spender_address` (str): Spender address
- `token_address` (str): Token address
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with allowance information

#### NFT Operations

```python
def nft_info(self, contract_address: str, token_id: Union[int, str], network: str = "ethereum", network_type: str = "mainnet", force_refresh: bool = False) -> Dict[str, Any]:
    """Get NFT information including metadata."""
```

**Parameters:**
- `contract_address` (str): NFT contract address
- `token_id` (Union[int, str]): Token ID
- `network` (str): Blockchain network
- `network_type` (str): Network type
- `force_refresh` (bool): Whether to force refresh cached data

**Returns:**
- Dictionary with NFT information

```python
def nft_owner(self, contract_address: str, token_id: Union[int, str], network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Get the owner of an NFT."""
```

**Parameters:**
- `contract_address` (str): NFT contract address
- `token_id` (Union[int, str]): Token ID
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with owner information

```python
def transfer_nft(self, from_address: str, to_address: str, contract_address: str, token_id: Union[int, str], private_key: str, token_standard: str = "ERC721", network: str = "ethereum", network_type: str = "mainnet", **kwargs) -> Dict[str, Any]:
    """Transfer an NFT."""
```

**Parameters:**
- `from_address` (str): Sender address
- `to_address` (str): Recipient address
- `contract_address` (str): NFT contract address
- `token_id` (Union[int, str]): Token ID
- `private_key` (str): Private key for signing
- `token_standard` (str): Token standard (ERC721 or ERC1155)
- `network` (str): Blockchain network
- `network_type` (str): Network type
- `**kwargs`: Additional transaction parameters

**Returns:**
- Dictionary with transfer result

#### Smart Contract Operations

```python
def call_contract(self, contract_address: str, method_name: str, args: List[Any], contract_abi: List[Dict[str, Any]], network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Call a smart contract read method."""
```

**Parameters:**
- `contract_address` (str): Contract address
- `method_name` (str): Method name to call
- `args` (List[Any]): Arguments to pass to the method
- `contract_abi` (List[Dict[str, Any]]): Contract ABI
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with call result

```python
def send_contract_transaction(self, contract_address: str, method_name: str, args: List[Any], contract_abi: List[Dict[str, Any]], from_address: str, private_key: str, network: str = "ethereum", network_type: str = "mainnet", **kwargs) -> Dict[str, Any]:
    """Send a smart contract write transaction."""
```

**Parameters:**
- `contract_address` (str): Contract address
- `method_name` (str): Method name to call
- `args` (List[Any]): Arguments to pass to the method
- `contract_abi` (List[Dict[str, Any]]): Contract ABI
- `from_address` (str): Sender address
- `private_key` (str): Private key for signing
- `network` (str): Blockchain network
- `network_type` (str): Network type
- `**kwargs`: Additional transaction parameters

**Returns:**
- Dictionary with transaction result

#### ENS Operations

```python
def resolve_ens(self, name: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Resolve ENS name to address."""
```

**Parameters:**
- `name` (str): ENS name to resolve
- `force_refresh` (bool): Whether to force refresh cached data

**Returns:**
- Dictionary with resolution result

```python
def lookup_ens(self, address: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Lookup address to find ENS name."""
```

**Parameters:**
- `address` (str): Address to lookup
- `force_refresh` (bool): Whether to force refresh cached data

**Returns:**
- Dictionary with lookup result

#### IPFS Operations

```python
def get_ipfs_content(self, cid: str, path: str = "", force_refresh: bool = False) -> Dict[str, Any]:
    """Get content from IPFS."""
```

**Parameters:**
- `cid` (str): IPFS CID
- `path` (str): Optional path within the CID
- `force_refresh` (bool): Whether to force refresh cached data

**Returns:**
- Dictionary with content information

```python
def add_to_ipfs(self, data: Any) -> Dict[str, Any]:
    """Add content to IPFS."""
```

**Parameters:**
- `data` (Any): Data to add

**Returns:**
- Dictionary with result information

#### DeFi Operations

```python
def swap_tokens(self, address: str, private_key: str, token_in: str, token_out: str, amount_in: Union[str, float], slippage: float = 0.5, protocol: str = "uniswap_v2", network: str = "ethereum", network_type: str = "mainnet", **kwargs) -> Dict[str, Any]:
    """Swap tokens using a DEX."""
```

**Parameters:**
- `address` (str): User address
- `private_key` (str): Private key
- `token_in` (str): Input token (address or symbol)
- `token_out` (str): Output token (address or symbol)
- `amount_in` (Union[str, float]): Input amount
- `slippage` (float): Allowed slippage percentage
- `protocol` (str): DEX protocol to use
- `network` (str): Blockchain network
- `network_type` (str): Network type
- `**kwargs`: Additional parameters

**Returns:**
- Dictionary with swap result

```python
def get_swap_quote(self, token_in: str, token_out: str, amount_in: Union[str, float], protocol: str = "uniswap_v2", network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Get a swap quote from a DEX."""
```

**Parameters:**
- `token_in` (str): Input token (address or symbol)
- `token_out` (str): Output token (address or symbol)
- `amount_in` (Union[str, float]): Input amount
- `protocol` (str): DEX protocol to use
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with quote information

#### Wallet Analysis

```python
def wallet_status(self, address: str, networks: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get comprehensive wallet status across multiple networks."""
```

**Parameters:**
- `address` (str): Wallet address
- `networks` (Optional[List[str]]): List of networks to check (defaults to ["ethereum"])

**Returns:**
- Dictionary with wallet status information

```python
def analyze_wallet(self, address: str, networks: Optional[List[str]] = None) -> Dict[str, Any]:
    """Perform a comprehensive analysis of a wallet."""
```

**Parameters:**
- `address` (str): Wallet address to analyze
- `networks` (Optional[List[str]]): List of networks to analyze

**Returns:**
- Dictionary with analysis information

#### Tool Management

```python
def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a specific Web3 tool directly."""
```

**Parameters:**
- `tool_name` (str): Name of the tool to run
- `params` (Dict[str, Any]): Parameters to pass to the tool

**Returns:**
- Tool execution result

---

## Web3Society

The `Web3Society` class creates a multi-agent system for complex Web3 tasks, combining specialized agent roles.

### Initialization

```python
from anus.web3 import Web3Society

society = Web3Society(config=None)
```

**Parameters:**
- `config` (Optional[Dict[str, Any]]): Configuration dictionary with the following options:
  - `ethereum_provider` (str): Ethereum provider URL or API endpoint
  - `solana_provider` (str): Solana provider URL or API endpoint
  - `memory_path` (str): Path for society memory storage
  - `coordination_strategy` (str): Agent coordination strategy ("hierarchical" or "consensus")

### Methods

#### Wallet Analysis

```python
def analyze_wallet(self, address: str, networks: Optional[List[str]] = None) -> Dict[str, Any]:
    """Perform comprehensive wallet analysis across multiple networks."""
```

**Parameters:**
- `address` (str): Wallet address to analyze
- `networks` (Optional[List[str]]): List of networks to analyze

**Returns:**
- Dictionary with wallet analysis

#### Smart Contract Analysis

```python
def assess_smart_contract(self, contract_address: str, network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Assess a smart contract for security, efficiency, and functionality."""
```

**Parameters:**
- `contract_address` (str): Contract address to assess
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with contract assessment

```python
def draft_smart_contract(self, requirements: str, contract_type: str) -> Dict[str, Any]:
    """Draft a smart contract based on provided requirements."""
```

**Parameters:**
- `requirements` (str): Contract requirements
- `contract_type` (str): Type of contract to draft

**Returns:**
- Dictionary with contract draft

#### DeFi Analysis

```python
def analyze_defi_protocol(self, protocol_name: str, contract_addresses: Optional[List[str]] = None) -> Dict[str, Any]:
    """Analyze a DeFi protocol in detail."""
```

**Parameters:**
- `protocol_name` (str): Name of the protocol to analyze
- `contract_addresses` (Optional[List[str]]): List of contract addresses related to the protocol

**Returns:**
- Dictionary with protocol analysis

```python
def create_defi_strategy(self, investment_amount: float, risk_profile: str, tokens: List[str] = None) -> Dict[str, Any]:
    """Create a DeFi investment strategy based on user parameters."""
```

**Parameters:**
- `investment_amount` (float): Amount to invest
- `risk_profile` (str): Risk profile (e.g., "conservative", "moderate", "aggressive")
- `tokens` (List[str]): Optional list of tokens of interest

**Returns:**
- Dictionary with investment strategy

```python
def analyze_token_economics(self, token_address: str, network: str = "ethereum", network_type: str = "mainnet") -> Dict[str, Any]:
    """Analyze tokenomics of a specific token."""
```

**Parameters:**
- `token_address` (str): Token address to analyze
- `network` (str): Blockchain network
- `network_type` (str): Network type

**Returns:**
- Dictionary with tokenomics analysis

#### NFT Analysis

```python
def monitor_nft_collection(self, collection_address: str, network: str = "ethereum", network_type: str = "mainnet", period: str = "7d") -> Dict[str, Any]:
    """Monitor and analyze an NFT collection, including recent sales and trends."""
```

**Parameters:**
- `collection_address` (str): NFT collection address
- `network` (str): Blockchain network
- `network_type` (str): Network type
- `period` (str): Time period to analyze (e.g., "7d", "30d")

**Returns:**
- Dictionary with collection analysis

#### Research and Development

```python
def research_web3_topic(self, topic: str, depth: str = "comprehensive") -> Dict[str, Any]:
    """Research a Web3-related topic comprehensively."""
```

**Parameters:**
- `topic` (str): Topic to research
- `depth` (str): Depth of research ("brief", "standard", "comprehensive")

**Returns:**
- Dictionary with research results

```python
def develop_dapp_concept(self, problem_statement: str, target_users: str, blockchain: str = "ethereum") -> Dict[str, Any]:
    """Develop a comprehensive dApp concept based on requirements."""
```

**Parameters:**
- `problem_statement` (str): Problem the dApp will solve
- `target_users` (str): Description of target users
- `blockchain` (str): Blockchain platform

**Returns:**
- Dictionary with dApp concept

---

## Web3 Tools

The Web3 module includes several specialized tools that extend the BaseTool class from the Anus AI framework.

### Web3ConnectionTool

The `Web3ConnectionTool` manages connections to various blockchain networks.

```python
def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the connection tool with the given parameters."""
```

**Parameters:**
- `params` (Dict[str, Any]): Parameters dictionary with:
  - `network` (str): Blockchain network to connect to
  - `network_type` (str): Network type
  - `force_reconnect` (bool): Whether to force reconnection
  - `provider_url` (str): Optional custom provider URL

**Returns:**
- Dictionary with connection result

### SmartContractTool

The `SmartContractTool` facilitates interaction with smart contracts on various blockchains.

```python
def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute smart contract interactions."""
```

**Parameters:**
- `params` (Dict[str, Any]): Parameters dictionary with:
  - `network` (str): Blockchain network
  - `network_type` (str): Network type
  - `action` (str): Action to perform ("read" or "write")
  - `contract_address` (str): Contract address
  - `contract_abi` (List[Dict]): Contract ABI
  - `method_name` (str): Method to call
  - `args` (List): Arguments to pass to the method
  - Additional parameters for write operations:
    - `from_address` (str): Sender address
    - `private_key` (str): Private key for signing
    - `gas` (int): Gas limit
    - `gas_price` (int): Gas price

**Returns:**
- Dictionary with interaction result

### TokenTool

The `TokenTool` handles token-related operations like balances, transfers, and approvals.

```python
def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute token operations."""
```

**Parameters:**
- `params` (Dict[str, Any]): Parameters dictionary with:
  - `network` (str): Blockchain network
  - `network_type` (str): Network type
  - `action` (str): Action to perform
  - `address` (str): Wallet address
  - Additional parameters depending on action:
    - For `token_balance`: `token_address` (Optional)
    - For `transfer`: `to_address`, `amount`, `token_address` (Optional), `private_key`
    - For `approve`: `spender_address`, `amount`, `token_address`, `private_key`
    - For `allowance`: `spender_address`, `token_address`

**Returns:**
- Dictionary with operation result

### NFTTool

The `NFTTool` manages NFT-related operations like viewing metadata and transfers.

```python
def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute NFT operations."""
```

**Parameters:**
- `params` (Dict[str, Any]): Parameters dictionary with:
  - `network` (str): Blockchain network
  - `network_type` (str): Network type
  - `action` (str): Action to perform
  - `address` (str): Wallet address
  - Additional parameters depending on action:
    - For `get_metadata`: `contract_address`, `token_id`, `force_refresh` (Optional)
    - For `get_owner`: `contract_address`, `token_id`
    - For `transfer`: `to_address`, `contract_address`, `token_id`, `private_key`, `token_standard` (Optional)
    - For `owned_by`: `address`, `contract_address`

**Returns:**
- Dictionary with operation result

### DeFiTool

The `DeFiTool` performs DeFi operations like swaps, lending, and liquidity provision.

```python
def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute DeFi operations."""
```

**Parameters:**
- `params` (Dict[str, Any]): Parameters dictionary with:
  - `network` (str): Blockchain network
  - `network_type` (str): Network type
  - `action` (str): Action to perform
  - `protocol` (str): DeFi protocol to use
  - `address` (str): Wallet address
  - Additional parameters depending on action:
    - For `swap`: `token_in`, `token_out`, `amount_in`, `slippage` (Optional), `private_key`
    - For `get_swap_quote`: `token_in`, `token_out`, `amount_in`
    - For `get_reserves`: `token_a`, `token_b`
    - For `get_user_data`: `address`

**Returns:**
- Dictionary with operation result

### ENSTool

The `ENSTool` handles Ethereum Name Service (ENS) operations.

```python
def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ENS operations."""
```

**Parameters:**
- `params` (Dict[str, Any]): Parameters dictionary with:
  - `action` (str): Action to perform
  - `name` (str): ENS name (for `resolve` action)
  - `address` (str): Address (for `lookup` action)
  - `key` (str): Text record key (for `get_text_record` action)
  - `force_refresh` (bool): Whether to force refresh cached data

**Returns:**
- Dictionary with operation result

### IPFSTool

The `IPFSTool` handles IPFS operations like content retrieval and pinning.

```python
def _execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute IPFS operations."""
```

**Parameters:**
- `params` (Dict[str, Any]): Parameters dictionary with:
  - `action` (str): Action to perform
  - Additional parameters depending on action:
    - For `get`: `cid`, `path` (Optional), `force_refresh` (Optional)
    - For `add`: `data`
    - For `pin`: `cid`

**Returns:**
- Dictionary with operation result

---

## Utility Functions

The Web3 module includes various utility functions for working with blockchain networks, smart contracts, and decentralized storage.

### Ethereum Utilities

```python
from anus.web3.utils import is_eth_address, normalize_eth_address, checksum_address
```

#### Address Utilities

```python
def is_eth_address(address: str) -> bool:
    """Check if a string is a valid Ethereum address."""
```

**Parameters:**
- `address` (str): The address to check

**Returns:**
- `bool`: True if the address is valid, False otherwise

```python
def normalize_eth_address(address: str) -> Optional[str]:
    """Normalize an Ethereum address to lowercase."""
```

**Parameters:**
- `address` (str): The address to normalize

**Returns:**
- `Optional[str]`: Normalized address or None if invalid

```python
def checksum_address(address: str) -> str:
    """Convert an Ethereum address to checksum format (EIP-55)."""
```

**Parameters:**
- `address` (str): The address to convert

**Returns:**
- `str`: Checksummed address

```python
def generate_eth_address() -> Tuple[str, str]:
    """Generate a random Ethereum address and private key."""
```

**Returns:**
- `Tuple[str, str]`: Tuple of (address, private_key)

#### Transaction Utilities

```python
def estimate_gas(web3, tx_params: Dict[str, Any]) -> int:
    """Estimate gas for a transaction."""
```

**Parameters:**
- `web3`: Web3 instance
- `tx_params` (Dict[str, Any]): Transaction parameters

**Returns:**
- `int`: Estimated gas amount

```python
def wait_for_transaction_receipt(web3, tx_hash: str, timeout: int = 120, poll_interval: float = 0.5) -> Dict[str, Any]:
    """Wait for a transaction receipt."""
```

**Parameters:**
- `web3`: Web3 instance
- `tx_hash` (str): Transaction hash
- `timeout` (int): Maximum time to wait (in seconds)
- `poll_interval` (float): Time between polls (in seconds)

**Returns:**
- `Dict[str, Any]`: Transaction receipt

```python
def decode_transaction_input(web3, contract_abi: List[Dict[str, Any]], input_data: str) -> Dict[str, Any]:
    """Decode transaction input data."""
```

**Parameters:**
- `web3`: Web3 instance
- `contract_abi` (List[Dict[str, Any]]): Contract ABI
- `input_data` (str): Transaction input data

**Returns:**
- `Dict[str, Any]`: Decoded input data

#### ABI Utilities

```python
def get_function_signature(function_name: str, param_types: List[str]) -> str:
    """Get function signature."""
```

**Parameters:**
- `function_name` (str): Name of the function
- `param_types` (List[str]): List of parameter types

**Returns:**
- `str`: Function signature

```python
def get_event_signature(event_name: str, param_types: List[str]) -> str:
    """Get event signature."""
```

**Parameters:**
- `event_name` (str): Name of the event
- `param_types` (List[str]): List of parameter types

**Returns:**
- `str`: Event signature

```python
def parse_event_logs(web3, contract_abi: List[Dict[str, Any]], logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse event logs."""
```

**Parameters:**
- `web3`: Web3 instance
- `contract_abi` (List[Dict[str, Any]]): Contract ABI
- `logs` (List[Dict[str, Any]]): List of event logs

**Returns:**
- `List[Dict[str, Any]]`: Parsed event logs

#### Conversion Utilities

```python
def wei_to_eth(wei_amount: Union[int, str]) -> float:
    """Convert wei to ETH."""
```

**Parameters:**
- `wei_amount` (Union[int, str]): Amount in wei

**Returns:**
- `float`: Amount in ETH

```python
def eth_to_wei(eth_amount: Union[float, str]) -> int:
    """Convert ETH to wei."""
```

**Parameters:**
- `eth_amount` (Union[float, str]): Amount in ETH

**Returns:**
- `int`: Amount in wei

```python
def eth_unit_convert(amount: Union[int, float, str], from_unit: str, to_unit: str) -> Union[int, float]:
    """Convert between Ethereum units."""
```

**Parameters:**
- `amount` (Union[int, float, str]): Amount to convert
- `from_unit` (str): Source unit (wei, gwei, eth, etc.)
- `to_unit` (str): Target unit (wei, gwei, eth, etc.)

**Returns:**
- `Union[int, float]`: Converted amount

#### ENS Utilities

```python
def is_ens_name(name: str) -> bool:
    """Check if a string is a valid ENS name."""
```

**Parameters:**
- `name` (str): The name to check

**Returns:**
- `bool`: True if the name is a valid ENS name, False otherwise

```python
def get_ens_resolver(web3, ens_name: str) -> Optional[str]:
    """Get the resolver address for an ENS name."""
```

**Parameters:**
- `web3`: Web3 instance
- `ens_name` (str): ENS name

**Returns:**
- `Optional[str]`: Resolver address or None if not found

#### Gas Price Utilities

```python
def get_recommended_gas_prices(web3) -> Dict[str, int]:
    """Get recommended gas prices."""
```

**Parameters:**
- `web3`: Web3 instance

**Returns:**
- `Dict[str, int]`: Dictionary with recommended gas prices (slow, standard, fast)

```python
def estimate_transaction_cost(web3, gas_limit: int, gas_price: int) -> float:
    """Estimate transaction cost in ETH."""
```

**Parameters:**
- `web3`: Web3 instance
- `gas_limit` (int): Gas limit
- `gas_price` (int): Gas price in wei

**Returns:**
- `float`: Estimated cost in ETH

### Solana Utilities

```python
from anus.web3.utils import is_sol_address, normalize_sol_address, generate_sol_keypair
```

#### Address Utilities

```python
def is_sol_address(address: str) -> bool:
    """Check if a string is a valid Solana address."""
```

**Parameters:**
- `address` (str): The address to check

**Returns:**
- `bool`: True if the address is valid, False otherwise

```python
def normalize_sol_address(address: str) -> Optional[str]:
    """Normalize a Solana address."""
```

**Parameters:**
- `address` (str): The address to normalize

**Returns:**
- `Optional[str]`: Normalized address or None if invalid

```python
def generate_sol_keypair() -> Tuple[str, str]:
    """Generate a random Solana keypair."""
```

**Returns:**
- `Tuple[str, str]`: Tuple of (address, private_key)

#### Transaction Utilities

```python
def estimate_sol_fee(client, num_signatures: int = 1, num_instructions: int = 1) -> int:
    """Estimate transaction fee for a Solana transaction."""
```

**Parameters:**
- `client`: Solana client
- `num_signatures` (int): Number of signatures
- `num_instructions` (int): Number of instructions

**Returns:**
- `int`: Estimated fee in lamports

```python
def wait_for_sol_transaction(client, signature: str, timeout: int = 60, poll_interval: float = 0.5) -> Dict[str, Any]:
    """Wait for a Solana transaction to be confirmed."""
```

**Parameters:**
- `client`: Solana client
- `signature` (str): Transaction signature
- `timeout` (int): Maximum time to wait (in seconds)
- `poll_interval` (float): Time between polls (in seconds)

**Returns:**
- `Dict[str, Any]`: Transaction status

#### Account Utilities

```python
def get_sol_account_info(client, address: str) -> Dict[str, Any]:
    """Get information about a Solana account."""
```

**Parameters:**
- `client`: Solana client
- `address` (str): Account address

**Returns:**
- `Dict[str, Any]`: Account information

```python
def is_sol_program_account(client, address: str) -> bool:
    """Check if an account is a program account."""
```

**Parameters:**
- `client`: Solana client
- `address` (str): Account address

**Returns:**
- `bool`: True if account is a program account, False otherwise

```python
def get_sol_token_accounts(client, owner_address: str) -> List[Dict[str, Any]]:
    """Get token accounts owned by an address."""
```

**Parameters:**
- `client`: Solana client
- `owner_address` (str): Owner address

**Returns:**
- `List[Dict[str, Any]]`: List of token accounts

#### Conversion Utilities

```python
def lamports_to_sol(lamports: Union[int, str]) -> float:
    """Convert lamports to SOL."""
```

**Parameters:**
- `lamports` (Union[int, str]): Amount in lamports

**Returns:**
- `float`: Amount in SOL

```python
def sol_to_lamports(sol_amount: Union[float, str]) -> int:
    """Convert SOL to lamports."""
```

**Parameters:**
- `sol_amount` (Union[float, str]): Amount in SOL

**Returns:**
- `int`: Amount in lamports

### IPFS Utilities

```python
from anus.web3.utils import ipfs_uri_to_http, is_ipfs_uri, normalize_ipfs_uri
```

#### URI Utilities

```python
def is_ipfs_uri(uri: str) -> bool:
    """Check if a URI is an IPFS URI."""
```

**Parameters:**
- `uri` (str): The URI to check

**Returns:**
- `bool`: True if the URI is an IPFS URI, False otherwise

```python
def normalize_ipfs_uri(uri: str) -> Optional[str]:
    """Normalize an IPFS URI to the ipfs://CID format."""
```

**Parameters:**
- `uri` (str): The URI to normalize

**Returns:**
- `Optional[str]`: Normalized URI or None if invalid

```python
def ipfs_uri_to_http(uri: str, gateway: str = "https://ipfs.io/ipfs/") -> Optional[str]:
    """Convert an IPFS URI to an HTTP URL using a gateway."""
```

**Parameters:**
- `uri` (str): The IPFS URI to convert
- `gateway` (str): The IPFS gateway URL to use

**Returns:**
- `Optional[str]`: HTTP URL or None if invalid

```python
def extract_ipfs_cid(uri: str) -> Optional[str]:
    """Extract the CID from an IPFS URI."""
```

**Parameters:**
- `uri` (str): The IPFS URI

**Returns:**
- `Optional[str]`: CID or None if invalid

#### Gateway Utilities

```python
def get_gateway_list() -> List[str]:
    """Get a list of public IPFS gateways."""
```

**Returns:**
- `List[str]`: List of gateway URLs

```python
def get_ipfs_gateway_url(config: Optional[Dict[str, Any]] = None) -> str:
    """Get the IPFS gateway URL from configuration or use default."""
```

**Parameters:**
- `config` (Optional[Dict[str, Any]]): Configuration dictionary

**Returns:**
- `str`: Gateway URL

```python
def select_fastest_gateway(gateways: Optional[List[str]] = None, timeout: int = 10) -> str:
    """Select the fastest IPFS gateway from a list."""
```

**Parameters:**
- `gateways` (Optional[List[str]]): List of gateway URLs to test
- `timeout` (int): Maximum time to wait for responses

**Returns:**
- `str`: URL of the fastest gateway

#### Content Utilities

```python
def fetch_ipfs_content(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """Fetch content from IPFS."""
```

**Parameters:**
- `uri` (str): IPFS URI or HTTP URL
- `gateway` (Optional[str]): Optional gateway URL to use
- `timeout` (int): Request timeout in seconds

**Returns:**
- `Dict[str, Any]`: Dictionary with content and metadata

```python
def is_ipfs_directory(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> bool:
    """Check if an IPFS URI points to a directory."""
```

**Parameters:**
- `uri` (str): IPFS URI
- `gateway` (Optional[str]): Optional gateway URL to use
- `timeout` (int): Request timeout in seconds

**Returns:**
- `bool`: True if the URI points to a directory, False otherwise

```python
def list_ipfs_directory(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """List contents of an IPFS directory."""
```

**Parameters:**
- `uri` (str): IPFS URI
- `gateway` (Optional[str]): Optional gateway URL to use
- `timeout` (int): Request timeout in seconds

**Returns:**
- `Dict[str, Any]`: Directory listing

#### NFT Metadata Utilities

```python
def get_nft_metadata_from_ipfs(uri: str, gateway: Optional[str] = None, timeout: int = 10) -> Dict[str, Any]:
    """Get NFT metadata from IPFS."""
```

**Parameters:**
- `uri` (str): IPFS URI to NFT metadata
- `gateway` (Optional[str]): Optional gateway URL to use
- `timeout` (int): Request timeout in seconds

**Returns:**
- `Dict[str, Any]`: NFT metadata

```python
def get_image_url_from_metadata(metadata: Dict[str, Any], gateway: Optional[str] = None) -> Optional[str]:
    """Extract image URL from NFT metadata."""
```

**Parameters:**
- `metadata` (Dict[str, Any]): NFT metadata
- `gateway` (Optional[str]): Optional gateway URL to use

**Returns:**
- `Optional[str]`: Image URL or None if not found

#### CID Utilities

```python
def is_valid_ipfs_cid(cid: str) -> bool:
    """Check if a string is a valid IPFS CID."""
```

**Parameters:**
- `cid` (str): The CID to check

**Returns:**
- `bool`: True if valid, False otherwise

```python
def convert_cid_version(cid: str, target_version: int = 1, target_base: str = 'base32') -> Optional[str]:
    """Convert between CID versions."""
```

**Parameters:**
- `cid` (str): The CID to convert
- `target_version` (int): Target CID version (0 or 1)
- `target_base` (str): Target base encoding for CIDv1

**Returns:**
- `Optional[str]`: Converted CID or None if conversion failed
