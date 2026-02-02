#!/usr/bin/env python3
"""
Universal Bridge - Cross-platform agent protocol translation
Supports MCP, A2A, UCP, ACP protocols
"""

import json
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class Protocol(Enum):
    MCP = "mcp"
    A2A = "a2a"
    UCP = "ucp"
    ACP = "acp"
    ARP = "arp"


@dataclass
class CanonicalMessage:
    """Universal message format"""
    intent: str
    params: Dict[str, Any]
    context: Dict[str, Any]
    source_protocol: Protocol
    target_protocol: Optional[Protocol] = None
    
    def to_dict(self) -> Dict:
        return {
            "intent": self.intent,
            "params": self.params,
            "context": self.context,
            "source": self.source_protocol.value,
            "target": self.target_protocol.value if self.target_protocol else None
        }


class ProtocolAdapter:
    """Base class for protocol adapters"""
    
    def __init__(self, protocol: Protocol):
        self.protocol = protocol
        self.handlers: Dict[str, Callable] = {}
    
    def to_canonical(self, message: Any) -> CanonicalMessage:
        """Convert protocol-specific message to canonical"""
        raise NotImplementedError
    
    def from_canonical(self, message: CanonicalMessage) -> Any:
        """Convert canonical message to protocol-specific"""
        raise NotImplementedError


class MCPAdapter(ProtocolAdapter):
    """Model Context Protocol adapter"""
    
    def __init__(self):
        super().__init__(Protocol.MCP)
    
    def to_canonical(self, message: Dict) -> CanonicalMessage:
        """MCP tools/call -> Canonical"""
        return CanonicalMessage(
            intent=f"mcp.{message.get('name', 'unknown')}",
            params=message.get("arguments", {}),
            context={"tool_call_id": message.get("id")},
            source_protocol=Protocol.MCP
        )
    
    def from_canonical(self, message: CanonicalMessage) -> Dict:
        """Canonical -> MCP tools/call"""
        tool_name = message.intent.replace("mcp.", "")
        return {
            "id": message.context.get("tool_call_id", "call_001"),
            "type": "function",
            "function": {
                "name": tool_name,
                "arguments": json.dumps(message.params)
            }
        }


class A2AAdapter(ProtocolAdapter):
    """Agent2Agent protocol adapter"""
    
    def __init__(self):
        super().__init__(Protocol.A2A)
    
    def to_canonical(self, message: Dict) -> CanonicalMessage:
        """A2A action -> Canonical"""
        return CanonicalMessage(
            intent=f"a2a.{message.get('action_id', 'unknown')}",
            params=message.get("payload", {}),
            context={"agent_id": message.get("agent_id")},
            source_protocol=Protocol.A2A
        )
    
    def from_canonical(self, message: CanonicalMessage) -> Dict:
        """Canonical -> A2A action"""
        action_id = message.intent.replace("a2a.", "")
        return {
            "action_id": action_id,
            "agent_id": message.context.get("agent_id", "unknown"),
            "payload": message.params
        }


class UniversalBridge:
    """
    Universal protocol bridge
    Routes messages between different agent protocols
    """
    
    def __init__(self):
        self.adapters: Dict[Protocol, ProtocolAdapter] = {
            Protocol.MCP: MCPAdapter(),
            Protocol.A2A: A2AAdapter(),
        }
        self.routes: Dict[str, Dict] = {}  # agent_id -> {protocol, endpoint}
        self.metrics = {
            "messages_routed": 0,
            "translations": {p.value: 0 for p in Protocol}
        }
    
    def register_agent(
        self,
        agent_id: str,
        protocol: Protocol,
        endpoint: str,
        capabilities: list
    ):
        """Register an agent with the bridge"""
        self.routes[agent_id] = {
            "protocol": protocol,
            "endpoint": endpoint,
            "capabilities": capabilities
        }
        print(f"✓ Registered {agent_id} ({protocol.value}) at {endpoint}")
    
    async def route(
        self,
        from_protocol: Protocol,
        to_protocol: Protocol,
        message: Any
    ) -> Any:
        """
        Route a message between protocols
        
        Flow:
        1. Convert source -> canonical
        2. (Optional) Transform/modify
        3. Convert canonical -> target
        """
        # Get adapters
        from_adapter = self.adapters.get(from_protocol)
        to_adapter = self.adapters.get(to_protocol)
        
        if not from_adapter or not to_adapter:
            raise ValueError(f"Unsupported protocol: {from_protocol} -> {to_protocol}")
        
        # Convert to canonical
        canonical = from_adapter.to_canonical(message)
        canonical.target_protocol = to_protocol
        
        # Transform (add routing info, etc.)
        canonical.context["bridge_routed"] = True
        canonical.context["bridge_timestamp"] = "2026-02-02T18:00:00Z"
        
        # Convert to target
        result = to_adapter.from_canonical(canonical)
        
        # Update metrics
        self.metrics["messages_routed"] += 1
        self.metrics["translations"][from_protocol.value] += 1
        self.metrics["translations"][to_protocol.value] += 1
        
        return result
    
    async def discover(self, capability: str) -> list:
        """Discover agents with specific capability"""
        matching = []
        for agent_id, info in self.routes.items():
            if capability in info.get("capabilities", []):
                matching.append({
                    "agent_id": agent_id,
                    "protocol": info["protocol"].value,
                    "endpoint": info["endpoint"]
                })
        return matching
    
    def get_metrics(self) -> Dict:
        """Get bridge metrics"""
        return {
            **self.metrics,
            "registered_agents": len(self.routes)
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def demo():
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║           UNIVERSAL BRIDGE DEMO                                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print()
        
        bridge = UniversalBridge()
        
        # Register agents
        bridge.register_agent(
            "agent:mcp_server",
            Protocol.MCP,
            "http://localhost:8000/mcp",
            ["search", "calculate", "retrieve"]
        )
        
        bridge.register_agent(
            "agent:a2a_worker",
            Protocol.A2A,
            "http://localhost:9000/a2a",
            ["process", "analyze", "generate"]
        )
        
        print()
        print("📨 Routing MCP -> A2A:")
        
        # MCP tool call
        mcp_message = {
            "id": "call_123",
            "name": "search_documents",
            "arguments": {"query": "agent protocols", "limit": 10}
        }
        
        print(f"  MCP Input: {json.dumps(mcp_message, indent=2)}")
        
        result = await bridge.route(
            from_protocol=Protocol.MCP,
            to_protocol=Protocol.A2A,
            message=mcp_message
        )
        
        print(f"\n  A2A Output: {json.dumps(result, indent=2)}")
        
        print()
        print("📊 Metrics:")
        metrics = bridge.get_metrics()
        print(f"  Registered agents: {metrics['registered_agents']}")
        print(f"  Messages routed: {metrics['messages_routed']}")
        
        print()
        print("🔍 Discover agents with 'search' capability:")
        agents = await bridge.discover("search")
        for a in agents:
            print(f"  - {a['agent_id']} ({a['protocol']})")
    
    asyncio.run(demo())
