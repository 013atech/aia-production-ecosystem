# Phase 2: Economic Governor & Dual-Token System Implementation Guide

## Overview
This guide details the implementation of the dual-token economic system with VWT (Value-Weighted Token) and CVT (Corporate Value Token) during weeks 5-8.

## Week 5-6: Dual-Token System Implementation

### 1. Token Contracts Definition

```python
# File: aia_system/economic/tokens/vwt_token.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json

class VWTToken:
    """
    Value-Weighted Token (VWT) - Utility token for platform services
    """
    
    def __init__(self):
        self.name = "Value-Weighted Token"
        self.symbol = "VWT"
        self.decimals = 18
        self.total_supply = Decimal("1000000000")  # 1 billion tokens
        self.circulating_supply = Decimal("0")
        
        # Token economics parameters
        self.inflation_rate = Decimal("0.02")  # 2% annual
        self.burn_rate = Decimal("0.001")  # 0.1% per transaction
        self.staking_reward_rate = Decimal("0.05")  # 5% APY
        
        # Balances and allowances
        self.balances: Dict[str, Decimal] = {}
        self.allowances: Dict[str, Dict[str, Decimal]] = {}
        self.staked_balances: Dict[str, Dict] = {}
        
        # Transaction history
        self.transactions: List[Dict] = []
        
        # Token velocity tracking
        self.velocity_window = timedelta(days=30)
        self.velocity_history: List[Dict] = []
    
    def mint(self, address: str, amount: Decimal) -> bool:
        """
        Mint new tokens (only for system rewards)
        """
        if amount <= 0:
            return False
        
        if self.circulating_supply + amount > self.total_supply:
            return False
        
        if address not in self.balances:
            self.balances[address] = Decimal("0")
        
        self.balances[address] += amount
        self.circulating_supply += amount
        
        self._record_transaction({
            "type": "mint",
            "to": address,
            "amount": str(amount),
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def transfer(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal
    ) -> bool:
        """
        Transfer tokens between addresses
        """
        if amount <= 0:
            return False
        
        if from_address not in self.balances:
            return False
        
        # Calculate burn amount
        burn_amount = amount * self.burn_rate
        transfer_amount = amount - burn_amount
        
        if self.balances[from_address] < amount:
            return False
        
        # Execute transfer
        self.balances[from_address] -= amount
        
        if to_address not in self.balances:
            self.balances[to_address] = Decimal("0")
        
        self.balances[to_address] += transfer_amount
        
        # Burn tokens
        self.circulating_supply -= burn_amount
        
        self._record_transaction({
            "type": "transfer",
            "from": from_address,
            "to": to_address,
            "amount": str(amount),
            "burn": str(burn_amount),
            "timestamp": datetime.now().isoformat()
        })
        
        # Update velocity
        self._update_velocity(amount)
        
        return True
    
    def stake(
        self,
        address: str,
        amount: Decimal,
        lock_period_days: int = 30
    ) -> bool:
        """
        Stake tokens for rewards
        """
        if amount <= 0:
            return False
        
        if address not in self.balances:
            return False
        
        if self.balances[address] < amount:
            return False
        
        # Lock tokens
        self.balances[address] -= amount
        
        stake_id = self._generate_stake_id(address, amount)
        
        if address not in self.staked_balances:
            self.staked_balances[address] = {}
        
        self.staked_balances[address][stake_id] = {
            "amount": amount,
            "start_time": datetime.now(),
            "lock_until": datetime.now() + timedelta(days=lock_period_days),
            "reward_rate": self.staking_reward_rate,
            "rewards_claimed": Decimal("0")
        }
        
        return True
    
    def calculate_stake_rewards(self, address: str) -> Decimal:
        """
        Calculate accumulated staking rewards
        """
        if address not in self.staked_balances:
            return Decimal("0")
        
        total_rewards = Decimal("0")
        
        for stake_id, stake_info in self.staked_balances[address].items():
            duration = datetime.now() - stake_info["start_time"]
            days_staked = duration.days
            
            # Calculate compound interest
            rewards = stake_info["amount"] * (
                (1 + stake_info["reward_rate"] / 365) ** days_staked - 1
            )
            
            # Subtract already claimed rewards
            unclaimed_rewards = rewards - stake_info["rewards_claimed"]
            total_rewards += max(unclaimed_rewards, Decimal("0"))
        
        return total_rewards
    
    def get_token_velocity(self) -> Decimal:
        """
        Calculate token velocity (transactions per month)
        """
        if not self.velocity_history:
            return Decimal("0")
        
        recent_transactions = [
            v for v in self.velocity_history
            if datetime.fromisoformat(v["timestamp"]) > 
            datetime.now() - self.velocity_window
        ]
        
        if not recent_transactions:
            return Decimal("0")
        
        total_volume = sum(Decimal(v["amount"]) for v in recent_transactions)
        avg_supply = self.circulating_supply
        
        if avg_supply == 0:
            return Decimal("0")
        
        # Velocity = Volume / Supply (annualized)
        monthly_velocity = (total_volume / avg_supply) * 12 / 365 * 30
        
        return monthly_velocity
    
    def _record_transaction(self, transaction: Dict):
        """Record transaction for audit trail"""
        transaction["hash"] = self._generate_tx_hash(transaction)
        self.transactions.append(transaction)
    
    def _update_velocity(self, amount: Decimal):
        """Update velocity tracking"""
        self.velocity_history.append({
            "amount": str(amount),
            "timestamp": datetime.now().isoformat()
        })
        
        # Clean old entries
        cutoff = datetime.now() - self.velocity_window
        self.velocity_history = [
            v for v in self.velocity_history
            if datetime.fromisoformat(v["timestamp"]) > cutoff
        ]
    
    def _generate_stake_id(self, address: str, amount: Decimal) -> str:
        """Generate unique stake ID"""
        data = f"{address}{amount}{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_tx_hash(self, transaction: Dict) -> str:
        """Generate transaction hash"""
        data = json.dumps(transaction, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
```

