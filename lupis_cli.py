#!/usr/bin/env python3
"""
LUPIS CLI - Command Line Interface for Loop-Updating Perception-Intelligence Synthesiser
Provides management, monitoring, and control capabilities for LUPIS
Version: 2025-06-17
"""

import asyncio
import click
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import sys
import subprocess

from config.lupis_config import get_lupis_config, LUPISConfig
from agents.lupis_orchestrator import LUPISOrchestrator, create_lupis_orchestrator
from agents.lupis_arsenal import UCoinLedger


class LUPISCLIContext:
    """CLI context for sharing state between commands"""
    
    def __init__(self):
        self.config: Optional[LUPISConfig] = None
        self.orchestrator: Optional[LUPISOrchestrator] = None
        self.debug = False


pass_context = click.make_pass_decorator(LUPISCLIContext, ensure=True)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--environment', default='development', help='Environment (development/production)')
@click.option('--config-file', type=click.Path(exists=True), help='Custom configuration file')
@pass_context
def cli(ctx: LUPISCLIContext, debug: bool, environment: str, config_file: Optional[str]):
    """LUPIS - Loop-Updating Perception-Intelligence Synthesiser CLI"""
    ctx.debug = debug
    
    # Setup logging
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    try:
        if config_file:
            # TODO: Implement config file loading
            ctx.config = get_lupis_config(environment)
        else:
            ctx.config = get_lupis_config(environment)
        
        click.echo(f"🤖 LUPIS v{ctx.config.version} - Environment: {environment}")
        
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}", err=True)
        sys.exit(1)


@cli.group()
@pass_context
def orchestrator(ctx: LUPISCLIContext):
    """Orchestrator management commands"""
    pass


@orchestrator.command()
@click.option('--background', is_flag=True, help='Run in background')
@pass_context
def start(ctx: LUPISCLIContext, background: bool):
    """Start the LUPIS orchestrator"""
    click.echo("🚀 Starting LUPIS orchestrator...")
    
    try:
        ctx.orchestrator = create_lupis_orchestrator(ctx.config.environment)
        
        if background:
            # TODO: Implement proper daemon mode
            click.echo("⚠️  Background mode not yet implemented - running in foreground")
        
        async def run_orchestrator():
            try:
                await ctx.orchestrator.start()
            except KeyboardInterrupt:
                click.echo("\n🛑 Stopping LUPIS orchestrator...")
                await ctx.orchestrator.stop()
        
        asyncio.run(run_orchestrator())
        
    except Exception as e:
        click.echo(f"❌ Error starting orchestrator: {e}", err=True)
        sys.exit(1)


@orchestrator.command()
@pass_context
def stop(ctx: LUPISCLIContext):
    """Stop the LUPIS orchestrator"""
    click.echo("🛑 Stopping LUPIS orchestrator...")
    
    if ctx.orchestrator:
        asyncio.run(ctx.orchestrator.stop())
        click.echo("✅ Orchestrator stopped")
    else:
        click.echo("⚠️  No running orchestrator found")


@orchestrator.command()
@pass_context
def status(ctx: LUPISCLIContext):
    """Show orchestrator status"""
    if not ctx.orchestrator:
        # Try to connect to running instance
        click.echo("📊 Checking orchestrator status...")
        click.echo("⚠️  Status checking not yet implemented")
        return
    
    stats = ctx.orchestrator.get_statistics()
    
    click.echo("📊 LUPIS Orchestrator Status")
    click.echo("=" * 40)
    click.echo(f"Running: {'✅ Yes' if stats['running'] else '❌ No'}")
    click.echo(f"Uptime: {stats['uptime_seconds']:.1f} seconds")
    click.echo(f"Events processed: {stats['processed_events']}")
    click.echo(f"Tickets created: {stats['optimization_tickets_created']}")
    click.echo(f"Consecutive failures: {stats['consecutive_failures']}")
    click.echo(f"Config version: {stats['config_version']}")


@cli.group()
@pass_context
def ucoin(ctx: LUPISCLIContext):
    """U-Coin economy management"""
    pass


@ucoin.command()
@pass_context
def balance(ctx: LUPISCLIContext):
    """Show current U-Coin balance"""
    try:
        ledger = UCoinLedger(ctx.config.ucoin)
        current_balance = ledger.check_balance()
        
        click.echo("💰 U-Coin Balance")
        click.echo("=" * 20)
        click.echo(f"Current Balance: {current_balance} tokens")
        click.echo(f"Minimum for Auto: {ctx.config.ucoin.min_balance_for_auto} tokens")
        click.echo(f"Maximum Balance: {ctx.config.ucoin.max_balance} tokens")
        
        # Show recent transactions
        click.echo("\n📜 Recent Transactions:")
        transactions = ledger.get_transaction_history(limit=5)
        for tx in transactions:
            amount_str = f"+{tx.amount}" if tx.transaction_type.value in ['credit', 'grant'] else f"-{tx.amount}"
            click.echo(f"  {tx.timestamp.strftime('%H:%M:%S')} | {amount_str:>6} | {tx.reason}")
        
    except Exception as e:
        click.echo(f"❌ Error checking balance: {e}", err=True)


