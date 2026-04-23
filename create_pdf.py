#!/usr/bin/env python3
"""Generate PDF overview for Kronos Trading Agent."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime

pdf_path = '/tmp/kronos_project/Kronos_Trading_Agent_Overview.pdf'
doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
elements = []
styles = getSampleStyleSheet()

# Title
elements.append(Paragraph('KRONOS TRADING AGENT', styles['Heading1']))
elements.append(Paragraph('Technical Overview & Implementation Guide', styles['Heading3']))
elements.append(Paragraph(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', styles['Normal']))
elements.append(Spacer(1, 0.3*inch))

# Summary
elements.append(Paragraph('Executive Summary', styles['Heading2']))
elements.append(Paragraph('The <b>Kronos Trading Agent</b> is an autonomous AI trading system combining 4 phases: predictive forecasting, RL-based position sizing, event-driven execution, and comprehensive validation.', styles['BodyText']))
elements.append(Paragraph('<b>Status:</b> All 4 phases implemented and tested ✓<br/><b>Total Codebase:</b> ~56KB across 5 Python modules<br/><b>Test Result:</b> All phases execute successfully', styles['BodyText']))
elements.append(Spacer(1, 0.2*inch))

# Architecture Table
arch_data = [
    ['Phase', 'Component', 'Purpose'],
    ['1', 'Kronos Validator', 'Gatekeeper - Out-of-sample validation'],
    ['2', 'RL Trading Agent', 'GRPO-based position sizing'],
    ['3', 'Trading Harness', 'Event-driven execution'],
    ['4', 'Validation Framework', 'Backtesting & benchmarking']
]
arch_table = Table(arch_data, colWidths=[0.5*inch, 2*inch, 3.5*inch])
arch_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
]))
elements.append(arch_table)
elements.append(Spacer(1, 0.3*inch))

# Phase Details
elements.append(Paragraph('Phase 1: Kronos Validator', styles['Heading2']))
elements.append(Paragraph('Validates Kronos predictions on 2022-2024 data. If R² < 0.1, pipeline aborts. Features OpenBB integration, synthetic fallback, R²/direction metrics.', styles['BodyText']))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph('Phase 2: RL Trading Agent', styles['Heading2']))
elements.append(Paragraph('GRPO-based RL policy. State: [kronos_pred, volatility, trend, position]. Action: Position sizing (0-1). Reward: Sortino Ratio. PyTorch MLP network.', styles['BodyText']))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph('Phase 3: Trading Harness', styles['Heading2']))
elements.append(Paragraph('Event-driven execution with state machine: IDLE → ANALYZE → DECIDE → EXECUTE → LOG. Risk limits: 2% daily loss, 10% max drawdown. CLI commands: /status, /trade, /start.', styles['BodyText']))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph('Phase 4: Validation Framework', styles['Heading2']))
elements.append(Paragraph('Transaction costs (0.05% + 0.1% slippage), walk-forward analysis, stress tests (COVID 2020, 2008 crisis, Flash Crash), benchmark vs Buy & Hold.', styles['BodyText']))
elements.append(Spacer(1, 0.3*inch))

# Usage
elements.append(Paragraph('Usage', styles['Heading2']))
usage = """
<b>Run Individual Phases:</b><br/>
python main.py validate      # Phase 1<br/>
python main.py train         # Phase 2<br/>
python main.py harness       # Phase 3<br/>
python main.py validate-full # Phase 4<br/><br/>
<b>Run Full Pipeline:</b><br/>
python main.py run
"""
elements.append(Paragraph(usage, styles['BodyText']))
elements.append(Spacer(1, 0.2*inch))

elements.append(Paragraph('— Kronos Trading Agent v1.0 —', styles['Normal']))

doc.build(elements)
print(f'✅ PDF created: {pdf_path}')