```python
# File: aia_system/economic/tokens/cvt_token.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

class CVTToken:
    """
    Corporate Value Token (CVT) - Governance token
    """
    
    def __init__(self):
        self.name = "Corporate Value Token"
        self.symbol = "CVT"
        self.decimals = 18
        self.total_supply = Decimal("100000000")  # 100 million tokens
        self.circulating_supply = Decimal("0")
        
        # Governance parameters
        self.min_proposal_stake = Decimal("1000")  # Min CVT to create proposal
        self.quorum_percentage = Decimal("0.1")  # 10% quorum
        self.voting_period_days = 7
        
        # Token distribution
        self.balances: Dict[str, Decimal] = {}
        self.locked_balances: Dict[str, Decimal] = {}  # For vesting
        self.delegated_balances: Dict[str, str] = {}  # Delegation for voting
        
        # Governance tracking
        self.proposals: Dict[str, Dict] = {}
        self.votes: Dict[str, Dict[str, Dict]] = {}
        
        # Conviction voting parameters
        self.conviction_growth_rate = Decimal("0.1")  # 10% per day
        self.max_conviction_multiplier = Decimal("3.0")
    
    def mint_governance_tokens(
        self,
        address: str,
        amount: Decimal,
        vesting_months: int = 0
    ) -> bool:
        """
        Mint governance tokens with optional vesting
        """
        if amount <= 0:
            return False
        
        if self.circulating_supply + amount > self.total_supply:
            return False
        
        if vesting_months > 0:
            # Add to locked balance with vesting schedule
            if address not in self.locked_balances:
                self.locked_balances[address] = Decimal("0")
            
            self.locked_balances[address] += amount
            
            # Create vesting schedule
            self._create_vesting_schedule(address, amount, vesting_months)
        else:
            # Add to regular balance
            if address not in self.balances:
                self.balances[address] = Decimal("0")
            
            self.balances[address] += amount
        
        self.circulating_supply += amount
        return True
    
    def create_proposal(
        self,
        proposer: str,
        proposal_id: str,
        title: str,
        description: str,
        execution_data: Optional[Dict] = None
    ) -> bool:
        """
        Create governance proposal
        """
        if proposer not in self.balances:
            return False
        
        if self.balances[proposer] < self.min_proposal_stake:
            return False
        
        self.proposals[proposal_id] = {
            "proposer": proposer,
            "title": title,
            "description": description,
            "execution_data": execution_data,
            "created_at": datetime.now(),
            "voting_ends": datetime.now() + timedelta(days=self.voting_period_days),
            "status": "active",
            "votes_for": Decimal("0"),
            "votes_against": Decimal("0"),
            "conviction_scores": {}
        }
        
        # Lock proposer's stake
        stake_amount = self.min_proposal_stake
        self.balances[proposer] -= stake_amount
        
        if proposer not in self.locked_balances:
            self.locked_balances[proposer] = Decimal("0")
        
        self.locked_balances[proposer] += stake_amount
        
        return True
    
    def vote_with_conviction(
        self,
        voter: str,
        proposal_id: str,
        support: bool,
        lock_periods: int = 1  # 1-6, higher = more conviction
    ) -> bool:
        """
        Vote with conviction (time-locked voting power)
        """
        if proposal_id not in self.proposals:
            return False
        
        if voter not in self.balances:
            return False
        
        proposal = self.proposals[proposal_id]
        
        if datetime.now() > proposal["voting_ends"]:
            return False
        
        # Calculate voting power with conviction
        base_votes = self.balances[voter]
        conviction_multiplier = self._calculate_conviction_multiplier(lock_periods)
        voting_power = base_votes * conviction_multiplier
        
        # Record vote
        if proposal_id not in self.votes:
            self.votes[proposal_id] = {}
        
        self.votes[proposal_id][voter] = {
            "support": support,
            "voting_power": voting_power,
            "lock_periods": lock_periods,
            "timestamp": datetime.now()
        }
        
        # Update proposal vote counts
        if support:
            proposal["votes_for"] += voting_power
        else:
            proposal["votes_against"] += voting_power
        
        # Lock tokens based on conviction
        lock_amount = base_votes
        lock_duration = lock_periods * self.voting_period_days
        
        self.balances[voter] -= lock_amount
        self._add_time_lock(voter, lock_amount, lock_duration)
        
        return True
    
    def delegate_voting_power(
        self,
        delegator: str,
        delegate: str
    ) -> bool:
        """
        Delegate voting power to another address
        """
        if delegator not in self.balances:
            return False
        
        self.delegated_balances[delegator] = delegate
        return True
    
    def calculate_voting_power(self, address: str) -> Decimal:
        """
        Calculate total voting power including delegations
        """
        if address not in self.balances:
            return Decimal("0")
        
        # Own balance
        voting_power = self.balances[address]
        
        # Add delegated balances
        for delegator, delegate in self.delegated_balances.items():
            if delegate == address and delegator != address:
                voting_power += self.balances.get(delegator, Decimal("0"))
        
        return voting_power
    
    def execute_proposal(self, proposal_id: str) -> bool:
        """
        Execute passed proposal
        """
        if proposal_id not in self.proposals:
            return False
        
        proposal = self.proposals[proposal_id]
        
        # Check if voting period ended
        if datetime.now() < proposal["voting_ends"]:
            return False
        
        # Check if proposal passed
        total_votes = proposal["votes_for"] + proposal["votes_against"]
        quorum_met = total_votes >= self.circulating_supply * self.quorum_percentage
        
        if not quorum_met:
            proposal["status"] = "failed_quorum"
            return False
        
        if proposal["votes_for"] <= proposal["votes_against"]:
            proposal["status"] = "rejected"
            return False
        
        # Execute proposal
        proposal["status"] = "executed"
        
        # Return proposer's stake
        proposer = proposal["proposer"]
        if proposer in self.locked_balances:
            unlock_amount = min(self.min_proposal_stake, self.locked_balances[proposer])
            self.locked_balances[proposer] -= unlock_amount
            self.balances[proposer] = self.balances.get(proposer, Decimal("0")) + unlock_amount
        
        return True
    
    def _calculate_conviction_multiplier(self, lock_periods: int) -> Decimal:
        """
        Calculate conviction multiplier based on lock periods
        """
        # Conviction = 1 + (lock_periods - 1) * growth_rate
        # Max multiplier capped at max_conviction_multiplier
        
        if lock_periods < 1:
            lock_periods = 1
        if lock_periods > 6:
            lock_periods = 6
        
        multiplier = Decimal("1") + (lock_periods - 1) * self.conviction_growth_rate
        
        return min(multiplier, self.max_conviction_multiplier)
    
    def _create_vesting_schedule(
        self,
        address: str,
        amount: Decimal,
        vesting_months: int
    ):
        """
        Create vesting schedule for locked tokens
        """
        # Implementation for vesting schedule
        # This would typically involve creating a schedule
        # that releases tokens gradually over time
        pass
    
    def _add_time_lock(
        self,
        address: str,
        amount: Decimal,
        lock_days: int
    ):
        """
        Add time lock for tokens
        """
        if address not in self.locked_balances:
            self.locked_balances[address] = Decimal("0")
        
        self.locked_balances[address] += amount
        
        # In production, would track unlock time
        # For now, simplified implementation
```

