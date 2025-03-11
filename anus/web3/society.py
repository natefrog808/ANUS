"""
Anus AI Web3 Society - Multi-Agent Setup for Web3 Applications

This module implements a specialized multi-agent society for complex Web3 tasks.
"""

from typing import Dict, Any, List, Optional, Union
import json

from anus.society import Society
from anus.agents import Agent
from anus.web3 import Web3Agent, Web3ConnectionTool, SmartContractTool, TokenTool, NFTTool, DeFiTool


class Web3Society(Society):
    """A specialized society of agents for Web3 tasks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a Web3Society with specialized agents for different Web3 domains."""
        self.config = config or {}
        
        # Create the core Web3 agent
        self.web3_agent = Web3Agent(self.config)
        
        # Create specialized agents for different Web3 domains
        self.blockchain_analyst = self._create_blockchain_analyst()
        self.smart_contract_expert = self._create_smart_contract_expert()
        self.defi_specialist = self._create_defi_specialist()
        self.nft_specialist = self._create_nft_specialist()
        self.research_agent = self._create_research_agent()
        
        # Build the society with all agents
        agents = [
            self.web3_agent,
            self.blockchain_analyst,
            self.smart_contract_expert,
            self.defi_specialist,
            self.nft_specialist,
            self.research_agent
        ]
        
        # Initialize the society with appropriate coordination strategy
        super().__init__(
            agents=agents,
            coordination_strategy=self.config.get("coordination_strategy", "hierarchical"),
            leader_agent_id=self.web3_agent.id if self.config.get("coordination_strategy") == "hierarchical" else None
        )
        
        # Share connection tools among agents that need them
        self._share_web3_connections()
    
    def _create_blockchain_analyst(self) -> Agent:
        """Create an agent specialized in blockchain data analysis."""
        return Agent(
            role="blockchain_analyst",
            tools=["code", "document", "search"],
            model=self.config.get("analyst_model", "gpt-4o"),
            memory_config={
                "type": "persistent",
                "path": f"{self.config.get('memory_path', './web3_society_memory')}/blockchain_analyst"
            },
            description=(
                "Specializes in analyzing blockchain data, transactions, and patterns. "
                "Executes data processing and visualizations on blockchain metrics."
            )
        )
    
    def _create_smart_contract_expert(self) -> Agent:
        """Create an agent specialized in smart contract analysis and development."""
        # Get the connection tool from the web3 agent
        connection_tool = self.web3_agent.connection_tool
        contract_tool = SmartContractTool(connection_tool)
        
        agent = Agent(
            role="smart_contract_expert",
            tools=["code", "document"],
            model=self.config.get("contract_model", "gpt-4o"),
            memory_config={
                "type": "persistent",
                "path": f"{self.config.get('memory_path', './web3_society_memory')}/smart_contract_expert"
            },
            description=(
                "Specializes in smart contract development, auditing, and analysis. "
                "Provides code reviews and identifies potential vulnerabilities."
            )
        )
        
        # Add the contract tool to this agent
        agent.add_tool(contract_tool)
        
        return agent
    
    def _create_defi_specialist(self) -> Agent:
        """Create an agent specialized in DeFi protocols and strategies."""
        # Get tools from the web3 agent
        connection_tool = self.web3_agent.connection_tool
        contract_tool = next((tool for tool in self.web3_agent.tools if tool.name == "smart_contract"), None)
        token_tool = next((tool for tool in self.web3_agent.tools if tool.name == "token"), None)
        
        # Create DeFi tool
        defi_tool = DeFiTool(connection_tool, contract_tool, token_tool)
        
        agent = Agent(
            role="defi_specialist",
            tools=["search", "document", "code"],
            model=self.config.get("defi_model", "gpt-4o"),
            memory_config={
                "type": "persistent",
                "path": f"{self.config.get('memory_path', './web3_society_memory')}/defi_specialist"
            },
            description=(
                "Specializes in decentralized finance protocols, yield strategies, and liquidity analysis. "
                "Provides insights on optimal strategies for different market conditions."
            )
        )
        
        # Add the DeFi tool to this agent
        agent.add_tool(defi_tool)
        
        return agent
    
    def _create_nft_specialist(self) -> Agent:
        """Create an agent specialized in NFTs and digital collectibles."""
        # Get tools from the web3 agent
        connection_tool = self.web3_agent.connection_tool
        contract_tool = next((tool for tool in self.web3_agent.tools if tool.name == "smart_contract"), None)
        
        # Create NFT tool
        nft_tool = NFTTool(connection_tool, contract_tool)
        
        agent = Agent(
            role="nft_specialist",
            tools=["search", "browser", "document"],
            model=self.config.get("nft_model", "gpt-4o"),
            memory_config={
                "type": "persistent",
                "path": f"{self.config.get('memory_path', './web3_society_memory')}/nft_specialist"
            },
            description=(
                "Specializes in NFT markets, collections, and trends. "
                "Provides analysis on NFT projects, rarity, and valuation."
            )
        )
        
        # Add the NFT tool to this agent
        agent.add_tool(nft_tool)
        
        return agent
    
    def _create_research_agent(self) -> Agent:
        """Create an agent specialized in Web3 research and documentation."""
        return Agent(
            role="web3_researcher",
            tools=["search", "browser", "document"],
            model=self.config.get("research_model", "gpt-4o"),
            memory_config={
                "type": "persistent",
                "path": f"{self.config.get('memory_path', './web3_society_memory')}/web3_researcher"
            },
            description=(
                "Specializes in researching Web3 projects, protocols, and trends. "
                "Gathers information, creates documentation, and stays updated on industry developments."
            )
        )
    
    def _share_web3_connections(self):
        """Share Web3 connection tools among agents to avoid duplicating connections."""
        # This method ensures that all agents use the same connection instances
        # for efficiency and consistency
        connection_tool = self.web3_agent.connection_tool
        
        # Could add more sophisticated connection sharing logic here
        pass
    
    def analyze_wallet(self, address: str, networks: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform comprehensive wallet analysis across multiple networks."""
        if networks is None:
            networks = ["ethereum"]
        
        task = f"Analyze the wallet {address} across {', '.join(networks)} networks."
        
        # First, gather basic information using the Web3 agent
        basic_info = self.web3_agent.wallet_status(address, networks)
        
        # Then, ask the society to analyze it in depth
        analysis_task = (
            f"Analyze the following wallet in detail:\n"
            f"Address: {address}\n"
            f"Basic Info: {json.dumps(basic_info, indent=2)}\n\n"
            f"Provide insights on:\n"
            f"1. Transaction patterns and history\n"
            f"2. Notable holdings (tokens, NFTs)\n"
            f"3. DeFi positions and strategies\n"
            f"4. Risk assessment\n"
            f"5. Recommendations based on the wallet profile"
        )
        
        analysis = self.run(analysis_task)
        
        return {
            "address": address,
            "networks": networks,
            "basic_info": basic_info,
            "analysis": analysis
        }
    
    def assess_smart_contract(self, contract_address: str, network: str = "ethereum") -> Dict[str, Any]:
        """Assess a smart contract for security, efficiency, and functionality."""
        task = (
            f"Perform a comprehensive assessment of smart contract at address {contract_address} "
            f"on {network} network.\n\n"
            f"1. Retrieve and analyze the contract code\n"
            f"2. Identify potential security vulnerabilities\n"
            f"3. Evaluate gas efficiency\n"
            f"4. Document contract functionality and interfaces\n"
            f"5. Provide recommendations for improvements"
        )
        
        assessment = self.run(task)
        
        return {
            "contract_address": contract_address,
            "network": network,
            "assessment": assessment
        }
    
    def analyze_defi_protocol(self, protocol_name: str, contract_addresses: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze a DeFi protocol in detail."""
        addresses_info = ""
        if contract_addresses:
            addresses_info = f"Key contract addresses: {', '.join(contract_addresses)}\n"
        
        task = (
            f"Analyze the DeFi protocol {protocol_name} in detail.\n"
            f"{addresses_info}\n"
            f"1. Protocol architecture and components\n"
            f"2. Tokenomics and incentive mechanisms\n"
            f"3. Current TVL, APYs, and performance metrics\n"
            f"4. Risk assessment\n"
            f"5. Competitive analysis\n"
            f"6. Strategic recommendations for users"
        )
        
        analysis = self.run(task)
        
        return {
            "protocol_name": protocol_name,
            "contract_addresses": contract_addresses,
            "analysis": analysis
        }
    
    def monitor_nft_collection(self, collection_address: str, network: str = "ethereum", period: str = "7d") -> Dict[str, Any]:
        """Monitor and analyze an NFT collection, including recent sales and trends."""
        task = (
            f"Monitor and analyze the NFT collection at address {collection_address} on {network} network "
            f"for the past {period}.\n\n"
            f"1. Collection overview and statistics\n"
            f"2. Recent sales and price trends\n"
            f"3. Notable holders and activity\n"
            f"4. Social sentiment and community engagement\n"
            f"5. Liquidity assessment\n"
            f"6. Projected value trend based on current patterns"
        )
        
        analysis = self.run(task)
        
        return {
            "collection_address": collection_address,
            "network": network,
            "period": period,
            "analysis": analysis
        }
    
    def draft_smart_contract(self, requirements: str, contract_type: str) -> Dict[str, Any]:
        """Draft a smart contract based on provided requirements."""
        task = (
            f"Draft a {contract_type} smart contract with the following requirements:\n\n"
            f"{requirements}\n\n"
            f"Provide:\n"
            f"1. Complete contract code with detailed comments\n"
            f"2. Deployment instructions\n"
            f"3. Security considerations\n"
            f"4. Optimization recommendations\n"
            f"5. Testing strategy"
        )
        
        draft = self.run(task)
        
        return {
            "contract_type": contract_type,
            "requirements": requirements,
            "draft": draft
        }
    
    def create_defi_strategy(self, investment_amount: float, risk_profile: str, tokens: List[str] = None) -> Dict[str, Any]:
        """Create a DeFi investment strategy based on user parameters."""
        tokens_list = ", ".join(tokens) if tokens else "various tokens"
        
        task = (
            f"Create a DeFi investment strategy with the following parameters:\n\n"
            f"Investment amount: ${investment_amount:,.2f}\n"
            f"Risk profile: {risk_profile}\n"
            f"Tokens of interest: {tokens_list}\n\n"
            f"Provide:\n"
            f"1. Asset allocation recommendation\n"
            f"2. Specific protocols and pools to utilize\n"
            f"3. Expected yields and risks\n"
            f"4. Entry and exit strategy\n"
            f"5. Monitoring and rebalancing guidelines\n"
            f"6. Tax and security considerations"
        )
        
        strategy = self.run(task)
        
        return {
            "investment_amount": investment_amount,
            "risk_profile": risk_profile,
            "tokens": tokens,
            "strategy": strategy
        }
    
    def analyze_token_economics(self, token_address: str, network: str = "ethereum") -> Dict[str, Any]:
        """Analyze tokenomics of a specific token."""
        task = (
            f"Analyze the tokenomics and fundamentals of the token at address {token_address} "
            f"on {network} network.\n\n"
            f"1. Supply and distribution metrics\n"
            f"2. Utility and use cases\n"
            f"3. Governance mechanisms\n"
            f"4. Emission schedule and inflation\n"
            f"5. Market performance and liquidity\n"
            f"6. Competitive positioning\n"
            f"7. Long-term sustainability assessment"
        )
        
        analysis = self.run(task)
        
        return {
            "token_address": token_address,
            "network": network,
            "analysis": analysis
        }
