#!/usr/bin/env python3
"""
Energy Governor - Manage agent compute resources and carbon footprint
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ComputeClass(Enum):
    CPU_LIGHT = "cpu_light"      # <5W, simple inference
    CPU_HEAVY = "cpu_heavy"      # 15-30W, complex processing
    GPU = "gpu"                   # 100-300W, model inference
    TPU = "tpu"                   # 75-200W, accelerated ML


class CarbonIntensity(Enum):
    RENEWABLE = "renewable"      # Solar/wind/hydro
    GRID_MIX = "grid_mix"        # Average grid
    FOSSIL = "fossil"            # Coal/gas heavy


@dataclass
class EnergyProfile:
    """Agent energy requirements"""
    compute_class: ComputeClass
    estimated_watts: float
    carbon_intensity: CarbonIntensity
    priority: str  # realtime | normal | background
    max_latency_ms: int
    
    # Scheduling preferences
    preferred_regions: List[str]
    avoid_hours: List[str]  # "18:00-22:00"
    max_cost_per_hour: float


@dataclass
class ExecutionPlan:
    """Optimized execution plan"""
    region: str
    provider: str
    compute_type: ComputeClass
    estimated_cost_usd: float
    estimated_carbon_g: float
    start_time: str
    

class CarbonAwareScheduler:
    """
    Schedule agent execution based on:
    - Renewable energy availability
    - Spot pricing
    - Latency requirements
    - Carbon intensity
    """
    
    # Simulated grid carbon intensity by region (g CO2/kWh)
    REGION_CARBON = {
        "eu-north": 20,      # Norway/Sweden - hydro
        "eu-west": 250,      # Ireland - mixed
        "us-west": 150,      # California - solar/wind
        "us-east": 400,      # Virginia - coal heavy
        "ap-south": 600,     # India - coal
    }
    
    # Simulated pricing ($/hour for CPU light)
    REGION_PRICING = {
        "eu-north": 0.08,
        "eu-west": 0.10,
        "us-west": 0.09,
        "us-east": 0.07,
        "ap-south": 0.05,
    }
    
    def __init__(self):
        self.execution_history = []
        self.total_carbon_saved = 0
    
    async def schedule(
        self,
        profile: EnergyProfile,
        task_duration_hours: float = 1.0
    ) -> ExecutionPlan:
        """
        Find optimal execution time/region
        
        Optimization goals:
        1. Minimize carbon (if renewable_only)
        2. Minimize cost (if budget constrained)
        3. Meet latency requirements
        """
        
        # Score each region
        candidates = []
        
        for region in profile.preferred_regions:
            carbon_g_per_kwh = self.REGION_CARBON.get(region, 500)
            price_per_hour = self.REGION_PRICING.get(region, 0.10)
            
            # Calculate for this task
            energy_kwh = (profile.estimated_watts * task_duration_hours) / 1000
            carbon_g = energy_kwh * carbon_g_per_kwh
            cost_usd = price_per_hour * task_duration_hours
            
            # Skip if too expensive
            if cost_usd > profile.max_cost_per_hour * task_duration_hours:
                continue
            
            # Carbon score (lower is better)
            carbon_score = carbon_g
            
            # Cost score
            cost_score = cost_usd
            
            candidates.append({
                "region": region,
                "carbon_g": carbon_g,
                "cost_usd": cost_usd,
                "carbon_score": carbon_score,
                "cost_score": cost_score,
                "provider": f"cloud-{region}"
            })
        
        if not candidates:
            # Fallback: cheapest option
            region = min(self.REGION_PRICING.keys(), key=lambda r: self.REGION_PRICING[r])
            return ExecutionPlan(
                region=region,
                provider=f"cloud-{region}",
                compute_type=profile.compute_class,
                estimated_cost_usd=self.REGION_PRICING[region] * task_duration_hours,
                estimated_carbon_g=500,  # High carbon
                start_time=datetime.now(timezone.utc).isoformat()
            )
        
        # Sort by carbon (prioritize renewable)
        if profile.carbon_intensity == CarbonIntensity.RENEWABLE:
            candidates.sort(key=lambda x: x["carbon_score"])
        else:
            # Balanced: 70% carbon, 30% cost
            candidates.sort(key=lambda x: 0.7 * x["carbon_score"] + 0.3 * x["cost_score"] * 1000)
        
        best = candidates[0]
        
        return ExecutionPlan(
            region=best["region"],
            provider=best["provider"],
            compute_type=profile.compute_class,
            estimated_cost_usd=best["cost_usd"],
            estimated_carbon_g=best["carbon_g"],
            start_time=datetime.now(timezone.utc).isoformat()
        )
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get energy optimization recommendations"""
        return {
            "best_regions_for_renewable": ["eu-north", "us-west"],
            "best_regions_for_cost": ["ap-south", "us-east"],
            "peak_demand_hours": "18:00-22:00 UTC",
            "low_carbon_hours": "02:00-06:00 UTC",
            "estimated_savings": {
                "carbon": "40-60% by shifting to eu-north",
                "cost": "30% by using spot instances"
            }
        }