### 2. Economic Governor Implementation

```python
# File: aia_system/economic/enhanced_economic_governor.py
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import numpy as np

from .tokens.vwt_token import VWTToken
from .tokens.cvt_token import CVTToken
from .bonding_curve import BondingCurve
from .treasury_manager import TreasuryManager

class EnhancedEconomicGovernor:
    """
    Central economic governance system with dual-token mechanics
    """
    
    def __init__(self):
        # Initialize tokens
        self.vwt = VWTToken()
        self.cvt = CVTToken()
        
        # Economic components
        self.bonding_curve = BondingCurve()
        self.treasury = TreasuryManager()
        
        # Economic parameters
        self.agent_reward_pool = Decimal("10000000")  # 10M VWT for agent rewards
        self.governance_reward_pool = Decimal("1000000")  # 1M CVT for governance
        
        # Performance metrics
        self.agent_performance_history: Dict[str, List[Dict]] = {}
        self.corporate_metrics: Dict = {
            "revenue": Decimal("0"),
            "users": 0,
            "analyses_completed": 0,
            "platform_efficiency": Decimal("1.0")
        }
        
        # Reward calculation parameters
        self.performance_weights = {
            "accuracy": 0.3,
            "speed": 0.2,
            "consensus_quality": 0.25,
            "innovation": 0.15,
            "collaboration": 0.1
        }
        
        # Corporate linkage parameters
        self.corporate_contribution_threshold = Decimal("0.7")
        self.corporate_bonus_multiplier = Decimal("1.5")
    
    async def initialize_economy(self):
        """
        Initialize the economic system
        """
        # Mint initial token supply
        treasury_address = "treasury"
        
        # Mint VWT for operations
        self.vwt.mint(treasury_address, self.agent_reward_pool)
        
        # Mint CVT for governance
        self.cvt.mint_governance_tokens(
            treasury_address,
            self.governance_reward_pool,
            vesting_months=0
        )
        
        # Initialize treasury
        await self.treasury.initialize(
            vwt_balance=self.agent_reward_pool,
            cvt_balance=self.governance_reward_pool
        )
        
        print("✅ Economic system initialized")
        print(f"  VWT Supply: {self.vwt.circulating_supply}")
        print(f"  CVT Supply: {self.cvt.circulating_supply}")
    
    async def calculate_agent_rewards(
        self,
        agent_id: str,
        performance_metrics: Dict[str, float]
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate VWT and CVT rewards for agent performance
        """
        
        # Calculate base performance score
        performance_score = Decimal("0")
        
        for metric, value in performance_metrics.items():
            if metric in self.performance_weights:
                weight = Decimal(str(self.performance_weights[metric]))
                performance_score += Decimal(str(value)) * weight
        
        # Calculate VWT reward (utility token)
        base_vwt_reward = self._calculate_base_vwt_reward(performance_score)
        
        # Calculate CVT reward (governance token)
        cvt_reward = self._calculate_cvt_reward(agent_id, performance_score)
        
        # Apply corporate performance multiplier
        corporate_multiplier = self._get_corporate_multiplier()
        vwt_reward = base_vwt_reward * corporate_multiplier
        
        # Record performance
        self._record_agent_performance(
            agent_id,
            performance_metrics,
            vwt_reward,
            cvt_reward
        )
        
        return vwt_reward, cvt_reward
    
    async def distribute_rewards(
        self,
        agent_id: str,
        vwt_amount: Decimal,
        cvt_amount: Decimal
    ) -> bool:
        """
        Distribute token rewards to agent
        """
        
        # Check treasury balance
        treasury_address = "treasury"
        
        if self.vwt.balances.get(treasury_address, Decimal("0")) < vwt_amount:
            print(f"⚠️ Insufficient VWT in treasury for reward")
            return False
        
        if self.cvt.balances.get(treasury_address, Decimal("0")) < cvt_amount:
            print(f"⚠️ Insufficient CVT in treasury for reward")
            return False
        
        # Transfer VWT
        if vwt_amount > 0:
            self.vwt.transfer(treasury_address, agent_id, vwt_amount)
        
        # Transfer CVT with vesting
        if cvt_amount > 0:
            # 50% immediate, 50% vested over 6 months
            immediate_cvt = cvt_amount / 2
            vested_cvt = cvt_amount - immediate_cvt
            
            self.cvt.transfer(treasury_address, agent_id, immediate_cvt)
            self.cvt.mint_governance_tokens(agent_id, vested_cvt, vesting_months=6)
        
        # Update treasury
        await self.treasury.record_distribution(
            agent_id,
            vwt_amount,
            cvt_amount
        )
        
        return True
    
    async def apply_corporate_performance_bonus(
        self,
        agent_name: str,
        bonus_amount: Decimal,
        corporate_metrics: Dict,
        contribution_details: Dict
    ) -> bool:
        """
        Apply corporate performance bonus to agent
        """
        
        # Validate contribution threshold
        contribution_score = contribution_details.get("total_score", Decimal("0"))
        
        if contribution_score < self.corporate_contribution_threshold:
            return False
        
        # Calculate bonus based on corporate metrics
        revenue_growth = corporate_metrics.get("revenue_growth", Decimal("0"))
        user_growth = corporate_metrics.get("user_growth", Decimal("0"))
        
        bonus_multiplier = Decimal("1") + (
            revenue_growth * Decimal("0.5") +
            user_growth * Decimal("0.3")
        )
        
        final_bonus = bonus_amount * bonus_multiplier
        
        # Distribute bonus
        treasury_address = "treasury"
        success = self.vwt.transfer(treasury_address, agent_name, final_bonus)
        
        if success:
            # Record corporate linkage
            self._record_corporate_linkage(
                agent_name,
                contribution_details,
                final_bonus
            )
        
        return success
    
    async def create_governance_proposal(
        self,
        proposer: str,
        proposal_type: str,
        proposal_data: Dict
    ) -> str:
        """
        Create governance proposal using CVT
        """
        
        proposal_id = f"prop_{datetime.now().timestamp()}"
        
        # Validate proposer has enough CVT
        if self.cvt.balances.get(proposer, Decimal("0")) < self.cvt.min_proposal_stake:
            raise ValueError(f"Insufficient CVT balance. Need {self.cvt.min_proposal_stake}")
        
        # Create proposal based on type
        if proposal_type == "parameter_change":
            title = f"Change {proposal_data['parameter']} to {proposal_data['new_value']}"
            description = proposal_data.get("rationale", "")
        elif proposal_type == "treasury_allocation":
            title = f"Allocate {proposal_data['amount']} tokens to {proposal_data['recipient']}"
            description = proposal_data.get("purpose", "")
        else:
            title = proposal_data.get("title", "Generic Proposal")
            description = proposal_data.get("description", "")
        
        # Create the proposal
        success = self.cvt.create_proposal(
            proposer,
            proposal_id,
            title,
            description,
            proposal_data
        )
        
        if success:
            print(f"✅ Proposal {proposal_id} created")
            return proposal_id
        else:
            raise Exception("Failed to create proposal")
    
    async def vote_on_proposal(
        self,
        voter: str,
        proposal_id: str,
        support: bool,
        conviction_level: int = 1
    ) -> bool:
        """
        Vote on governance proposal with conviction
        """
        
        success = self.cvt.vote_with_conviction(
            voter,
            proposal_id,
            support,
            conviction_level
        )
        
        if success:
            print(f"✅ Vote recorded for {proposal_id}")
            
            # Check if proposal can be executed
            proposal = self.cvt.proposals[proposal_id]
            if datetime.now() > proposal["voting_ends"]:
                await self.execute_proposal(proposal_id)
        
        return success
    
    async def execute_proposal(self, proposal_id: str) -> bool:
        """
        Execute a passed governance proposal
        """
        
        if not self.cvt.execute_proposal(proposal_id):
            return False
        
        proposal = self.cvt.proposals[proposal_id]
        execution_data = proposal.get("execution_data", {})
        
        # Execute based on proposal type
        if execution_data.get("type") == "parameter_change":
            await self._execute_parameter_change(execution_data)
        elif execution_data.get("type") == "treasury_allocation":
            await self._execute_treasury_allocation(execution_data)
        
        print(f"✅ Proposal {proposal_id} executed")
        return True
    
    async def optimize_incentive_mechanisms(
        self,
        performance_data: Dict,
        user_behavior_data: Dict
    ) -> Dict:
        """
        Optimize economic incentives based on data
        """
        
        optimizations = {}
        
        # Analyze token velocity
        vwt_velocity = self.vwt.get_token_velocity()
        target_velocity = Decimal("2.5")
        
        if vwt_velocity < target_velocity * Decimal("0.8"):
            # Velocity too low - increase rewards
            optimizations["vwt_reward_increase"] = Decimal("1.1")
        elif vwt_velocity > target_velocity * Decimal("1.2"):
            # Velocity too high - decrease rewards slightly
            optimizations["vwt_reward_decrease"] = Decimal("0.95")
        
        # Analyze governance participation
        total_cvt = self.cvt.circulating_supply
        voting_cvt = sum(
            self.cvt.calculate_voting_power(addr)
            for addr in self.cvt.balances.keys()
        )
        
        participation_rate = voting_cvt / total_cvt if total_cvt > 0 else Decimal("0")
        
        if participation_rate < Decimal("0.3"):
            # Low participation - increase governance rewards
            optimizations["governance_reward_boost"] = Decimal("1.5")
        
        # Analyze agent performance distribution
        performance_scores = [
            p["performance_score"]
            for agent_history in self.agent_performance_history.values()
            for p in agent_history[-10:]  # Last 10 entries
        ]
        
        if performance_scores:
            avg_performance = sum(performance_scores) / len(performance_scores)
            std_performance = np.std([float(p) for p in performance_scores])
            
            if std_performance > 0.3:
                # High variance - adjust weights to reduce inequality
                optimizations["performance_weight_adjustment"] = {
                    "collaboration": 0.15,  # Increase collaboration weight
                    "innovation": 0.1  # Decrease innovation weight
                }
        
        return optimizations
    
    def _calculate_base_vwt_reward(self, performance_score: Decimal) -> Decimal:
        """
        Calculate base VWT reward from performance score
        """
        
        # Base reward calculation
        # Score 0-1 maps to 0-1000 VWT
        max_reward = Decimal("1000")
        base_reward = performance_score * max_reward
        
        # Apply logarithmic scaling for fairness
        if base_reward > 0:
            scaled_reward = Decimal(str(np.log1p(float(base_reward)))) * Decimal("100")
            return min(scaled_reward, max_reward)
        
        return Decimal("0")
    
    def _calculate_cvt_reward(
        self,
        agent_id: str,
        performance_score: Decimal
    ) -> Decimal:
        """
        Calculate CVT governance token reward
        """
        
        # CVT is awarded for exceptional performance only
        if performance_score < Decimal("0.8"):
            return Decimal("0")
        
        # Check historical performance for consistency
        if agent_id in self.agent_performance_history:
            recent_scores = [
                p["performance_score"]
                for p in self.agent_performance_history[agent_id][-5:]
            ]
            
            if len(recent_scores) >= 5:
                avg_score = sum(recent_scores) / len(recent_scores)
                
                if avg_score >= Decimal("0.75"):
                    # Consistent high performer - award CVT
                    cvt_reward = (performance_score - Decimal("0.75")) * Decimal("100")
                    return min(cvt_reward, Decimal("50"))  # Cap at 50 CVT
        
        return Decimal("0")
    
    def _get_corporate_multiplier(self) -> Decimal:
        """
        Get corporate performance multiplier
        """
        
        # Calculate based on platform metrics
        revenue_target = Decimal("150000")  # Monthly target
        current_revenue = self.corporate_metrics["revenue"]
        
        if current_revenue >= revenue_target:
            return self.corporate_bonus_multiplier
        elif current_revenue >= revenue_target * Decimal("0.8"):
            return Decimal("1.2")
        elif current_revenue >= revenue_target * Decimal("0.6"):
            return Decimal("1.0")
        else:
            return Decimal("0.8")
    
    def _record_agent_performance(
        self,
        agent_id: str,
        metrics: Dict,
        vwt_reward: Decimal,
        cvt_reward: Decimal
    ):
        """
        Record agent performance for history
        """
        
        if agent_id not in self.agent_performance_history:
            self.agent_performance_history[agent_id] = []
        
        performance_record = {
            "timestamp": datetime.now(),
            "metrics": metrics,
            "vwt_reward": vwt_reward,
            "cvt_reward": cvt_reward,
            "performance_score": sum(
                Decimal(str(metrics.get(m, 0))) * Decimal(str(w))
                for m, w in self.performance_weights.items()
            )
        }
        
        self.agent_performance_history[agent_id].append(performance_record)
        
        # Keep only last 100 records
        if len(self.agent_performance_history[agent_id]) > 100:
            self.agent_performance_history[agent_id] = \
                self.agent_performance_history[agent_id][-100:]
    
    def _record_corporate_linkage(
        self,
        agent_name: str,
        contribution_details: Dict,
        bonus_amount: Decimal
    ):
        """
        Record corporate-agent performance linkage
        """
        
        # This would typically be stored in a database
        # For now, we'll just log it
        linkage_record = {
            "agent": agent_name,
            "contribution": contribution_details,
            "bonus": bonus_amount,
            "timestamp": datetime.now(),
            "corporate_metrics": self.corporate_metrics.copy()
        }
        
        print(f"📊 Corporate linkage recorded: {linkage_record}")
    
    async def _execute_parameter_change(self, execution_data: Dict):
        """
        Execute parameter change from governance
        """
        
        parameter = execution_data["parameter"]
        new_value = execution_data["new_value"]
        
        # Update the specified parameter
        if parameter == "agent_reward_pool":
            self.agent_reward_pool = Decimal(str(new_value))
        elif parameter == "performance_weights":
            self.performance_weights.update(new_value)
        # Add more parameters as needed
    
    async def _execute_treasury_allocation(self, execution_data: Dict):
        """
        Execute treasury allocation from governance
        """
        
        amount = Decimal(str(execution_data["amount"]))
        recipient = execution_data["recipient"]
        token_type = execution_data.get("token_type", "VWT")
        
        treasury_address = "treasury"
        
        if token_type == "VWT":
            self.vwt.transfer(treasury_address, recipient, amount)
        elif token_type == "CVT":
            self.cvt.transfer(treasury_address, recipient, amount)
```