@ucoin.command()
@click.argument('amount', type=int)
@click.argument('reason')
@pass_context
def grant(ctx: LUPISCLIContext, amount: int, reason: str):
    """Grant U-Coins (admin operation)"""
    try:
        ledger = UCoinLedger(ctx.config.ucoin)
        ledger.credit(amount, f"manual_grant: {reason}", {'admin': True})
        
        new_balance = ledger.check_balance()
        click.echo(f"✅ Granted {amount} U-Coins. New balance: {new_balance}")
        
    except Exception as e:
        click.echo(f"❌ Error granting tokens: {e}", err=True)


@ucoin.command()
@pass_context
def history(ctx: LUPISCLIContext):
    """Show U-Coin transaction history"""
    try:
        ledger = UCoinLedger(ctx.config.ucoin)
        transactions = ledger.get_transaction_history(limit=20)
        
        click.echo("📜 U-Coin Transaction History")
        click.echo("=" * 60)
        click.echo(f"{'Time':<19} | {'Type':<8} | {'Amount':<8} | {'Balance':<8} | {'Reason'}")
        click.echo("-" * 60)
        
        for tx in transactions:
            amount_str = f"+{tx.amount}" if tx.transaction_type.value in ['credit', 'grant'] else f"-{tx.amount}"
            click.echo(f"{tx.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                      f"{tx.transaction_type.value:<8} | "
                      f"{amount_str:>8} | "
                      f"{tx.balance_after:>8} | "
                      f"{tx.reason}")
        
    except Exception as e:
        click.echo(f"❌ Error retrieving history: {e}", err=True)


@cli.group()
@pass_context
def metrics(ctx: LUPISCLIContext):
    """Metrics and monitoring commands"""
    pass


@metrics.command()
@pass_context
def show(ctx: LUPISCLIContext):
    """Show current system metrics"""
    click.echo("📈 System Metrics")
    click.echo("=" * 30)
    
    # TODO: Implement actual metrics collection
    click.echo("⚠️  Metrics collection not yet implemented")
    click.echo("This will show:")
    click.echo("  - Capture latency")
    click.echo("  - Throughput")
    click.echo("  - Context accuracy")
    click.echo("  - Error rates")


@metrics.command()
@click.argument('metric')
@click.argument('value', type=float)
@click.option('--source', default='manual')
@pass_context
def submit(ctx: LUPISCLIContext, metric: str, value: float, source: str):
    """Submit a metric event to LUPIS"""
    if not ctx.orchestrator:
        click.echo("❌ Orchestrator not running. Start it first with 'lupis orchestrator start'")
        return
    
    async def submit_metric():
        await ctx.orchestrator.submit_metric_event(metric, value, source)
    
    try:
        asyncio.run(submit_metric())
        click.echo(f"✅ Submitted metric: {metric} = {value} (source: {source})")
    except Exception as e:
        click.echo(f"❌ Error submitting metric: {e}", err=True)


@cli.group()
@pass_context
def audit(ctx: LUPISCLIContext):
    """Audit trail commands"""
    pass


@audit.command()
@click.option('--limit', default=10, help='Number of entries to show')
@pass_context
def show(ctx: LUPISCLIContext, limit: int):
    """Show recent audit entries"""
    audit_file = Path(ctx.config.audit.audit_path) / ctx.config.audit.audit_file
    
    if not audit_file.exists():
        click.echo("📋 No audit entries found")
        return
    
    try:
        with open(audit_file, 'r') as f:
            content = f.read()
        
        # Parse YAML entries
        entries = []
        for doc in yaml.safe_load_all(content):
            if doc:
                entries.append(doc)
        
        # Show recent entries
        recent_entries = entries[-limit:] if entries else []
        
        click.echo(f"📋 Recent Audit Entries (showing {len(recent_entries)})")
        click.echo("=" * 50)
        
        for entry in reversed(recent_entries):
            timestamp = entry.get('timestamp', 'Unknown')
            action = entry.get('action', 'Unknown')
            roi_score = entry.get('roi_score', 0.0)
            urgency = entry.get('urgency', 0.0)
            
            click.echo(f"🕐 {timestamp}")
            click.echo(f"🎯 Action: {action}")
            click.echo(f"💡 ROI: {roi_score:.3f} | Urgency: {urgency:.3f}")
            click.echo(f"📝 {entry.get('reasoning', 'No reasoning provided')}")
            if entry.get('outcome'):
                click.echo(f"✅ Outcome: {entry['outcome']}")
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error reading audit trail: {e}", err=True)


