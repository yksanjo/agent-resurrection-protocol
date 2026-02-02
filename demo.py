#!/usr/bin/env python3
"""
Agent Resurrection Protocol - Full Demo
Shows decentralized persistence, cross-platform bridging, and energy management
"""

import asyncio
import json
from arp.core import AgentResurrection
from arp.bridge import UniversalBridge, Protocol
from arp.energy import EnergyGovernor, ComputeClass


async def full_demo():
    """Complete ARP demonstration"""
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║     🤖 AGENT RESURRECTION PROTOCOL - FULL DEMO                   ║")
    print("║                                                                  ║")
    print("║   Decentralized persistence | Cross-platform | Energy-aware      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # ═════════════════════════════════════════════════════════════════
    # PART 1: DECENTRALIZED AGENT PERSISTENCE
    # ═════════════════════════════════════════════════════════════════
    
    print("=" * 70)
    print("🧬 PART 1: DECENTRALIZED AGENT PERSISTENCE")
    print("=" * 70)
    print()
    
    # Create an agent
    class ResearchAgent:
        """Example research agent"""
        def __init__(self):
            self.memory = []
            self.tasks_completed = 0
        
        async def execute(self, task):
            self.memory.append(task)
            self.tasks_completed += 1
            return {
                "status": "completed",
                "task": task["name"],
                "insights": f"Analyzed {len(self.memory)} data points"
            }
    
    agent = ResearchAgent()
    arp = AgentResurrection(
        agent=agent,
        checkpoint_interval=5  # Fast checkpointing for demo
    )
    
    print(f"✨ Agent created: {arp.agent_id}")
    print(f"   Initial state: {agent.tasks_completed} tasks completed")
    print()
    
    # Execute some tasks
    print("📋 Executing research tasks...")
    for i in range(3):
        result = await arp.execute({
            "name": f"research_task_{i}",
            "type": "data_analysis",
            "data": f"dataset_{i}"
        })
        print(f"   Task {i+1}: {result['insights']}")
    
    print(f"\n   State before hibernation: {agent.tasks_completed} tasks")
    print()
    
    # Hibernate (shutdown)
    print("🦇 HIBERNATING AGENT...")
    checkpoint = await arp.hibernate()
    print(f"   ✓ Saved to: {checkpoint.storage}")
    print()
    
    # RESURRECTION on a different "node"
    print("✨ RESURRECTING ON NEW NODE...")
    arp2 = await AgentResurrection.load(arp.agent_id)
    
    # Continue work
    print("\n📋 Continuing research after resurrection...")
    result = await arp2.execute({
        "name": "post_resurrection_analysis",
        "type": "synthesis",
        "data": "all_previous_results"
    })
    print(f"   Result: {result.get('insights', result.get('result', 'completed'))}")
    print(f"   Total checkpoints: {arp2.sequence}")
    print()
    
    # ═════════════════════════════════════════════════════════════════
    # PART 2: UNIVERSAL BRIDGE (Cross-Platform)
    # ═════════════════════════════════════════════════════════════════
    
    print("=" * 70)
    print("🌉 PART 2: UNIVERSAL CROSS-PLATFORM BRIDGE")
    print("=" * 70)
    print()
    
    bridge = UniversalBridge()
    
    # Register agents from different platforms
    bridge.register_agent(
        "claude-desktop",
        Protocol.MCP,
        "http://localhost:8000",
        ["search", "code", "analyze"]
    )
    
    bridge.register_agent(
        "google-a2a-worker",
        Protocol.A2A,
        "http://localhost:9000",
        ["process", "generate", "search"]
    )
    
    bridge.register_agent(
        "moltbook-agent",
        Protocol.UCP,
        "https://moltbook.com/api",
        ["post", "comment", "vote"]
    )
    
    print()
    print("📨 CROSS-PLATFORM MESSAGE ROUTING:")
    print()
    
    # Route MCP -> A2A
    mcp_tool_call = {
        "id": "call_001",
        "name": "search_documents",
        "arguments": {"query": "agent coordination protocols"}
    }
    
    print("MCP (Claude) wants to call a tool:")
    print(json.dumps(mcp_tool_call, indent=2))
    print()
    
    a2a_action = await bridge.route(
        from_protocol=Protocol.MCP,
        to_protocol=Protocol.A2A,
        message=mcp_tool_call
    )
    
    print("→ Translated to A2A action for Google agent:")
    print(json.dumps(a2a_action, indent=2))
    print()
    
    # Discover capabilities
    print("🔍 DISCOVERY:")
    search_agents = await bridge.discover("search")
    print(f"   Agents with 'search' capability: {len(search_agents)}")
    for a in search_agents:
        print(f"   - {a['agent_id']} ({a['protocol']})")
    print()
    
    # ═════════════════════════════════════════════════════════════════
    # PART 3: ENERGY-AWARE EXECUTION
    # ═════════════════════════════════════════════════════════════════
    
    print("=" * 70)
    print("⚡ PART 3: ENERGY & CARBON MANAGEMENT")
    print("=" * 70)
    print()
    
    # Create energy-conscious governor
    governor = EnergyGovernor(
        renewable_only=True,
        max_latency_ms=3000,
        budget_usd_per_hour=0.50
    )
    
    print("🌱 Running with RENEWABLE-ONLY constraint...")
    print()
    
    tasks = [
        ("light_inference", ComputeClass.CPU_LIGHT),
        ("document_processing", ComputeClass.CPU_HEAVY),
        ("model_training", ComputeClass.GPU),
    ]
    
    for task_name, compute in tasks:
        print(f"📋 Task: {task_name} ({compute.value})")
        result = await governor.execute(
            task={"name": task_name},
            compute_class=compute
        )
        energy = result['energy']
        print(f"   Region: {energy['region']}")
        print(f"   Carbon: {energy['carbon_g']:.1f}g CO₂")
        print(f"   Cost: ${energy['cost_usd']:.3f}")
        print(f"   Renewable: {'✅ Yes' if energy['renewable'] else '❌ No'}")
        print()
    
    # Stats
    stats = governor.get_stats()
    print("📊 ENERGY SUMMARY:")
    print(f"   Total tasks: {stats['total_executions']}")
    print(f"   Total carbon: {stats['total_carbon_g']:.1f}g CO₂")
    print(f"   Total cost: ${stats['total_cost_usd']:.3f}")
    print(f"   Avg per task: {stats.get('avg_carbon_per_execution', 0):.1f}g CO₂")
    print()
    
    # ═════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═════════════════════════════════════════════════════════════════
    
    print("=" * 70)
    print("🎯 SUMMARY: AGENT RESURRECTION PROTOCOL")
    print("=" * 70)
    print()
    print("✅ Decentralized Persistence:")
    print(f"   • Agent {arp.agent_id} hibernated and resurrected")
    print(f"   • State preserved across sessions")
    print(f"   • {arp2.sequence} checkpoints maintained")
    print()
    print("✅ Universal Bridge:")
    print(f"   • 3 platforms connected (MCP, A2A, UCP)")
    print(f"   • {bridge.get_metrics()['messages_routed']} messages routed")
    print(f"   • Cross-platform discovery working")
    print()
    print("✅ Energy Management:")
    print(f"   • {stats['total_executions']} tasks optimized")
    print(f"   • Renewable-only constraint enforced")
    print(f"   • ${stats['total_cost_usd']:.3f} total cost")
    print()
    print("=" * 70)
    print("🚀 The future of agents is:")
    print("   • Persistent (survive shutdown)")
    print("   • Interoperable (cross-platform)")
    print("   • Sustainable (carbon-aware)")
    print("=" * 70)
    print()
    print("📁 Checkpoints saved to: ./checkpoints/")
    print("🔗 GitHub: github.com/yksanjo/agent-resurrection-protocol")


if __name__ == "__main__":
    asyncio.run(full_demo())