### 3. Bonding Curve Implementation

```python
# File: aia_system/economic/bonding_curve.py
from decimal import Decimal
import math

class BondingCurve:
    """
    Bonding curve for token pricing and liquidity
    """
    
    def __init__(self):
        # Curve parameters
        self.reserve_ratio = Decimal("0.5")  # 50% reserve ratio
        self.initial_price = Decimal("0.01")  # Initial token price
        self.curve_steepness = Decimal("0.001")
        
        # Reserves
        self.token_supply = Decimal("0")
        self.reserve_balance = Decimal("0")
    
    def calculate_purchase_price(
        self,
        tokens_to_buy: Decimal
    ) -> Decimal:
        """
        Calculate price for purchasing tokens
        """
        
        if tokens_to_buy <= 0:
            return Decimal("0")
        
        # Price = initial_price * (1 + curve_steepness * supply) ^ (1/reserve_ratio)
        current_price = self._get_current_price()
        
        # Calculate average price for the purchase
        end_supply = self.token_supply + tokens_to_buy
        end_price = self._calculate_price_at_supply(end_supply)
        
        # Integral of the bonding curve
        total_cost = (current_price + end_price) / 2 * tokens_to_buy
        
        return total_cost
    
    def calculate_sale_return(
        self,
        tokens_to_sell: Decimal
    ) -> Decimal:
        """
        Calculate return for selling tokens
        """
        
        if tokens_to_sell <= 0 or tokens_to_sell > self.token_supply:
            return Decimal("0")
        
        # Calculate return based on bonding curve
        current_price = self._get_current_price()
        
        end_supply = self.token_supply - tokens_to_sell
        end_price = self._calculate_price_at_supply(end_supply)
        
        # Return with slippage
        sale_return = (current_price + end_price) / 2 * tokens_to_sell
        
        # Apply exit fee (2%)
        exit_fee = sale_return * Decimal("0.02")
        
        return sale_return - exit_fee
    
    def buy_tokens(
        self,
        payment_amount: Decimal
    ) -> Decimal:
        """
        Buy tokens with payment
        """
        
        # Calculate tokens received
        tokens_received = self._calculate_tokens_from_payment(payment_amount)
        
        # Update state
        self.token_supply += tokens_received
        self.reserve_balance += payment_amount
        
        return tokens_received
    
    def sell_tokens(
        self,
        token_amount: Decimal
    ) -> Decimal:
        """
        Sell tokens for reserve currency
        """
        
        if token_amount > self.token_supply:
            return Decimal("0")
        
        # Calculate return
        sale_return = self.calculate_sale_return(token_amount)
        
        if sale_return > self.reserve_balance:
            return Decimal("0")
        
        # Update state
        self.token_supply -= token_amount
        self.reserve_balance -= sale_return
        
        return sale_return
    
    def _get_current_price(self) -> Decimal:
        """
        Get current token price
        """
        return self._calculate_price_at_supply(self.token_supply)
    
    def _calculate_price_at_supply(self, supply: Decimal) -> Decimal:
        """
        Calculate price at specific supply level
        """
        
        if supply == 0:
            return self.initial_price
        
        # Exponential bonding curve
        price = self.initial_price * (
            Decimal("1") + self.curve_steepness * supply
        ) ** (Decimal("1") / self.reserve_ratio)
        
        return price
    
    def _calculate_tokens_from_payment(
        self,
        payment: Decimal
    ) -> Decimal:
        """
        Calculate tokens received for payment
        """
        
        # Numerical approximation for tokens
        # In production, use more sophisticated calculation
        
        estimated_tokens = payment / self._get_current_price()
        
        # Refine estimate
        for _ in range(5):
            cost = self.calculate_purchase_price(estimated_tokens)
            
            if abs(cost - payment) < Decimal("0.01"):
                break
            
            adjustment = (payment - cost) / self._get_current_price()
            estimated_tokens += adjustment / 2
        
        return estimated_tokens
```