@audit.command()
@pass_context
def verify(ctx: LUPISCLIContext):
    """Verify audit trail integrity"""
    if not ctx.config.audit.chain_enabled:
        click.echo("⚠️  Audit chain not enabled in configuration")
        return
    
    try:
        from agents.lupis_arsenal import AuditSink
        
        audit_sink = AuditSink(ctx.config.audit)
        verification = audit_sink.verify_chain_integrity()
        
        click.echo("🔍 Audit Chain Verification")
        click.echo("=" * 30)
        click.echo(f"Status: {'✅ Valid' if verification['valid'] else '❌ Invalid'}")
        click.echo(f"Total entries: {verification['total_entries']}")
        click.echo(f"Verified entries: {verification['verified_entries']}")
        click.echo(f"Broken links: {len(verification.get('broken_links', []))}")
        
        if verification.get('broken_links'):
            click.echo("\n❌ Broken Chain Links:")
            for link in verification['broken_links']:
                click.echo(f"  Entry: {link['entry_id']}")
                click.echo(f"  Expected: {link['expected_previous'][:16]}...")
                click.echo(f"  Actual: {link['actual_previous'][:16]}...")
        
    except Exception as e:
        click.echo(f"❌ Error verifying audit chain: {e}", err=True)


@cli.group()
@pass_context
def config(ctx: LUPISCLIContext):
    """Configuration management"""
    pass


@config.command()
@pass_context
def show(ctx: LUPISCLIContext):
    """Show current configuration"""
    click.echo("⚙️  LUPIS Configuration")
    click.echo("=" * 40)
    
    config_dict = ctx.config.to_dict()
    
    # Show key configuration sections
    sections = ['ucoin', 'sensors', 'analyzers', 'actuators']
    
    for section in sections:
        if section in config_dict:
            click.echo(f"\n📂 {section.upper()}:")
            section_data = config_dict[section]
            for key, value in section_data.items():
                if not key.startswith('_'):  # Skip private fields
                    click.echo(f"  {key}: {value}")


@config.command()
@click.option('--output', type=click.Path(), help='Output file path')
@pass_context
def export(ctx: LUPISCLIContext, output: Optional[str]):
    """Export configuration to file"""
    config_dict = ctx.config.to_dict()
    
    if output:
        output_path = Path(output)
        with open(output_path, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
        click.echo(f"✅ Configuration exported to {output_path}")
    else:
        click.echo(json.dumps(config_dict, indent=2, default=str))


@config.command()
@pass_context
def validate(ctx: LUPISCLIContext):
    """Validate current configuration"""
    click.echo("🔍 Validating configuration...")
    
    errors = ctx.config.validate()
    
    if errors:
        click.echo("❌ Configuration validation failed:")
        for error in errors:
            click.echo(f"  • {error}")
        sys.exit(1)
    else:
        click.echo("✅ Configuration is valid")


@cli.command()
@click.option('--check-deps', is_flag=True, help='Check dependencies')
@pass_context
def doctor(ctx: LUPISCLIContext, check_deps: bool):
    """Run LUPIS system health check"""
    click.echo("🏥 LUPIS System Health Check")
    click.echo("=" * 35)
    
    # Check configuration
    click.echo("🔍 Checking configuration...")
    config_errors = ctx.config.validate()
    if config_errors:
        click.echo(f"❌ Configuration errors: {len(config_errors)}")
        for error in config_errors:
            click.echo(f"  • {error}")
    else:
        click.echo("✅ Configuration valid")
    
    # Check file system permissions
    click.echo("\n📁 Checking file system...")
    audit_path = Path(ctx.config.audit.audit_path)
    try:
        audit_path.mkdir(parents=True, exist_ok=True)
        test_file = audit_path / ".lupis_test"
        test_file.write_text("test")
        test_file.unlink()
        click.echo("✅ File system permissions OK")
    except Exception as e:
        click.echo(f"❌ File system error: {e}")
    
    # Check dependencies
    if check_deps:
        click.echo("\n📦 Checking dependencies...")
        deps = ['zmq', 'yaml', 'requests', 'github']
        
        for dep in deps:
            try:
                __import__(dep)
                click.echo(f"✅ {dep}")
            except ImportError:
                click.echo(f"❌ {dep} (missing)")
    
    # Check GitHub integration
    if ctx.config.integration.github_enabled:
        click.echo("\n🐙 Checking GitHub integration...")
        if ctx.config.actuators.github_api_token:
            click.echo("✅ GitHub token configured")
        else:
            click.echo("❌ GitHub token missing")
    
    click.echo("\n🏥 Health check complete")


@cli.command()
@pass_context
def version(ctx: LUPISCLIContext):
    """Show LUPIS version information"""
    click.echo(f"🤖 LUPIS v{ctx.config.version}")
    click.echo(f"Environment: {ctx.config.environment}")
    click.echo(f"Debug mode: {'Enabled' if ctx.config.debug_mode else 'Disabled'}")
    click.echo(f"Autonomous mode: {'Enabled' if ctx.config.autonomous_mode else 'Disabled'}")


if __name__ == '__main__':
    cli()