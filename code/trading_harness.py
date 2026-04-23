"""
Trading Harness (Phase 3)
Simplified event-driven execution system.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Callable

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingState(Enum):
    """Trading state machine states."""
    IDLE = "idle"
    ANALYZE = "analyze"
    DECIDE = "decide"
    EXECUTE = "execute"
    LOG = "log"


@dataclass
class RiskLimits:
    """Risk management parameters."""
    max_daily_loss_pct: float = 2.0      # Stop trading after 2% daily loss
    max_drawdown_pct: float = 10.0       # Hard stop at 10% drawdown
    max_position_size: float = 1.0       # Max 100% allocated
    max_trades_per_day: int = 10         # Limit overtrading


@dataclass
class Position:
    """Current position tracking."""
    symbol: str
    size: float = 0.0                    # Position size (0-1)
    entry_price: float = 0.0
    entry_time: Optional[datetime] = None
    unrealized_pnl: float = 0.0


@dataclass
class TradingSession:
    """Session tracking for risk management."""
    start_time: datetime = field(default_factory=datetime.now)
    daily_pnl: float = 0.0
    total_trades: int = 0
    peak_value: float = field(default_factory=lambda: 100000.0)  # Start with 100k
    current_value: float = 100000.0
    
    @property
    def drawdown_pct(self) -> float:
        """Calculate current drawdown percentage."""
        if self.peak_value == 0:
            return 0.0
        return (self.peak_value - self.current_value) / self.peak_value * 100
    
    def update_value(self, new_value: float):
        """Update portfolio value and track peak."""
        self.current_value = new_value
        if new_value > self.peak_value:
            self.peak_value = new_value


class TradingHarness:
    """
    Simplified event-driven trading execution.
    
    Replaces multi-agent Claw Code coordination with single deterministic state machine.
    """
    
    def __init__(
        self,
        risk_limits: Optional[RiskLimits] = None,
        mode: str = "paper"  # "paper" or "live"
    ):
        self.risk_limits = risk_limits or RiskLimits()
        self.mode = mode
        self.state = TradingState.IDLE
        self.session = TradingSession()
        self.positions: Dict[str, Position] = {}
        
        # Event handlers
        self.on_analyze: Optional[Callable] = None
        self.on_decide: Optional[Callable] = None
        self.on_execute: Optional[Callable] = None
        
        # Circuit breaker
        self.trading_halted = False
        self.halt_reason: Optional[str] = None
        
        # Event log
        self.events = []
    
    def _log_event(self, event_type: str, data: dict):
        """Log an event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "state": self.state.value,
            "type": event_type,
            "data": data
        }
        self.events.append(event)
        logger.info(f"[{self.state.value}] {event_type}: {data}")
    
    def check_risk_limits(self) -> tuple[bool, Optional[str]]:
        """
        Check if any risk limits are breached.
        
        Returns: (is_safe, reason_if_not_safe)
        """
        # Check daily loss
        daily_loss_pct = abs(self.session.daily_pnl) / self.session.current_value * 100
        if daily_loss_pct >= self.risk_limits.max_daily_loss_pct:
            return False, f"Daily loss limit hit: {daily_loss_pct:.2f}%"
        
        # Check drawdown
        if self.session.drawdown_pct >= self.risk_limits.max_drawdown_pct:
            return False, f"Max drawdown hit: {self.session.drawdown_pct:.2f}%"
        
        # Check trade count
        if self.session.total_trades >= self.risk_limits.max_trades_per_day:
            return False, f"Max trades per day: {self.session.total_trades}"
        
        return True, None
    
    async def transition_to(self, new_state: TradingState):
        """Transition to a new state."""
        logger.info(f"State transition: {self.state.value} -> {new_state.value}")
        self._log_event("state_transition", {"from": self.state.value, "to": new_state.value})
        self.state = new_state
    
    async def state_analyze(self):
        """ANALYZE: Gather data and signals."""
        if self.trading_halted:
            return
        
        # Check risk limits
        is_safe, reason = self.check_risk_limits()
        if not is_safe:
            self.trading_halted = True
            self.halt_reason = reason
            logger.error(f"🚫 TRADING HALTED: {reason}")
            return
        
        self._log_event("analyze", {"message": "Analyzing market data and Kronos signals"})
        
        # Call analysis handler if provided
        if self.on_analyze:
            await self.on_analyze()
        
        await self.transition_to(TradingState.DECIDE)
    
    async def state_decide(self):
        """DECIDE: Determine action based on signals."""
        if self.trading_halted:
            return
        
        self._log_event("decide", {"message": "Making trading decision"})
        
        # Call decision handler if provided
        if self.on_decide:
            decision = await self.on_decide()
            self._log_event("decision", decision)
        
        await self.transition_to(TradingState.EXECUTE)
    
    async def state_execute(self):
        """EXECUTE: Place orders (paper or live)."""
        if self.trading_halted:
            return
        
        self._log_event("execute", {"mode": self.mode, "message": "Executing trade"})
        
        if self.mode == "paper":
            # Simulate execution
            self._log_event("paper_trade", {"status": "simulated"})
        else:
            # Live execution (not implemented in this version)
            raise NotImplementedError("Live trading not yet implemented")
        
        self.session.total_trades += 1
        
        await self.transition_to(TradingState.LOG)
    
    async def state_log(self):
        """LOG: Record trade and update P&L."""
        self._log_event("log", {"total_trades": self.session.total_trades})
        
        # Save events to file
        log_file = Path("/tmp/kronos_project/logs/trades.jsonl")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a') as f:
            for event in self.events[-5:]:  # Last 5 events
                f.write(json.dumps(event) + '\n')
        
        await self.transition_to(TradingState.IDLE)
    
    async def run_cycle(self):
        """Run one complete trading cycle."""
        if self.state == TradingState.IDLE:
            await self.transition_to(TradingState.ANALYZE)
        elif self.state == TradingState.ANALYZE:
            await self.state_analyze()
        elif self.state == TradingState.DECIDE:
            await self.state_decide()
        elif self.state == TradingState.EXECUTE:
            await self.state_execute()
        elif self.state == TradingState.LOG:
            await self.state_log()
    
    async def run_continuous(self, interval_seconds: float = 60.0):
        """Run trading loop continuously."""
        logger.info(f"🚀 Trading Harness started ({self.mode} mode)")
        logger.info(f"Risk limits: Daily loss {self.risk_limits.max_daily_loss_pct}%, "
                   f"Max DD {self.risk_limits.max_drawdown_pct}%")
        
        try:
            while True:
                await self.run_cycle()
                
                if self.trading_halted:
                    logger.error(f"Trading halted: {self.halt_reason}")
                    break
                
                await asyncio.sleep(interval_seconds)
        
        except asyncio.CancelledError:
            logger.info("Trading harness stopped")
            raise
    
    # CLI Commands
    def cmd_status(self) -> str:
        """Get current status for CLI display."""
        lines = [
            "╔══════════════════════════════════════════╗",
            "║       TRADING HARNESS STATUS             ║",
            "╠══════════════════════════════════════════╣",
            f"║ State:           {self.state.value:<15}   ║",
            f"║ Mode:            {self.mode:<15}   ║",
            f"║ Daily P&L:       ${self.session.daily_pnl:>10.2f}      ║",
            f"║ Drawdown:        {self.session.drawdown_pct:>10.2f}%      ║",
            f"║ Total Trades:    {self.session.total_trades:>10}        ║",
            f"║ Trading Halted:  {'YES' if self.trading_halted else 'NO':<15}   ║",
        ]
        
        if self.trading_halted and self.halt_reason:
            lines.append(f"║ Halt Reason:     {self.halt_reason[:20]:<20}   ║")
        
        lines.append("╚══════════════════════════════════════════╝")
        
        return '\n'.join(lines)
    
    def cmd_trade(self, symbol: str, size: float) -> str:
        """Manual trade command for CLI."""
        if self.trading_halted:
            return f"❌ Trading halted: {self.halt_reason}"
        
        # Validate size
        if size < 0 or size > self.risk_limits.max_position_size:
            return f"❌ Invalid size: {size}. Must be 0-{self.risk_limits.max_position_size}"
        
        # Update position
        self.positions[symbol] = Position(symbol=symbol, size=size)
        
        return f"✅ Position updated: {symbol} @ {size:.2%}"


# CLI Interface
async def cli_main():
    """Main entry point for CLI."""
    harness = TradingHarness(mode="paper")
    
    print(harness.cmd_status())
    print("\nCommands:")
    print("  /status  - Show current status")
    print("  /trade <symbol> <size>  - Place trade")
    print("  /start   - Start trading loop")
    print("  /stop    - Stop trading loop")
    print("  /quit    - Exit")
    
    while True:
        try:
            cmd = input("\n> ").strip()
            
            if cmd == "/status":
                print(harness.cmd_status())
            
            elif cmd == "/start":
                print("Starting trading loop...")
                # Run in background
                asyncio.create_task(harness.run_continuous())
            
            elif cmd == "/stop":
                print("Stopping... (not fully implemented)")
            
            elif cmd.startswith("/trade"):
                parts = cmd.split()
                if len(parts) == 3:
                    _, symbol, size = parts
                    print(harness.cmd_trade(symbol, float(size)))
                else:
                    print("Usage: /trade <symbol> <size>")
            
            elif cmd == "/quit":
                break
            
            else:
                print(f"Unknown command: {cmd}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")
    
    print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(cli_main())
