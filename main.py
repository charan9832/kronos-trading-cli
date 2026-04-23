#!/usr/bin/env python3
"""
Kronos Trading Agent - Main Orchestrator
=========================================

Entry point for the full trading system.

Usage:
    python main.py validate    # Run Phase 1: Kronos validation
    python main.py train       # Run Phase 2: RL training
    python main.py harness     # Run Phase 3: Start trading harness
    python main.py validate-full # Run Phase 4: Full validation
    python main.py run         # Run complete pipeline
"""

import argparse
import asyncio
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from code.kronos_validator import KronosValidator
    from code.rl_trading_agent import RLTradingAgent, train_on_historical_data
    from code.trading_harness import TradingHarness, TradingState
    from code.validation_framework import ValidationFramework
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    raise


def phase1_validate_kronos():
    """
    Phase 1: Validate Kronos model on out-of-sample data.
    
    This is the GATEKEEPER phase. If Kronos doesn't show signal,
    the entire project should abort.
    """
    logger.info("="*70)
    logger.info("PHASE 1: Kronos Model Validation (Gatekeeper)")
    logger.info("="*70)
    
    validator = KronosValidator(
        assets=["SPY", "QQQ", "TSLA", "BTC-USD"]
    )
    
    report = validator.run_full_validation()
    
    # Print summary
    print("\n" + "="*70)
    print("PHASE 1 RESULTS")
    print("="*70)
    print(f"Overall Status: {report['overall_status']}")
    print(f"Assets Passed: {report['assets_passed']}/{report['assets_tested']}")
    print(f"Go/No-Go: {report['go_no_go']}")
    print(f"\n{report['recommendation']}")
    print("="*70)
    
    return report['overall_status'] == 'PASS'


def phase2_train_rl():
    """
    Phase 2: Train RL policy to wrap Kronos.
    """
    logger.info("="*70)
    logger.info("PHASE 2: RL Agent Training")
    logger.info("="*70)
    
    import numpy as np
    
    # Create agent
    agent = RLTradingAgent()
    
    # Generate mock data (in production, use real historical data)
    np.random.seed(42)
    prices = np.cumsum(np.random.randn(500) * 0.01) + 100
    kronos_preds = prices + np.random.randn(500) * 0.5
    
    # Train
    logger.info("Training RL agent on historical data...")
    metrics = train_on_historical_data(agent, prices, kronos_preds, epochs=50)
    
    # Save model
    models_dir = Path("/tmp/kronos_project/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    agent.save(str(models_dir / "rl_policy.pt"))
    
    print("\n" + "="*70)
    print("PHASE 2 RESULTS")
    print("="*70)
    print(f"Training epochs: {len(metrics)}")
    print(f"Final loss: {metrics[-1]['loss']:.4f}")
    print(f"Mean reward: {metrics[-1]['mean_reward']:.4f}")
    print(f"Model saved to: {models_dir / 'rl_policy.pt'}")
    print("="*70)
    
    return True


def phase3_trading_harness():
    """
    Phase 3: Start the trading harness.
    """
    logger.info("="*70)
    logger.info("PHASE 3: Trading Harness")
    logger.info("="*70)
    
    harness = TradingHarness(mode="paper")
    
    # Set up event handlers
    async def on_analyze():
        logger.info("Analyzing market...")
    
    async def on_decide():
        logger.info("Making decision...")
        return {"action": "HOLD", "size": 0.0}
    
    harness.on_analyze = on_analyze
    harness.on_decide = on_decide
    
    print("\n" + "="*70)
    print("PHASE 3: Trading Harness Started")
    print("="*70)
    print(harness.cmd_status())
    print("\nRun: /trade SPY 0.5  (to simulate a trade)")
    print("="*70)
    
    # Start CLI
    asyncio.run(harness.run_continuous(interval_seconds=5))
    
    return True


def phase4_full_validation():
    """
    Phase 4: Run full validation framework.
    """
    logger.info("="*70)
    logger.info("PHASE 4: Full Validation Framework")
    logger.info("="*70)
    
    import numpy as np
    import pandas as pd
    
    framework = ValidationFramework()
    
    # Generate mock data
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='B')
    np.random.seed(42)
    prices = pd.Series(
        np.cumsum(np.random.randn(len(dates)) * 0.01) + 100,
        index=dates
    )
    
    # Simple strategy
    def momentum_strategy(prices):
        returns = prices.pct_change()
        momentum = returns.rolling(20).mean()
        return momentum.apply(lambda x: 0.5 if x > 0.001 else -0.5 if x < -0.001 else 0)
    
    # Run backtest
    results = framework.run_backtest(prices, momentum_strategy)
    
    # Benchmark
    benchmark = framework.benchmark_vs_buy_hold(
        results['equity_curve'].pct_change().dropna(),
        prices
    )
    
    # Generate report
    report = framework.generate_report(results, benchmark)
    
    print("\n" + "="*70)
    print("PHASE 4 RESULTS")
    print("="*70)
    print(report)
    print("="*70)
    
    # Save report
    output_path = Path('/tmp/kronos_project/results/final_validation_report.txt')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_path}")
    
    return True


def run_full_pipeline():
    """Run all phases in sequence."""
    logger.info("="*70)
    logger.info("KRONOS TRADING AGENT - FULL PIPELINE")
    logger.info("="*70)
    
    # Phase 1: Validation (Gatekeeper)
    if not phase1_validate_kronos():
        logger.error("❌ Phase 1 FAILED - Aborting pipeline")
        return False
    
    logger.info("✅ Phase 1 PASSED - Proceeding to Phase 2")
    
    # Phase 2: RL Training
    if not phase2_train_rl():
        logger.error("❌ Phase 2 FAILED")
        return False
    
    logger.info("✅ Phase 2 PASSED - Proceeding to Phase 3")
    
    # Phase 3: Trading Harness (starts CLI)
    logger.info("⚡ Phase 3: Starting Trading Harness (Interactive)")
    phase3_trading_harness()
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Kronos Trading Agent - Full Pipeline"
    )
    parser.add_argument(
        'command',
        choices=['validate', 'train', 'harness', 'validate-full', 'run'],
        help='Which phase to run'
    )
    
    args = parser.parse_args()
    
    # Create necessary directories
    Path('/tmp/kronos_project/code').mkdir(parents=True, exist_ok=True)
    Path('/tmp/kronos_project/results').mkdir(parents=True, exist_ok=True)
    Path('/tmp/kronos_project/logs').mkdir(parents=True, exist_ok=True)
    Path('/tmp/kronos_project/models').mkdir(parents=True, exist_ok=True)
    
    if args.command == 'validate':
        phase1_validate_kronos()
    elif args.command == 'train':
        phase2_train_rl()
    elif args.command == 'harness':
        phase3_trading_harness()
    elif args.command == 'validate-full':
        phase4_full_validation()
    elif args.command == 'run':
        run_full_pipeline()


if __name__ == "__main__":
    main()