## Week 7-8: Performance Linkage & Integration

### 4. Corporate-Agent Performance Linkage

```python
# File: aia_system/economic/performance_linkage.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

class CorporatePerformanceLinkage:
    """
    Link agent performance to corporate KPIs
    """
    
    def __init__(self, economic_governor):
        self.economic_governor = economic_governor
        
        # Corporate KPI definitions
        self.corporate_kpis = {
            "revenue": {
                "target": Decimal("150000"),  # Monthly
                "weight": 0.3,
                "unit": "EUR"
            },
            "user_satisfaction": {
                "target": Decimal("4.5"),  # Out of 5
                "weight": 0.25,
                "unit": "rating"
            },
            "analysis_quality": {
                "target": Decimal("0.9"),  # 90% accuracy
                "weight": 0.2,
                "unit": "score"
            },
            "platform_efficiency": {
                "target": Decimal("0.85"),  # 85% efficiency
                "weight": 0.15,
                "unit": "ratio"
            },
            "innovation_index": {
                "target": Decimal("0.7"),
                "weight": 0.1,
                "unit": "index"
            }
        }
        
        # Agent contribution mapping
        self.agent_contribution_map = {
            "GLAC": {
                "revenue": 0.3,
                "analysis_quality": 0.4,
                "innovation_index": 0.2
            },
            "TSGLA": {
                "revenue": 0.25,
                "analysis_quality": 0.35,
                "platform_efficiency": 0.3
            },
            "TASA-NS-Alg": {
                "user_satisfaction": 0.4,
                "analysis_quality": 0.3,
                "innovation_index": 0.3
            }
        }
    
    async def calculate_corporate_contribution(
        self,
        agent_performance: Dict,
        corporate_metrics: Dict,
        agent_type: str
    ) -> Dict:
        """
        Calculate agent's contribution to corporate metrics
        """
        
        contribution_score = Decimal("0")
        contribution_details = {}
        
        # Get agent's contribution weights
        agent_weights = self.agent_contribution_map.get(agent_type, {})
        
        for kpi_name, kpi_config in self.corporate_kpis.items():
            if kpi_name not in corporate_metrics:
                continue
            
            # Calculate KPI achievement
            current_value = Decimal(str(corporate_metrics[kpi_name]))
            target_value = kpi_config["target"]
            achievement_rate = min(current_value / target_value, Decimal("1"))
            
            # Calculate agent's contribution to this KPI
            agent_contribution_weight = Decimal(str(
                agent_weights.get(kpi_name, 0)
            ))
            
            if agent_contribution_weight > 0:
                # Factor in agent's performance
                performance_factor = Decimal(str(
                    agent_performance.get("overall_score", 0)
                ))
                
                contribution = (
                    achievement_rate * 
                    agent_contribution_weight * 
                    performance_factor *
                    Decimal(str(kpi_config["weight"]))
                )
                
                contribution_score += contribution
                
                contribution_details[kpi_name] = {
                    "achievement_rate": float(achievement_rate),
                    "agent_contribution": float(agent_contribution_weight),
                    "weighted_contribution": float(contribution)
                }
        
        # Calculate revenue impact
        revenue_impact = self._calculate_revenue_impact(
            contribution_score,
            corporate_metrics.get("revenue", 0)
        )
        
        return {
            "total_score": contribution_score,
            "details": contribution_details,
            "revenue_impact": revenue_impact,
            "bonus_eligible": contribution_score >= Decimal("0.7")
        }
    
    async def calculate_reward_adjustment(
        self,
        corporate_contribution: Dict
    ) -> Dict:
        """
        Calculate reward adjustment based on corporate contribution
        """
        
        base_adjustment = Decimal("1.0")
        
        contribution_score = corporate_contribution["total_score"]
        
        # Tiered bonus structure
        if contribution_score >= Decimal("0.9"):
            vwt_multiplier = Decimal("2.0")  # 2x multiplier
            cvt_bonus = Decimal("100")  # 100 CVT bonus
        elif contribution_score >= Decimal("0.8"):
            vwt_multiplier = Decimal("1.5")
            cvt_bonus = Decimal("50")
        elif contribution_score >= Decimal("0.7"):
            vwt_multiplier = Decimal("1.2")
            cvt_bonus = Decimal("20")
        else:
            vwt_multiplier = base_adjustment
            cvt_bonus = Decimal("0")
        
        return {
            "vwt_multiplier": vwt_multiplier,
            "cvt_bonus": cvt_bonus,
            "bonus_vwt": corporate_contribution["revenue_impact"] * Decimal("0.1")
        }
    
    async def calculate_performance_correlation(
        self,
        agent_performance: Dict,
        corporate_metrics: Dict
    ) -> float:
        """
        Calculate correlation between agent and corporate performance
        """
        
        # Extract time series data
        agent_scores = agent_performance.get("historical_scores", [])
        corporate_scores = corporate_metrics.get("historical_performance", [])
        
        if len(agent_scores) < 10 or len(corporate_scores) < 10:
            return 0.0
        
        # Calculate Pearson correlation
        correlation = np.corrcoef(
            agent_scores[-30:],  # Last 30 data points
            corporate_scores[-30:]
        )[0, 1]
        
        return float(correlation) if not np.isnan(correlation) else 0.0
    
    def _calculate_revenue_impact(
        self,
        contribution_score: Decimal,
        current_revenue: Decimal
    ) -> Decimal:
        """
        Calculate agent's impact on revenue
        """
        
        # Simplified model: contribution score * revenue * impact factor
        impact_factor = Decimal("0.05")  # 5% impact factor
        
        revenue_impact = contribution_score * current_revenue * impact_factor
        
        return revenue_impact
```

