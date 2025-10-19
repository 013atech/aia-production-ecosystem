#!/usr/bin/env python3
"""
AIA Enhanced CLI with Claude Code Agent Integration
==================================================

Enhanced AIA CLI that integrates seamlessly with Claude Code agent system
providing full admin access and cryptography agent leadership.

Features:
- Direct integration with Claude Code Integration Service (port 8025)
- Cryptography agent team leadership
- Atomic-DKG enhanced processing (14,384+ atoms)
- Local development admin authentication
- Real-time multi-agent coordination
- Enterprise-grade security and compliance
"""

import os
import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import getpass
import argparse

# Import the CLI bridge
from aia_cli_claude_code_bridge import AIACliBridge

# Setup logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise for CLI
logger = logging.getLogger(__name__)

class EnhancedAIACLI:
    """
    Enhanced AIA CLI with Claude Code integration and admin access
    """

    def __init__(self):
        self.bridge: Optional[AIACliBridge] = None
        self.authenticated = False

    async def initialize(self):
        """Initialize CLI with authentication"""
        print("🔧 Initializing AIA Enhanced CLI...")

        self.bridge = AIACliBridge()
        await self.bridge.initialize()
        self.authenticated = True

        print("✅ AIA Enhanced CLI ready with admin access")

    async def run_command(self, command: str, args: argparse.Namespace = None) -> Dict[str, Any]:
        """Run a command through the agent system"""

        if not self.authenticated:
            print("❌ Authentication required")
            return {"error": "Not authenticated"}

        context = {
            "cli_args": vars(args) if args else {},
            "working_directory": os.getcwd(),
            "timestamp": datetime.now().isoformat()
        }

        print(f"🤖 Processing: {command}")
        print("🔐 Cryptography agent leading coordination...")

        result = await self.bridge.execute_command(command, context)

        if result.get("success"):
            print("✅ Task completed successfully")
            return result
        else:
            print("❌ Task failed")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return result

    async def show_status(self):
        """Show system status"""
        print("📊 AIA System Status Check...")

        status = await self.bridge.get_system_status()

        print(f"\n🎯 CLI Status: {status.get('cli_bridge_status', 'unknown')}")
        print(f"🔐 Admin Access: {'✅' if status.get('admin_access') else '❌'}")
        print(f"🤖 Available Agents: {status.get('available_agents', 0)}")
        print(f"🧠 Atomic-DKG: {'✅' if status.get('atomic_dkg_enabled') else '❌'}")

        user_profile = status.get('user_profile', {})
        if user_profile:
            print(f"👤 User: {user_profile.get('username', 'unknown')}@{user_profile.get('machine_id', 'unknown')}")
            print(f"🏆 Tier: {user_profile.get('tier', 'unknown')}")

        # Show service health
        claude_service = status.get('claude_service', {})
        if claude_service.get('service_status') == 'healthy':
            components = claude_service.get('components', {})
            agent_registry = components.get('agent_registry', {})
            atomic_dkg = components.get('atomic_dkg', {})

            print(f"\n🔧 Service Components:")
            print(f"  Agent Registry: {agent_registry.get('total_agents', 0)} total, {agent_registry.get('active_agents', 0)} active")
            print(f"  Atomic-DKG: {atomic_dkg.get('total_atoms', 0):,} atoms, {atomic_dkg.get('total_checkpoints', 0)} checkpoints")

    async def list_agents(self, capability: str = None):
        """List available agents"""
        print("🤖 Available Claude Agents:")

        agents = await self.bridge.list_available_agents(capability)
        total = agents.get('total_agents', 0)

        if capability:
            print(f"  Filtered by capability: {capability}")

        print(f"  Total: {total} agents")

        for agent in agents.get('agents', [])[:15]:  # Show first 15
            name = agent.get('name', 'Unknown')
            capabilities = agent.get('capabilities', [])
            status = agent.get('status', 'unknown')

            status_emoji = "✅" if status == "active" else "⏸️" if status == "registered" else "❌"
            print(f"  {status_emoji} {name} ({len(capabilities)} capabilities)")

    async def cleanup(self):
        """Cleanup resources"""
        if self.bridge:
            await self.bridge.cleanup()

def create_argument_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="AIA Enhanced CLI with Claude Code Agent Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aia "create a secure authentication system"
  aia "analyze the codebase for performance issues"
  aia "deploy to production with monitoring"
  aia status
  aia agents
        """
    )

    parser.add_argument('command', nargs='*', help='Command to execute')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--agents', action='store_true', help='List available agents')
    parser.add_argument('--tasks', action='store_true', help='Show active tasks')
    parser.add_argument('--capability', type=str, help='Filter agents by capability')
    parser.add_argument('--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    return parser

async def main():
    """Main CLI entry point"""
    parser = create_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    cli = EnhancedAIACLI()

    try:
        await cli.initialize()

        if args.status:
            await cli.show_status()
        elif args.agents:
            await cli.list_agents(args.capability)
        elif args.tasks:
            tasks = await cli.bridge.get_active_tasks()
            print(f"⚡ Active Tasks: {len(tasks.get('active_tasks', {}))}")
        elif args.interactive or not args.command:
            await interactive_mode(cli.bridge)
        else:
            command = " ".join(args.command)
            await cli.run_command(command, args)

    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"❌ CLI Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
    finally:
        await cli.cleanup()

if __name__ == "__main__":
    asyncio.run(main())