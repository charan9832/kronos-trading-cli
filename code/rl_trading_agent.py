"""
RL Trading Agent (Phase 2)
GRPO-based RL policy that wraps Kronos predictions.
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TradingState:
    """State representation for the RL agent."""
    
    def __init__(self, kronos_pred: float, volatility: float, 
                 trend: float, position: float = 0.0):
        self.kronos_pred = kronos_pred  # Kronos prediction
        self.volatility = volatility    # 20-day realized vol
        self.trend = trend              # 20-day trend
        self.position = position        # Current position (0-1)
    
    def to_tensor(self) -> torch.Tensor:
        """Convert state to tensor for network input."""
        return torch.FloatTensor([
            self.kronos_pred,
            self.volatility,
            self.trend,
            self.position
        ])


class RLPolicyNetwork(nn.Module):
    """Policy network for position sizing."""
    
    def __init__(self, state_dim: int = 4, action_dim: int = 1, 
                 hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Sigmoid()  # Output 0-1 for position sizing
        )
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass. Returns position size (0-1)."""
        return self.net(state)


class RLTradingAgent:
    """
    RL agent that learns to size positions based on Kronos predictions.
    
    Uses GRPO (Group Relative Policy Optimization) for training.
    """
    
    def __init__(self, 
                 learning_rate: float = 3e-4,
                 risk_target: float = 0.10,  # Target 10% annualized vol
                 max_position: float = 1.0,
                 min_position: float = 0.0):
        
        self.policy = RLPolicyNetwork()
        self.optimizer = torch.optim.Adam(
            self.policy.parameters(), 
            lr=learning_rate
        )
        
        self.risk_target = risk_target
        self.max_position = max_position
        self.min_position = min_position
        
        # Training history
        self.episode_returns = []
        self.episode_lengths = []
        
    def get_action(self, state: TradingState) -> float:
        """
        Get position size from policy.
        
        Returns: Position size (0-1)
        """
        with torch.no_grad():
            state_tensor = state.to_tensor().unsqueeze(0)
            action = self.policy(state_tensor)
            return action.item()
    
    def calculate_reward(self, 
                        returns: List[float], 
                        downside_returns: List[float]) -> float:
        """
        Calculate Sortino ratio as reward.
        
        Sortino = mean(return) / std(downside_returns)
        """
        if len(returns) == 0:
            return 0.0
        
        mean_return = np.mean(returns)
        
        # Downside deviation
        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            downside_std = 0.001  # Small floor to avoid div by zero
        else:
            downside_std = np.std(downside_returns)
        
        sortino = mean_return / downside_std
        
        # Annualize
        return sortino * np.sqrt(252)
    
    def train_step(self, 
                   states: List[TradingState],
                   actions: List[float],
                   rewards: List[float]) -> Dict:
        """
        Single training step using policy gradient.
        
        Simplified GRPO-style update.
        """
        if len(states) == 0:
            return {"loss": 0.0, "mean_reward": 0.0}
        
        # Convert to tensors
        state_tensors = torch.stack([s.to_tensor() for s in states])
        action_tensors = torch.FloatTensor(actions).unsqueeze(1)
        reward_tensors = torch.FloatTensor(rewards)
        
        # Forward pass
        predicted_actions = self.policy(state_tensors)
        
        # Policy gradient loss (simplified)
        # Encourage actions that led to higher rewards
        advantage = reward_tensors - reward_tensors.mean()
        loss = -torch.mean(advantage * torch.log(predicted_actions.squeeze() + 1e-8))
        
        # Update
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 1.0)
        self.optimizer.step()
        
        return {
            "loss": loss.item(),
            "mean_reward": reward_tensors.mean().item(),
            "std_reward": reward_tensors.std().item()
        }
    
    def save(self, path: str):
        """Save model checkpoint."""
        torch.save({
            'policy_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model checkpoint."""
        checkpoint = torch.load(path)
        self.policy.load_state_dict(checkpoint['policy_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        logger.info(f"Model loaded from {path}")


def train_on_historical_data(
    agent: RLTradingAgent,
    historical_data: np.ndarray,
    kronos_predictions: np.ndarray,
    epochs: int = 100
) -> List[Dict]:
    """
    Train agent on historical data.
    
    Args:
        agent: RLTradingAgent instance
        historical_data: Price data (OHLCV)
        kronos_predictions: Kronos model predictions
        epochs: Number of training epochs
    
    Returns:
        List of training metrics per epoch
    """
    metrics = []
    
    for epoch in range(epochs):
        states = []
        actions = []
        rewards = []
        
        # Simulate trading over historical data
        for i in range(20, len(historical_data) - 1):
            # Calculate state features
            returns = np.diff(historical_data[i-20:i]) / historical_data[i-20:i-1]
            volatility = np.std(returns)
            trend = (historical_data[i] - historical_data[i-20]) / historical_data[i-20]
            
            state = TradingState(
                kronos_pred=kronos_predictions[i],
                volatility=volatility,
                trend=trend,
                position=actions[-1] if actions else 0.0
            )
            
            # Get action
            action = agent.get_action(state)
            
            # Calculate reward (next-day return)
            next_return = (historical_data[i+1] - historical_data[i]) / historical_data[i]
            reward = next_return * action  # Return scaled by position
            
            states.append(state)
            actions.append(action)
            rewards.append(reward)
        
        # Train on this episode
        if len(states) > 10:
            epoch_metrics = agent.train_step(states, actions, rewards)
            epoch_metrics['epoch'] = epoch
            epoch_metrics['total_return'] = sum(rewards)
            metrics.append(epoch_metrics)
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Loss={epoch_metrics['loss']:.4f}, "
                          f"Mean Reward={epoch_metrics['mean_reward']:.4f}")
    
    return metrics


if __name__ == "__main__":
    # Example usage
    agent = RLTradingAgent()
    
    # Mock data for testing
    prices = np.cumsum(np.random.randn(100) * 0.01) + 100
    kronos_preds = prices + np.random.randn(100) * 0.5
    
    metrics = train_on_historical_data(agent, prices, kronos_preds, epochs=10)
    print(f"Training complete. Final loss: {metrics[-1]['loss']:.4f}")
    
    # Save model
    agent.save("/tmp/kronos_project/models/rl_policy.pt")