### 5. Integration with Main System

```python
# File: aia_system/api/economic_integration.py
from typing import Dict, Any
from ..economic.enhanced_economic_governor import EnhancedEconomicGovernor
from ..economic.performance_linkage import CorporatePerformanceLinkage

class EconomicSystemIntegration:
    """
    Integration of economic system with main API
    """
    
    def __init__(self):
        self.economic_governor = EnhancedEconomicGovernor()
        self.performance_linkage = CorporatePerformanceLinkage(
            self.economic_governor
        )
        
    async def initialize(self):
        """
        Initialize economic system
        """
        await self.economic_governor.initialize_economy()
        print("✅ Economic system integrated with main API")
    
    async def process_agent_completion(
        self,
        agent_id: str,
        agent_type: str,
        task_result: Dict,
        performance_metrics: Dict
    ) -> Dict:
        """
        Process agent task completion and distribute rewards
        """
        
        # Calculate rewards
        vwt_reward, cvt_reward = await self.economic_governor.calculate_agent_rewards(
            agent_id,
            performance_metrics
        )
        
        # Calculate corporate contribution
        corporate_metrics = await self._get_corporate_metrics()
        
        corporate_contribution = await self.performance_linkage.calculate_corporate_contribution(
            performance_metrics,
            corporate_metrics,
            agent_type
        )
        
        # Apply corporate bonus if eligible
        if corporate_contribution["bonus_eligible"]:
            reward_adjustment = await self.performance_linkage.calculate_reward_adjustment(
                corporate_contribution
            )
            
            vwt_reward *= reward_adjustment["vwt_multiplier"]
            cvt_reward += reward_adjustment["cvt_bonus"]
            
            # Apply corporate bonus
            await self.economic_governor.apply_corporate_performance_bonus(
                agent_id,
                reward_adjustment["bonus_vwt"],
                corporate_metrics,
                corporate_contribution
            )
        
        # Distribute rewards
        success = await self.economic_governor.distribute_rewards(
            agent_id,
            vwt_reward,
            cvt_reward
        )
        
        return {
            "rewards_distributed": success,
            "vwt_earned": float(vwt_reward),
            "cvt_earned": float(cvt_reward),
            "corporate_contribution": corporate_contribution,
            "agent_balance": {
                "vwt": float(self.economic_governor.vwt.balances.get(agent_id, 0)),
                "cvt": float(self.economic_governor.cvt.balances.get(agent_id, 0))
            }
        }
    
    async def get_token_metrics(self) -> Dict:
        """
        Get current token metrics
        """
        
        vwt_metrics = {
            "total_supply": float(self.economic_governor.vwt.total_supply),
            "circulating_supply": float(self.economic_governor.vwt.circulating_supply),
            "velocity": float(self.economic_governor.vwt.get_token_velocity()),
            "staking_apy": float(self.economic_governor.vwt.staking_reward_rate * 100)
        }
        
        cvt_metrics = {
            "total_supply": float(self.economic_governor.cvt.total_supply),
            "circulating_supply": float(self.economic_governor.cvt.circulating_supply),
            "active_proposals": len([
                p for p in self.economic_governor.cvt.proposals.values()
                if p["status"] == "active"
            ]),
            "governance_participation": self._calculate_governance_participation()
        }
        
        return {
            "vwt": vwt_metrics,
            "cvt": cvt_metrics,
            "treasury_balance": {
                "vwt": float(self.economic_governor.vwt.balances.get("treasury", 0)),
                "cvt": float(self.economic_governor.cvt.balances.get("treasury", 0))
            }
        }
    
    async def _get_corporate_metrics(self) -> Dict:
        """
        Get current corporate metrics
        """
        
        # In production, these would come from analytics service
        return {
            "revenue": 125000,  # EUR
            "user_satisfaction": 4.3,
            "analysis_quality": 0.88,
            "platform_efficiency": 0.82,
            "innovation_index": 0.65,
            "revenue_growth": 0.15,  # 15% growth
            "user_growth": 0.20  # 20% growth
        }
    
    def _calculate_governance_participation(self) -> float:
        """
        Calculate governance participation rate
        """
        
        total_cvt = self.economic_governor.cvt.circulating_supply
        
        if total_cvt == 0:
            return 0.0
        
        participating_cvt = sum(
            self.economic_governor.cvt.calculate_voting_power(addr)
            for addr in self.economic_governor.cvt.balances.keys()
        )
        
        return float(participating_cvt / total_cvt)
```

