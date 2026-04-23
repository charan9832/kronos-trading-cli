"""
Validation Framework (Phase 4)
Comprehensive backtesting and paper trading validation.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Callable
import json
import logging

logger = logging.getLogger(__name__)


class TransactionCostModel:
    """
    Realistic transaction cost modeling.
    
    Includes: commission, slippage, market impact
    """
    
    def __init__(
        self,
        commission_pct: float = 0.05,  # 0.05% per trade
        slippage_pct: float = 0.1,    # 0.1% slippage
        min_commission: float = 1.0     # $1 minimum
    ):
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        self.min_commission = min_commission
    
    def calculate_cost(self, notional_value: float) -> float:
        """Calculate total transaction cost for a trade."""
        commission = max(notional_value * self.commission_pct / 100, self.min_commission)
        slippage = notional_value * self.slippage_pct / 100
        return commission + slippage


class WalkForwardAnalyzer:
    """
    Walk-forward analysis for out-of-sample testing.
    
    Prevents lookahead bias by training on past, testing on future.
    """
    
    def __init__(
        self,
        train_size: int = 252,    # 1 year training
        test_size: int = 63,      # 3 months testing
        step_size: int = 63       # Step forward 3 months
    ):
        self.train_size = train_size
        self.test_size = test_size
        self.step_size = step_size
    
    def generate_windows(self, total_data: pd.DataFrame) -> List[Dict]:
        """
        Generate train/test windows for walk-forward analysis.
        
        Returns list of windows with train_idx and test_idx
        """
        n = len(total_data)
        windows = []
        
        start = 0
        while start + self.train_size + self.test_size <= n:
            train_start = start
            train_end = start + self.train_size
            test_start = train_end
            test_end = test_start + self.test_size
            
            windows.append({
                'train_idx': (train_start, train_end),
                'test_idx': (test_start, test_end),
                'train_dates': (total_data.index[train_start], total_data.index[train_end-1]),
                'test_dates': (total_data.index[test_start], total_data.index[test_end-1])
            })
            
            start += self.step_size
        
        return windows


class StressTestScenario:
    """Single stress test scenario."""
    
    def __init__(self, name: str, start_date: str, end_date: str, description: str):
        self.name = name
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.description = description


class ValidationFramework:
    """
    Comprehensive validation framework for trading strategies.
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.tx_cost_model = TransactionCostModel()
        self.walk_forward = WalkForwardAnalyzer()
        
        # Predefined stress scenarios
        self.stress_scenarios = [
            StressTestScenario(
                "COVID Crash 2020",
                "2020-02-19", "2020-03-23",
                "S&P 500 dropped 34% in 33 days"
            ),
            StressTestScenario(
                "2008 Financial Crisis",
                "2007-10-09", "2009-03-09",
                "Great Recession bear market"
            ),
            StressTestScenario(
                "2010 Flash Crash",
                "2010-05-06", "2010-05-06",
                "Dow dropped 998 points in minutes"
            ),
            StressTestScenario(
                "2022 Inflation Selloff",
                "2022-01-03", "2022-10-12",
                "Fed rate hikes, tech selloff"
            )
        ]
    
    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate annualized Sharpe ratio."""
        if returns.std() == 0:
            return 0.0
        return returns.mean() / returns.std() * np.sqrt(252)
    
    def calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio (downside risk only)."""
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        return returns.mean() / downside_returns.std() * np.sqrt(252)
    
    def calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown percentage."""
        rolling_max = equity_curve.cummax()
        drawdown = (equity_curve - rolling_max) / rolling_max
        return drawdown.min() * 100
    
    def run_backtest(
        self,
        price_data: pd.Series,
        signal_function: Callable[[pd.Series], pd.Series],
        include_costs: bool = True
    ) -> Dict:
        """
        Run single backtest with transaction costs.
        
        Args:
            price_data: Asset price series
            signal_function: Function that takes prices and returns position sizes (-1 to 1)
            include_costs: Whether to include transaction costs
        
        Returns:
            Dictionary with backtest results
        """
        signals = signal_function(price_data)
        
        # Calculate returns
        price_returns = price_data.pct_change().dropna()
        strategy_returns = signals.shift(1) * price_returns  # Lag signal by 1 day
        strategy_returns = strategy_returns.dropna()
        
        # Apply transaction costs
        if include_costs:
            # Detect signal changes (trades)
            signal_changes = signals.diff().abs()
            trades = signal_changes > 0.01  # Threshold for significant change
            
            # Estimate costs (simplified)
            trade_costs = trades * self.tx_cost_model.calculate_cost(self.initial_capital)
            daily_cost_pct = trade_costs / self.initial_capital * 100
            strategy_returns = strategy_returns - daily_cost_pct
        
        # Calculate equity curve
        equity_curve = (1 + strategy_returns).cumprod() * self.initial_capital
        
        # Buy and hold benchmark
        bh_equity = (1 + price_returns).cumprod() * self.initial_capital
        
        results = {
            'total_return_pct': (equity_curve.iloc[-1] / self.initial_capital - 1) * 100,
            'annualized_return_pct': strategy_returns.mean() * 252 * 100,
            'volatility_pct': strategy_returns.std() * np.sqrt(252) * 100,
            'sharpe_ratio': self.calculate_sharpe_ratio(strategy_returns),
            'sortino_ratio': self.calculate_sortino_ratio(strategy_returns),
            'max_drawdown_pct': self.calculate_max_drawdown(equity_curve),
            'num_trades': len(signals.diff().abs()[signals.diff().abs() > 0.01]),
            'win_rate_pct': (strategy_returns > 0).mean() * 100,
            'vs_buy_hold_pct': (equity_curve.iloc[-1] / bh_equity.iloc[-1] - 1) * 100,
            'equity_curve': equity_curve,
            'signals': signals
        }
        
        return results
    
    def benchmark_vs_buy_hold(
        self,
        strategy_returns: pd.Series,
        price_data: pd.Series
    ) -> Dict:
        """
        Compare strategy against buy-and-hold benchmark.
        """
        bh_returns = price_data.pct_change().dropna()
        
        comparison = {
            'strategy_total_return': (1 + strategy_returns).prod() - 1,
            'bh_total_return': (1 + bh_returns).prod() - 1,
            'strategy_annualized_vol': strategy_returns.std() * np.sqrt(252),
            'bh_annualized_vol': bh_returns.std() * np.sqrt(252),
            'strategy_sharpe': self.calculate_sharpe_ratio(strategy_returns),
            'bh_sharpe': self.calculate_sharpe_ratio(bh_returns),
        }
        
        comparison['excess_return'] = comparison['strategy_total_return'] - comparison['bh_total_return']
        comparison['outperformed'] = comparison['excess_return'] > 0
        
        return comparison
    
    def run_walk_forward_validation(
        self,
        price_data: pd.DataFrame,
        train_function: Callable[[pd.Series], dict],
        predict_function: Callable[[dict, pd.Series], pd.Series]
    ) -> List[Dict]:
        """
        Run walk-forward validation.
        
        Args:
            price_data: Full price history
            train_function: Function to train model on training data
            predict_function: Function to predict on test data using trained model
        
        Returns:
            List of results for each window
        """
        windows = self.walk_forward.generate_windows(price_data)
        results = []
        
        for i, window in enumerate(windows):
            logger.info(f"Walk-forward window {i+1}/{len(windows)}")
            
            train_data = price_data.iloc[window['train_idx'][0]:window['train_idx'][1]]
            test_data = price_data.iloc[window['test_idx'][0]:window['test_idx'][1]]
            
            # Train on training data
            model = train_function(train_data)
            
            # Predict on test data
            predictions = predict_function(model, test_data)
            
            # Evaluate
            test_returns = test_data.pct_change().dropna()
            strategy_returns = predictions.shift(1) * test_returns
            
            results.append({
                'window': i,
                'train_dates': window['train_dates'],
                'test_dates': window['test_dates'],
                'sharpe': self.calculate_sharpe_ratio(strategy_returns),
                'return_pct': strategy_returns.sum() * 100,
                'max_dd_pct': self.calculate_max_drawdown(
                    (1 + strategy_returns).cumprod() * self.initial_capital
                )
            })
        
        return results
    
    def run_stress_test(
        self,
        price_data: pd.DataFrame,
        signal_function: Callable[[pd.Series], pd.Series],
        scenario: Optional[StressTestScenario] = None
    ) -> Dict:
        """
        Run stress test during crisis periods.
        """
        if scenario is None:
            scenario = self.stress_scenarios[0]  # Default to COVID
        
        # Filter data to stress period
        mask = (price_data.index >= scenario.start_date) & (price_data.index <= scenario.end_date)
        stress_data = price_data[mask]
        
        if len(stress_data) == 0:
            return {
                'scenario': scenario.name,
                'error': 'No data for stress period'
            }
        
        # Run backtest on stress period
        results = self.run_backtest(stress_data, signal_function)
        results['scenario'] = scenario.name
        results['scenario_description'] = scenario.description
        results['period'] = f"{scenario.start_date.date()} to {scenario.end_date.date()}"
        
        return results
    
    def paper_trading_simulation(
        self,
        live_signal_function: Callable[[], float],
        duration_days: int = 30
    ) -> Dict:
        """
        Simulate paper trading for validation before live deployment.
        
        Args:
            live_signal_function: Function that returns current signal
            duration_days: Number of days to simulate
        
        Returns:
            Paper trading results
        """
        logger.info(f"Starting {duration_days}-day paper trading simulation")
        
        # Track simulated performance
        daily_returns = []
        signals = []
        
        for day in range(duration_days):
            signal = live_signal_function()
            signals.append(signal)
            
            # Simulate next-day return (placeholder)
            simulated_return = np.random.normal(0.0001, 0.02)
            daily_returns.append(signal * simulated_return)
            
            logger.info(f"Day {day+1}: Signal={signal:.2f}, Return={daily_returns[-1]:.4f}")
        
        returns_series = pd.Series(daily_returns)
        
        results = {
            'duration_days': duration_days,
            'total_return_pct': returns_series.sum() * 100,
            'sharpe': self.calculate_sharpe_ratio(returns_series),
            'max_dd_pct': self.calculate_max_drawdown(
                (1 + returns_series).cumprod() * self.initial_capital
            ),
            'avg_signal': np.mean(signals),
            'signal_std': np.std(signals)
        }
        
        return results
    
    def generate_report(
        self,
        backtest_results: Dict,
        benchmark_results: Dict,
        walk_forward_results: Optional[List[Dict]] = None,
        stress_test_results: Optional[List[Dict]] = None
    ) -> str:
        """Generate comprehensive validation report."""
        
        lines = [
            "╔════════════════════════════════════════════════════════════════╗",
            "║              VALIDATION FRAMEWORK REPORT                       ║",
            "╠════════════════════════════════════════════════════════════════╣",
            f"║ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M'):<48} ║",
            "╠════════════════════════════════════════════════════════════════╣",
            "║ BACKTEST RESULTS                                               ║",
            "╟────────────────────────────────────────────────────────────────╢",
            f"║ Total Return:      {backtest_results['total_return_pct']:>8.2f}%                          ║",
            f"║ Annualized Return: {backtest_results['annualized_return_pct']:>8.2f}%                          ║",
            f"║ Volatility:         {backtest_results['volatility_pct']:>8.2f}%                          ║",
            f"║ Sharpe Ratio:       {backtest_results['sharpe_ratio']:>8.2f}                           ║",
            f"║ Sortino Ratio:      {backtest_results['sortino_ratio']:>8.2f}                           ║",
            f"║ Max Drawdown:       {backtest_results['max_drawdown_pct']:>8.2f}%                          ║",
            f"║ Number of Trades:   {backtest_results['num_trades']:>8}                           ║",
            f"║ Win Rate:           {backtest_results['win_rate_pct']:>8.1f}%                          ║",
            "╟────────────────────────────────────────────────────────────────╢",
            "║ BENCHMARK COMPARISON                                           ║",
            "╟────────────────────────────────────────────────────────────────╢",
            f"║ Strategy Return:    {benchmark_results['strategy_total_return']*100:>8.2f}%                          ║",
            f"║ Buy & Hold Return:  {benchmark_results['bh_total_return']*100:>8.2f}%                          ║",
            f"║ Excess Return:      {benchmark_results['excess_return']*100:>8.2f}%                          ║",
            f"║ {'OUTPERFORMED' if benchmark_results['outperformed'] else 'UNDERPERFORMED':<58} ║",
        ]
        
        if walk_forward_results:
            lines.extend([
                "╟────────────────────────────────────────────────────────────────╢",
                "║ WALK-FORWARD VALIDATION                                        ║",
                "╟────────────────────────────────────────────────────────────────╢",
                f"║ Windows Tested:     {len(walk_forward_results):>8}                           ║",
                f"║ Avg Sharpe:         {np.mean([r['sharpe'] for r in walk_forward_results]):>8.2f}                           ║",
            ])
        
        lines.extend([
            "╚════════════════════════════════════════════════════════════════╝",
        ])
        
        return '\n'.join(lines)


# Example usage
if __name__ == "__main__":
    framework = ValidationFramework()
    
    # Mock price data
    dates = pd.date_range('2020-01-01', '2024-12-31', freq='B')
    np.random.seed(42)
    prices = pd.Series(
        np.cumsum(np.random.randn(len(dates)) * 0.01) + 100,
        index=dates
    )
    
    # Simple momentum strategy
    def momentum_strategy(prices):
        returns = prices.pct_change()
        momentum = returns.rolling(20).mean()
        return momentum.apply(lambda x: 1 if x > 0 else -1 if x < 0 else 0)
    
    # Run backtest
    results = framework.run_backtest(prices, momentum_strategy)
    
    # Compare to benchmark
    benchmark = framework.benchmark_vs_buy_hold(
        results['equity_curve'].pct_change().dropna(),
        prices
    )
    
    # Generate report
    report = framework.generate_report(results, benchmark)
    print(report)
    
    # Save results
    output_path = '/tmp/kronos_project/results/validation_report.txt'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {output_path}")