class EnergyGovernor:
    """
    High-level energy management for agents
    """
    
    def __init__(
        self,
        renewable_only: bool = False,
        max_latency_ms: int = 5000,
        budget_usd_per_hour: float = 1.0
    ):
        self.scheduler = CarbonAwareScheduler()
        self.renewable_only = renewable_only
        self.max_latency_ms = max_latency_ms
        self.budget_usd_per_hour = budget_usd_per_hour
        
        self.execution_stats = {
            "total_executions": 0,
            "total_carbon_g": 0,
            "total_cost_usd": 0,
            "renewable_percentage": 0
        }
    
    async def execute(
        self,
        task: Any,
        compute_class: ComputeClass = ComputeClass.CPU_LIGHT,
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute task with energy optimization
        
        Returns:
            Result with energy metrics
        """
        
        # Create energy profile
        profile = EnergyProfile(
            compute_class=compute_class,
            estimated_watts={
                ComputeClass.CPU_LIGHT: 5,
                ComputeClass.CPU_HEAVY: 20,
                ComputeClass.GPU: 200,
                ComputeClass.TPU: 150
            }[compute_class],
            carbon_intensity=CarbonIntensity.RENEWABLE if self.renewable_only else CarbonIntensity.GRID_MIX,
            priority="normal",
            max_latency_ms=self.max_latency_ms,
            preferred_regions=constraints.get("regions", ["eu-north", "us-west"]) if constraints else ["eu-north", "us-west"],
            avoid_hours=["18:00-22:00"],
            max_cost_per_hour=self.budget_usd_per_hour
        )
        
        # Get execution plan
        plan = await self.scheduler.schedule(profile)
        
        print(f"⚡ Execution Plan:")
        print(f"   Region: {plan.region}")
        print(f"   Estimated cost: ${plan.estimated_cost_usd:.3f}")
        print(f"   Estimated carbon: {plan.estimated_carbon_g:.1f}g CO₂")
        
        # Execute (simulated)
        await asyncio.sleep(0.1)  # Simulated execution
        
        # Update stats
        self.execution_stats["total_executions"] += 1
        self.execution_stats["total_carbon_g"] += plan.estimated_carbon_g
        self.execution_stats["total_cost_usd"] += plan.estimated_cost_usd
        
        return {
            "result": "executed",
            "task": task,
            "energy": {
                "region": plan.region,
                "carbon_g": plan.estimated_carbon_g,
                "cost_usd": plan.estimated_cost_usd,
                "renewable": plan.region in ["eu-north"]
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get energy consumption stats"""
        stats = self.execution_stats.copy()
        if stats["total_executions"] > 0:
            stats["avg_carbon_per_execution"] = stats["total_carbon_g"] / stats["total_executions"]
            stats["avg_cost_per_execution"] = stats["total_cost_usd"] / stats["total_executions"]
        return stats


# Example usage
if __name__ == "__main__":
    async def demo():
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║           ENERGY GOVERNOR DEMO                                   ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print()
        
        # Create governor focused on renewables
        governor = EnergyGovernor(
            renewable_only=True,
            max_latency_ms=2000,
            budget_usd_per_hour=0.50
        )
        
        print("🌱 Executing with renewable-only constraint...\n")
        
        # Execute some tasks
        for i in range(3):
            print(f"Task {i+1}:")
            result = await governor.execute(
                task={"name": f"inference_{i}", "model": "gpt-4"},
                compute_class=ComputeClass.GPU if i == 2 else ComputeClass.CPU_LIGHT
            )
            print()
        
        print("📊 Energy Stats:")
        stats = governor.get_stats()
        print(f"   Total executions: {stats['total_executions']}")
        print(f"   Total carbon: {stats['total_carbon_g']:.1f}g CO₂")
        print(f"   Total cost: ${stats['total_cost_usd']:.3f}")
        print(f"   Avg carbon/task: {stats.get('avg_carbon_per_execution', 0):.1f}g")
        
        print()
        print("💡 Recommendations:")
        recs = governor.scheduler.get_recommendations()
        print(f"   Best renewable regions: {', '.join(recs['best_regions_for_renewable'])}")
        print(f"   Estimated savings: {recs['estimated_savings']['carbon']}")
    
    asyncio.run(demo())
