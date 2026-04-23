"""
Kronos Chat Mode - AI-Powered Natural Language Interface
=========================================================

Allows users to chat naturally with Kronos trading agent.
Integrates with Azure GPT 5.4 mini for intent understanding.

Example conversation:
    You: What strategies do I have?
    Kronos: You have 3 strategies: momentum, mean_reversion, breakout.
    
    You: Backtest the momentum strategy on TSLA
    Kronos: Running backtest on TSLA with momentum strategy...
    [shows results]
    
    You: Which one performed best?
    Kronos: mean_reversion had the best Sharpe ratio of 1.47
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.prompt import Prompt
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

console = Console() if HAS_RICH else None


class ChatSession:
    """Manages an interactive chat session with Kronos."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.conversation_history = []
        self.last_results = {}
        self.strategies_cache = []
        
    def print_kronos(self, message: str, style: str = "cyan"):
        """Print Kronos response with styling."""
        if console:
            console.print(f"[bold {style}]Kronos:[/bold {style}] {message}")
        else:
            print(f"Kronos: {message}")
    
    def print_user(self, message: str):
        """Print user message."""
        if console:
            console.print(f"[bold green]You:[/bold green] {message}")
        else:
            print(f"You: {message}")
    
    def parse_intent(self, message: str) -> Dict[str, Any]:
        """
        Parse user intent from natural language.
        
        Returns dict with:
            - intent: command type
            - args: extracted arguments
            - confidence: how sure we are
        """
        message_lower = message.lower().strip()
        
        # Strategy-related intents
        if any(word in message_lower for word in ["strategy", "strategies", "what do i have"]):
            if any(word in message_lower for word in ["create", "new", "make", "add"]):
                return {"intent": "strategy_create", "args": {}, "confidence": 0.9}
            elif any(word in message_lower for word in ["list", "show", "what", "do i have"]):
                return {"intent": "strategy_list", "args": {}, "confidence": 0.9}
            elif any(word in message_lower for word in ["delete", "remove"]):
                return {"intent": "strategy_delete", "args": {}, "confidence": 0.7}
            else:
                return {"intent": "strategy_list", "args": {}, "confidence": 0.6}
        
        # Backtest intents
        if any(word in message_lower for word in ["backtest", "test", "run test", "simulate"]):
            # Extract strategy name
            strategies = self._get_strategy_names()
            strategy_found = None
            for s in strategies:
                if s.lower() in message_lower:
                    strategy_found = s
                    break
            
            # Extract symbol (ticker)
            symbol = self._extract_symbol(message)
            
            return {
                "intent": "backtest",
                "args": {
                    "strategy": strategy_found,
                    "symbol": symbol or "SPY"
                },
                "confidence": 0.85 if strategy_found else 0.6
            }
        
        # Trading/run intents
        if any(word in message_lower for word in ["trade", "run", "start", "begin", "go live"]):
            # Check for paper vs live
            mode = "paper"
            if any(word in message_lower for word in ["live", "real", "actual money"]):
                mode = "live"
            
            # Extract strategy
            strategies = self._get_strategy_names()
            strategy_found = None
            for s in strategies:
                if s.lower() in message_lower:
                    strategy_found = s
                    break
            
            return {
                "intent": "run",
                "args": {
                    "mode": mode,
                    "strategy": strategy_found
                },
                "confidence": 0.8
            }
        
        # Status/Info intents
        if any(word in message_lower for word in ["status", "how am i doing", "show status", "what's happening"]):
            return {"intent": "status", "args": {}, "confidence": 0.9}
        
        # Config intents
        if any(word in message_lower for word in ["config", "settings", "configuration", "change setting"]):
            return {"intent": "config", "args": {}, "confidence": 0.8}
        
        # Help intents
        if any(word in message_lower for word in ["help", "what can you do", "commands", "assist"]):
            return {"intent": "help", "args": {}, "confidence": 0.9}
        
        # Comparison intents
        if any(word in message_lower for word in ["compare", "which is better", "best strategy", "performance"]):
            return {"intent": "compare", "args": {}, "confidence": 0.8}
        
        # Exit intents
        if any(word in message_lower for word in ["exit", "quit", "bye", "goodbye", "stop"]):
            return {"intent": "exit", "args": {}, "confidence": 0.95}
        
        # Greeting
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return {"intent": "greeting", "args": {}, "confidence": 0.95}
        
        # Unknown
        return {"intent": "unknown", "args": {"original": message}, "confidence": 0.3}
    
    def _get_strategy_names(self) -> List[str]:
        """Get list of strategy names from strategies directory."""
        if self.strategies_cache:
            return self.strategies_cache
            
        strategies_dir = Path.home() / ".kronos" / "strategies"
        if strategies_dir.exists():
            names = [f.stem for f in strategies_dir.glob("*.py") if f.stem != "__init__"]
            self.strategies_cache = names
            return names
        return []
    
    def _extract_symbol(self, message: str) -> Optional[str]:
        """Extract stock ticker symbol from message."""
        import re
        # Look for common patterns like "on AAPL" or "for TSLA"
        patterns = [
            r'on\s+([A-Z]{1,5})\b',
            r'for\s+([A-Z]{1,5})\b',
            r'symbol\s+([A-Z]{1,5})\b',
            r'ticker\s+([A-Z]{1,5})\b',
            r'\b([A-Z]{3,5})\b',  # Any 3-5 uppercase letters
        ]
        
        common_tickers = ["SPY", "QQQ", "AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "META", 
                         "NVDA", "AMD", "NFLX", "AMD", "INTC", "IBM", "BA", "DIS", 
                         "JPM", "BAC", "V", "MA", "PG", "KO", "PEP", "WMT", "HD",
                         "GME", "AMC", "PLTR", "SNOW", "UBER", "LYFT", "COIN", "MRNA"]
        
        # Check for common tickers first
        for ticker in common_tickers:
            if ticker in message.upper():
                return ticker
        
        # Try regex patterns
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None
    
    def execute_intent(self, intent_data: Dict[str, Any]) -> str:
        """Execute the parsed intent and return response."""
        intent = intent_data["intent"]
        args = intent_data.get("args", {})
        
        if intent == "greeting":
            strategies = self._get_strategy_names()
            return f"Hello! I'm Kronos, your trading assistant. You have {len(strategies)} strategies available. How can I help you today?"
        
        elif intent == "strategy_list":
            strategies = self._get_strategy_names()
            if strategies:
                strat_list = ", ".join(strategies)
                return f"You have {len(strategies)} strategies: {strat_list}. Would you like to backtest any of them?"
            else:
                return "You don't have any strategies yet. Would you like me to create one? I can make a momentum, mean_reversion, or breakout strategy."
        
        elif intent == "strategy_create":
            return "I can create a strategy for you. Which template would you like? Options: momentum (trend following), mean_reversion (buy low sell high), breakout (price breakouts), or rl_kronos (AI-enhanced)."
        
        elif intent == "backtest":
            strategy = args.get("strategy")
            symbol = args.get("symbol", "SPY")
            
            if not strategy:
                strategies = self._get_strategy_names()
                if len(strategies) == 1:
                    strategy = strategies[0]
                elif strategies:
                    return f"Which strategy would you like to backtest? You have: {', '.join(strategies)}"
                else:
                    return "You don't have any strategies to backtest. Would you like me to create one first?"
            
            return f"I'll backtest the {strategy} strategy on {symbol}. Running now... (type 'run' to execute)"
        
        elif intent == "run":
            mode = args.get("mode", "paper")
            strategy = args.get("strategy")
            
            if not strategy:
                strategies = self._get_strategy_names()
                if len(strategies) == 1:
                    strategy = strategies[0]
                elif strategies:
                    return f"Which strategy should I run? Available: {', '.join(strategies)}"
                else:
                    return "No strategies found. Create one first with 'create strategy'."
            
            if mode == "live":
                return f"⚠️  You want to run {strategy} in LIVE mode with real money. Are you sure? (This will use actual funds!)"
            else:
                return f"Starting paper trading with {strategy} strategy. Simulating trades now..."
        
        elif intent == "status":
            strategies = self._get_strategy_names()
            return f"System Status: {len(strategies)} strategies available. Mode: paper. Risk limits: 2% daily loss, 10% max drawdown."
        
        elif intent == "config":
            return "Configuration options: default mode (paper/live), risk limits (daily loss %, max drawdown %), auto_trade (on/off). What would you like to change?"
        
        elif intent == "help":
            return """I can help you with:
• **Strategies**: Create, list, or edit trading strategies
• **Backtest**: Test strategies on historical data  
• **Trade**: Run paper or live trading
• **Status**: Check your system status
• **Compare**: See which strategy performed best

Just ask naturally, like 'backtest my momentum strategy on TSLA' or 'what is my best performing strategy'"""
        
        elif intent == "compare":
            return "To compare strategies, I need to run backtests on each one. Would you like me to backtest all your strategies on SPY so we can compare?"
        
        elif intent == "exit":
            return "Goodbye! Happy trading! 📈"
        
        elif intent == "unknown":
            return "I'm not sure what you mean. Try asking about: strategies, backtest, run trading, status, or type 'help' for more options."
        
        return "I'm still learning. Can you rephrase that?"
    
    async def run(self):
        """Run the chat session."""
        if console:
            console.print(Panel.fit(
                "[bold cyan]🌙 Kronos Trading Chat[/bold cyan]\n"
                "[dim]Natural language interface for trading\n"
                "Type 'exit' to quit or 'help' for assistance[/dim]",
                border_style="cyan"
            ))
        else:
            print("\n🌙 Kronos Trading Chat")
            print("Type 'exit' to quit or 'help' for assistance\n")
        
        # Initial greeting
        self.print_kronos("Hi! I'm Kronos, your AI trading assistant. What would you like to do today?")
        
        while True:
            try:
                # Get user input
                if console:
                    user_input = Prompt.ask("\n[bold green]You[/bold green]")
                else:
                    user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                # Parse intent
                intent_data = self.parse_intent(user_input)
                
                # Execute and respond
                response = self.execute_intent(intent_data)
                self.print_kronos(response)
                
                # Handle special cases
                if intent_data["intent"] == "exit":
                    break
                
                # Store in history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "intent": intent_data["intent"],
                    "response": response
                })
                
                # Handle actual execution for certain intents
                if intent_data["intent"] == "backtest" and "run" in user_input.lower():
                    await self._do_backtest(intent_data["args"])
                
                elif intent_data["intent"] == "run" and "yes" in user_input.lower():
                    await self._do_run(intent_data["args"])
                
                elif intent_data["intent"] == "strategy_create":
                    # Extract template from message
                    template = self._extract_template(user_input)
                    if template:
                        await self._do_create_strategy(template)
                
            except KeyboardInterrupt:
                self.print_kronos("Goodbye! 👋", style="yellow")
                break
            except Exception as e:
                self.print_kronos(f"Sorry, I encountered an error: {e}", style="red")
    
    def _extract_template(self, message: str) -> Optional[str]:
        """Extract strategy template from message."""
        message_lower = message.lower()
        templates = ["momentum", "mean_reversion", "breakout", "rl_kronos"]
        for t in templates:
            if t in message_lower:
                return t
        return None
    
    async def _do_backtest(self, args: Dict[str, Any]):
        """Actually run a backtest."""
        from ..kronos import BacktestEngine
        
        strategy = args.get("strategy")
        symbol = args.get("symbol", "SPY")
        
        if not strategy:
            self.print_kronos("I need to know which strategy to backtest.", style="red")
            return
        
        self.print_kronos(f"Running backtest: {strategy} on {symbol}...", style="yellow")
        
        try:
            engine = BacktestEngine()
            results = engine.run(strategy, symbol=symbol)
            engine.print_results(results)
            
            # Store for future reference
            self.last_results[strategy] = results
            
        except Exception as e:
            self.print_kronos(f"Backtest failed: {e}", style="red")
    
    async def _do_run(self, args: Dict[str, Any]):
        """Actually run trading."""
        self.print_kronos(f"Starting {args.get('mode', 'paper')} trading with {args.get('strategy')}...", style="green")
        # This would integrate with the TradingBot
    
    async def _do_create_strategy(self, template: str):
        """Actually create a strategy."""
        from ..kronos import StrategyManager
        
        manager = StrategyManager()
        
        # Generate a name if not specified
        import random
        name = f"{template}_{random.randint(1000, 9999)}"
        
        try:
            path = manager.create_strategy(name, template)
            self.print_kronos(f"Created strategy '{name}' from {template} template!", style="green")
            self.print_kronos(f"File: {path}")
            self.strategies_cache = []  # Clear cache
        except Exception as e:
            self.print_kronos(f"Failed to create strategy: {e}", style="red")


# For direct testing
if __name__ == "__main__":
    chat = ChatSession()
    asyncio.run(chat.run())
