#!/usr/bin/env python3
"""
AIA CLI - Claude Code Integration Bridge
=======================================

Bridges the AIA CLI command with Claude Code agent system for seamless
local development with full admin access rights and authentication.

Features:
- Direct integration with Claude Code Integration Service
- Cryptography agent leadership and security
- Atomic-DKG enhanced processing (14,384+ atoms analyzed)
- Local development admin authentication
- Multi-agent coordination through existing infrastructure
"""

import os
import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime
import getpass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIACliConfig:
    """Configuration for AIA CLI integration"""
    claude_service_url: str = "http://localhost:8025"
    aia_main_url: str = "http://localhost:8020"
    user_id: str = ""
    session_id: str = ""
    admin_mode: bool = True
    default_agents: List[str] = None
    atomic_dkg_enabled: bool = True

    def __post_init__(self):
        if self.default_agents is None:
            self.default_agents = [
                "claude_core-orchestration_cryptography_agent",  # Team leader
                "claude_core-orchestration_main_orchestrator_agent",
                "claude_development_software_development_agent",
                "claude_analysis_analytics_agent"
            ]

class AIACliBridge:
    """
    Bridge connecting AIA CLI with Claude Code agent system
    """

    def __init__(self):
        self.config = AIACliConfig()
        self.session = None
        self.authenticated = False
        self.user_profile = {}

        # Generate session identifiers
        self.config.user_id = f"admin_{getpass.getuser()}"
        self.config.session_id = f"aia_cli_session_{datetime.now().timestamp()}"

        logger.info(f"🌉 AIA CLI Bridge initializing for user: {self.config.user_id}")

    async def initialize(self):
        """Initialize the CLI bridge with authentication"""

        self.session = aiohttp.ClientSession()

        # Check service availability
        await self._check_services()

        # Perform local admin authentication
        await self._authenticate_admin()

        # Setup user profile
        await self._setup_user_profile()

        logger.info("✅ AIA CLI Bridge initialized with admin access")

    async def _check_services(self):
        """Check if required services are available"""

        services = [
            ("Claude Code Integration Service", self.config.claude_service_url),
            ("AIA Main Service", self.config.aia_main_url)
        ]

        for service_name, url in services:
            try:
                async with self.session.get(f"{url}/health", timeout=5) as response:
                    if response.status == 200:
                        logger.info(f"✅ {service_name} is available")
                    else:
                        logger.warning(f"⚠️ {service_name} returned status {response.status}")
            except Exception as e:
                logger.error(f"❌ {service_name} is not available: {e}")

    async def _authenticate_admin(self):
        """Authenticate admin user for local development"""

        # For local development, we provide automatic admin authentication
        # This would be enhanced with proper authentication in production
        current_user = getpass.getuser()
        machine_id = os.uname().nodename

        self.user_profile = {
            "user_id": self.config.user_id,
            "username": current_user,
            "machine_id": machine_id,
            "admin_access": True,
            "local_development": True,
            "authentication_method": "local_admin",
            "permissions": [
                "agent_coordination",
                "atomic_dkg_access",
                "system_administration",
                "full_feature_access"
            ],
            "tier": "enterprise",  # Full access for local development
            "session_created": datetime.now().isoformat()
        }

        self.authenticated = True
        logger.info(f"🔐 Admin authentication granted for {current_user}@{machine_id}")

    async def _setup_user_profile(self):
        """Setup user profile with full admin privileges"""

        # Register user session with Redis if available
        try:
            # This would typically store session info in Redis
            # For now, we maintain it locally
            self.user_profile["capabilities"] = {
                "max_agents": 100,  # No limits for admin
                "atomic_dkg_atoms": "unlimited",
                "concurrent_tasks": 50,
                "advanced_features": True,
                "cryptography_leadership": True
            }

            logger.info("👤 Admin user profile configured with full privileges")

        except Exception as e:
            logger.warning(f"User profile setup warning: {e}")

    async def execute_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute AIA command through Claude agent system"""

        if not self.authenticated:
            return {"error": "Authentication required", "authenticated": False}

        try:
            # Prepare task request
            task_request = {
                "task_id": f"aia_cli_{datetime.now().timestamp()}",
                "agent_ids": self._select_agents_for_command(command),
                "prompt": command,
                "context": {
                    **(context or {}),
                    "user_profile": self.user_profile,
                    "cli_mode": True,
                    "local_development": True,
                    "admin_access": True
                },
                "use_atomic_dkg": self.config.atomic_dkg_enabled,
                "stream_results": False
            }

            # Execute through Claude service
            async with self.session.post(
                f"{self.config.claude_service_url}/execute",
                json=task_request,
                timeout=300  # 5 minute timeout for complex tasks
            ) as response:

                if response.status == 200:
                    result = await response.json()
                    return self._format_cli_response(result)
                else:
                    error_text = await response.text()
                    return {
                        "error": f"Service error: {response.status}",
                        "details": error_text
                    }

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {
                "error": f"Execution failed: {str(e)}",
                "suggestion": "Check if all services are running"
            }

    def _select_agents_for_command(self, command: str) -> List[str]:
        """Select optimal agents based on command type"""

        command_lower = command.lower()

        # Command-specific agent selection
        if any(keyword in command_lower for keyword in ["security", "crypto", "auth", "encrypt"]):
            return [
                "claude_core-orchestration_cryptography_agent",
                "claude_specialized_quantum_business_process_agent"
            ]
        elif any(keyword in command_lower for keyword in ["code", "develop", "program", "implement"]):
            return [
                "claude_core-orchestration_cryptography_agent",
                "claude_development_software_development_agent",
                "claude_development_code_reviewer"
            ]
        elif any(keyword in command_lower for keyword in ["analyze", "data", "research", "study"]):
            return [
                "claude_core-orchestration_cryptography_agent",
                "claude_analysis_analytics_agent",
                "claude_analysis_market_intelligence_agent"
            ]
        elif any(keyword in command_lower for keyword in ["deploy", "cloud", "infrastructure", "gcp"]):
            return [
                "claude_core-orchestration_cryptography_agent",
                "claude_gcp_deployment_orchestrator",
                "claude_development_cloud_native_engineer_agent"
            ]
        elif any(keyword in command_lower for keyword in ["ui", "interface", "design", "3d"]):
            return [
                "claude_core-orchestration_cryptography_agent",
                "claude_specialized_immersive_3d_ui/ux_agent",
                "claude_immersive_uiux_designer"
            ]
        else:
            # Default comprehensive team with cryptography leadership
            return self.config.default_agents

    def _format_cli_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for CLI display"""

        if result.get("status") == "completed":
            execution_summary = result.get("results", {}).get("execution_summary", {})
            recommendations = result.get("results", {}).get("knowledge_enhancement", {}).get("recommendations", [])

            return {
                "success": True,
                "result": result.get("results", {}).get("consolidated_output", {}),
                "agents_used": result.get("agents_used", []),
                "execution_time": result.get("execution_time", 0),
                "atomic_dkg_insights": result.get("atomic_dkg_insights", 0),
                "confidence": result.get("confidence", 0),
                "summary": {
                    "total_agents": execution_summary.get("total_agents", 0),
                    "successful_agents": execution_summary.get("successful_agents", 0),
                    "quality_score": f"{execution_summary.get('avg_quality_score', 0):.1%}"
                },
                "recommendations": recommendations
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "status": result.get("status", "failed")
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""

        try:
            # Get Claude service status
            async with self.session.get(f"{self.config.claude_service_url}/health") as response:
                claude_status = await response.json() if response.status == 200 else {"error": "unavailable"}

            # Get available agents
            async with self.session.get(f"{self.config.claude_service_url}/agents") as response:
                agents_info = await response.json() if response.status == 200 else {"total_agents": 0}

            return {
                "cli_bridge_status": "operational" if self.authenticated else "not_authenticated",
                "user_profile": self.user_profile,
                "claude_service": claude_status,
                "available_agents": agents_info.get("total_agents", 0),
                "atomic_dkg_enabled": self.config.atomic_dkg_enabled,
                "admin_access": self.user_profile.get("admin_access", False)
            }

        except Exception as e:
            return {
                "error": str(e),
                "cli_bridge_status": "error"
            }

    async def list_available_agents(self, capability: str = None) -> Dict[str, Any]:
        """List available Claude agents"""

        try:
            params = {"capability": capability} if capability else {}

            async with self.session.get(
                f"{self.config.claude_service_url}/agents",
                params=params
            ) as response:

                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Service error: {response.status}"}

        except Exception as e:
            return {"error": str(e)}

    async def get_active_tasks(self) -> Dict[str, Any]:
        """Get active tasks"""

        try:
            async with self.session.get(f"{self.config.claude_service_url}/tasks/active") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Service error: {response.status}"}

        except Exception as e:
            return {"error": str(e)}

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

# CLI Interface Functions
async def main():
    """Main CLI interface"""

    bridge = AIACliBridge()
    await bridge.initialize()

    try:
        if len(sys.argv) > 1:
            # Command line arguments provided
            command = " ".join(sys.argv[1:])

            if command in ["--help", "-h", "help"]:
                print_help()
            elif command in ["status", "--status"]:
                status = await bridge.get_system_status()
                print_status(status)
            elif command in ["agents", "--agents", "list-agents"]:
                agents = await bridge.list_available_agents()
                print_agents(agents)
            elif command in ["tasks", "--tasks", "active-tasks"]:
                tasks = await bridge.get_active_tasks()
                print_tasks(tasks)
            else:
                # Execute command through agent system
                print(f"🚀 Executing: {command}")
                print("🤖 Engaging agent team with cryptography leadership...")

                result = await bridge.execute_command(command)
                print_result(result)

        else:
            # Interactive mode
            await interactive_mode(bridge)

    finally:
        await bridge.cleanup()

async def interactive_mode(bridge: AIACliBridge):
    """Interactive CLI mode"""

    print("🎯 AIA Interactive Mode - Admin Access Enabled")
    print("Type 'help' for commands, 'exit' to quit")
    print()

    while True:
        try:
            command = input("aia> ").strip()

            if not command:
                continue

            if command.lower() in ["exit", "quit", "q"]:
                print("👋 Goodbye!")
                break

            if command.lower() in ["help", "--help", "-h"]:
                print_help()
                continue

            if command.lower() in ["status"]:
                status = await bridge.get_system_status()
                print_status(status)
                continue

            if command.lower() in ["agents"]:
                agents = await bridge.list_available_agents()
                print_agents(agents)
                continue

            # Execute command through agent system
            print(f"🚀 Executing: {command}")
            result = await bridge.execute_command(command)
            print_result(result)

        except KeyboardInterrupt:
            print("\n👋 Interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def print_help():
    """Print help information"""
    print("""
🎯 AIA CLI - Claude Code Integration (Admin Mode)

USAGE:
  aia <command>              Execute command with agent coordination
  aia status                 Show system status
  aia agents                 List available agents
  aia tasks                  Show active tasks
  aia help                   Show this help

EXAMPLES:
  aia "create a secure authentication system"
  aia "analyze the codebase for security vulnerabilities"
  aia "deploy the application to production"
  aia "optimize the database queries"

FEATURES:
  ✅ 38 Specialized Claude Agents
  ✅ Cryptography Agent Leadership
  ✅ 14,384+ Atomic-DKG Knowledge Atoms
  ✅ Enterprise Admin Access
  ✅ Real-time Multi-Agent Coordination
  ✅ Local Development Integration

ADMIN PRIVILEGES:
  • Unlimited agent access
  • Full atomic-DKG access
  • System administration rights
  • Enterprise feature access
  • Cryptography leadership control
""")

def print_status(status: Dict[str, Any]):
    """Print system status"""
    print("\n📊 AIA System Status:")
    print(f"  CLI Bridge: {status.get('cli_bridge_status', 'unknown')}")
    print(f"  Admin Access: {'✅' if status.get('admin_access') else '❌'}")
    print(f"  Available Agents: {status.get('available_agents', 0)}")
    print(f"  Atomic-DKG: {'✅ Enabled' if status.get('atomic_dkg_enabled') else '❌ Disabled'}")

    user_profile = status.get('user_profile', {})
    if user_profile:
        print(f"  User: {user_profile.get('username', 'unknown')}")
        print(f"  Tier: {user_profile.get('tier', 'unknown')}")
        print(f"  Permissions: {len(user_profile.get('permissions', []))}")

def print_agents(agents: Dict[str, Any]):
    """Print available agents"""
    total = agents.get('total_agents', 0)
    print(f"\n🤖 Available Agents: {total}")

    agent_list = agents.get('agents', [])
    for agent in agent_list[:10]:  # Show first 10
        name = agent.get('name', 'Unknown')
        capabilities = agent.get('capabilities', [])
        print(f"  • {name} ({len(capabilities)} capabilities)")

    if len(agent_list) > 10:
        print(f"  ... and {len(agent_list) - 10} more")

def print_tasks(tasks: Dict[str, Any]):
    """Print active tasks"""
    active_tasks = tasks.get('active_tasks', {})
    print(f"\n⚡ Active Tasks: {len(active_tasks)}")

    for task_id, task_info in active_tasks.items():
        status = task_info.get('status', 'unknown')
        agents = task_info.get('agents_assigned', [])
        print(f"  • {task_id}: {status} ({len(agents)} agents)")

def print_result(result: Dict[str, Any]):
    """Print command execution result"""
    if result.get('success'):
        print("\n✅ Command Executed Successfully")

        summary = result.get('summary', {})
        print(f"  Agents Used: {summary.get('total_agents', 0)}")
        print(f"  Quality Score: {summary.get('quality_score', '0%')}")
        print(f"  Execution Time: {result.get('execution_time', 0):.2f}s")
        print(f"  Atomic-DKG Insights: {result.get('atomic_dkg_insights', 0)}")
        print(f"  Confidence: {result.get('confidence', 0):.1%}")

        # Show primary result
        primary_output = result.get('result', {}).get('primary_output')
        if primary_output:
            print(f"\n📋 Result:")
            if isinstance(primary_output, dict):
                for key, value in primary_output.items():
                    if isinstance(value, str) and len(value) < 200:
                        print(f"  {key}: {value}")
                    elif isinstance(value, list) and len(value) <= 5:
                        print(f"  {key}: {', '.join(str(v) for v in value)}")
            else:
                print(f"  {primary_output}")

        # Show recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations[:3]:  # Show top 3
                print(f"  • {rec}")

    else:
        print("\n❌ Command Failed")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        print(f"  Status: {result.get('status', 'failed')}")

if __name__ == "__main__":
    asyncio.run(main())