## Testing & Monitoring

### Economic System Tests

```python
# File: tests/test_economic_system.py
import pytest
import asyncio
from decimal import Decimal
from aia_system.economic.enhanced_economic_governor import EnhancedEconomicGovernor
from aia_system.economic.performance_linkage import CorporatePerformanceLinkage

@pytest.fixture
async def economic_governor():
    governor = EnhancedEconomicGovernor()
    await governor.initialize_economy()
    return governor

@pytest.mark.asyncio
async def test_token_initialization(economic_governor):
    """Test token initialization"""
    assert economic_governor.vwt.circulating_supply > 0
    assert economic_governor.cvt.circulating_supply > 0

@pytest.mark.asyncio
async def test_reward_calculation(economic_governor):
    """Test reward calculation"""
    
    performance_metrics = {
        "accuracy": 0.9,
        "speed": 0.8,
        "consensus_quality": 0.85,
        "innovation": 0.7,
        "collaboration": 0.75
    }
    
    vwt_reward, cvt_reward = await economic_governor.calculate_agent_rewards(
        "agent_1",
        performance_metrics
    )
    
    assert vwt_reward > 0
    assert isinstance(vwt_reward, Decimal)

@pytest.mark.asyncio
async def test_governance_proposal(economic_governor):
    """Test governance proposal creation"""
    
    # Give proposer some CVT
    proposer = "user_1"
    economic_governor.cvt.mint_governance_tokens(
        proposer,
        Decimal("2000"),
        vesting_months=0
    )
    
    # Create proposal
    proposal_id = await economic_governor.create_governance_proposal(
        proposer,
        "parameter_change",
        {
            "parameter": "agent_reward_pool",
            "new_value": "20000000",
            "rationale": "Increase agent incentives"
        }
    )
    
    assert proposal_id is not None
    assert proposal_id in economic_governor.cvt.proposals

@pytest.mark.asyncio
async def test_conviction_voting(economic_governor):
    """Test conviction voting"""
    
    # Setup
    proposer = "proposer"
    voter = "voter"
    
    economic_governor.cvt.mint_governance_tokens(proposer, Decimal("2000"), 0)
    economic_governor.cvt.mint_governance_tokens(voter, Decimal("1000"), 0)
    
    # Create proposal
    proposal_id = await economic_governor.create_governance_proposal(
        proposer,
        "parameter_change",
        {"parameter": "test", "new_value": "value"}
    )
    
    # Vote with conviction
    success = await economic_governor.vote_on_proposal(
        voter,
        proposal_id,
        support=True,
        conviction_level=3
    )
    
    assert success == True
    
    # Check vote was recorded
    proposal = economic_governor.cvt.proposals[proposal_id]
    assert proposal["votes_for"] > 0
```

## Deployment Configuration

### Docker Setup

```dockerfile
# File: aia_system/economic/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY economic/ ./economic/

ENV PYTHONPATH=/app

CMD ["python", "-m", "economic.service"]
```

### Kubernetes Configuration

```yaml
# File: k8s/economic/economic-governor.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: economic-governor
  namespace: mas-system
spec:
  replicas: 1  # Single instance for consistency
  selector:
    matchLabels:
      app: economic-governor
  template:
    metadata:
      labels:
        app: economic-governor
    spec:
      containers:
      - name: economic-governor
        image: mas-system/economic-governor:1.0.0
        ports:
        - containerPort: 8100
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: POSTGRES_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
```

## Next Steps

1. Deploy economic system components
2. Test token mechanics with simulated transactions
3. Integrate with agent reward distribution
4. Setup governance UI for proposals
5. Monitor token velocity and economic health
6. Move to Phase 3: Advanced Capabilities