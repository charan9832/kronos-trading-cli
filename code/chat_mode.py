"""
Kronos Chat Mode - Interface to Kronos AI Model's Native Conversational Ability
===============================================================================

This is NOT a wrapper with intent parsing - it's a direct interface to the
Kronos AI model which natively understands trading AND conversation.

The Kronos model itself:
- Understands natural language about trading
- Can explain its own decisions
- Answers trading questions using its knowledge
- Maintains conversation context
"""

import asyncio
import os
import sys
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime

# Rich for beautiful CLI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner

# Kronos model
from code.kronos_model import KronosAgent, KronosConfig, Mode


console = Console()


@dataclass
class ChatConfig:
    """Configuration for chat mode."""
    show_reasoning: bool = True  # Show Kronos's thought process
    voice_mode: bool = False     # Future: voice conversation
    auto_trade: bool = False     # Allow Kronos to trade from chat


class KronosChatInterface:
    """
    Direct interface to Kronos AI model's conversational capabilities.
    
    Unlike a command wrapper, this talks to Kronos as an AI that:
    - Understands trading concepts natively
    - Has built-in market knowledge
    - Can reason about strategies
    - Explains its own logic
    """
    
    def __init__(self, config: Optional[KronosConfig] = None):
        self.config = config or KronosConfig()
        self.chat_config = ChatConfig()
        
        # Initialize the actual Kronos AI model
        console.print("[dim]Initializing Kronos AI model...[/dim]")
        self.kronos = KronosAgent(self.config)
        self.kronos.set_mode(Mode.CHAT)
        
        # Conversation history for context
        self.history: List[Dict] = []
        
    def print_banner(self):
        """Print welcome banner."""
        banner = """
╦╔═┌─┐┌─┐┌─┐┌┐┌
╠╩╗│ ││ ││ ││││
╩ ╩└─┘└─┘└─┘┘└┘
        """
        console.print(f"[bold cyan]{banner}[/bold cyan]")
        console.print(Panel.fit(
            "[bold]Kronos AI Model - Native Conversational Trading Agent[/bold]\n"
            "I understand trading. Ask me anything about markets, strategies, or portfolios.",
            border_style="cyan"
        ))
        console.print("\n[dim]Type your message or 'help' for examples. 'exit' to quit.[/dim]\n")
        
    async def run(self):
        """Main chat loop - talking directly to Kronos AI."""
        self.print_banner()
        
        while True:
            try:
                # Get user input
                user_input = console.input("[bold green]You:[/bold green] ").strip()
                
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("\n[dim]Kronos: Goodbye! Happy trading. 📈[/dim]")
                    break
                    
                if user_input.lower() == 'help':
                    self._print_help()
                    continue
                    
                if user_input.lower() == 'status':
                    self._print_status()
                    continue
                
                # Add to history
                self.history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Generate response using Kronos's NATIVE conversational ability
                with console.status("[dim]Kronos thinking...[/dim]", spinner="dots"):
                    response = await self._ask_kronos(user_input)
                
                # Display response
                console.print(f"[bold cyan]Kronos:[/bold cyan] {response}")
                
                # Store response
                self.history.append({
                    "role": "kronos",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                console.print()
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit properly[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    async def _ask_kronos(self, message: str) -> str:
        """
        Ask the Kronos AI model directly.
        
        This uses Kronos's native language understanding - NOT intent parsing.
        The model itself understands trading concepts and can respond naturally.
        """
        # Create portfolio context (would be real data in production)
        portfolio_context = {
            "cash": 100000.00,
            "positions": {"SPY": 50, "AAPL": 25},
            "total_value": 125000.00,
            "pnl_pct": 0.25,
            "strategies": ["momentum", "mean_reversion"],
            "openai_base_url": self.config.openai_base_url,
            "openai_model": self.config.openai_model
        }
        
        # Ask Kronos using its native conversational ability
        response = self.kronos.chat(message, portfolio_context)
        
        return response
    
    def _print_help(self):
        """Show example conversations."""
        help_text = """
# Talking to Kronos AI

Kronos understands trading naturally. Just talk to it like a knowledgeable trading partner.

## Example conversations:

**Market Analysis:**
- "What do you think about Tesla's momentum right now?"
- "Should I be worried about the VIX spike?"
- "Analyze SPY's chart pattern for me"

**Strategy Questions:**
- "Explain how momentum strategy works"
- "When does mean reversion work best?"
- "Compare my strategies - which performed better?"

**Portfolio Advice:**
- "I'm down 10% on AAPL, what should I do?"
- "Should I diversify more?"
- "What's my risk exposure?"

**Trading Decisions:**
- "Should I enter a position in NVDA?"
- "When will Kronos trade next?"
- "Explain why you sold yesterday"

**Commands:**
- `status` - Show Kronos model status
- `exit` - Quit chat

Just ask naturally. Kronos understands trading concepts natively.
"""
        console.print(Markdown(help_text))
        console.print()
    
    def _print_status(self):
        """Show Kronos model status."""
        status = self.kronos.get_status()
        
        console.print(Panel(
            f"[bold]Kronos AI Model Status[/bold]\n\n"
            f"Mode: [cyan]{status['mode']}[/cyan]\n"
            f"Parameters: [dim]{status['model_params']:,}[/dim]\n"
            f"Conversation turns: {status['conversation_turns']}\n"
            f"Native language: [green]✓ Enabled[/green]\n"
            f"Trading capability: [green]✓ Active[/green]",
            border_style="cyan"
        ))


# Legacy alias for backward compatibility
ChatSession = KronosChatInterface


if __name__ == "__main__":
    # Quick test
    chat = KronosChatInterface()
    
    # Simulate a conversation
    test_messages = [
        "What is momentum trading?",
        "Should I invest in tech stocks right now?",
        "How do you decide when to sell?"
    ]
    
    for msg in test_messages:
        console.print(f"\n[bold green]User:[/bold green] {msg}")
        response = chat._ask_kronos(msg)
        console.print(f"[bold cyan]Kronos:[/bold cyan] {response}")
