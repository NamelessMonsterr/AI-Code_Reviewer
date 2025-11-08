import sys
from src.config.settings import Settings
from rich.console import Console
from rich.table import Table

console = Console()

def validate_configuration() -> Settings:
    """Validate and load configuration"""
    try:
        settings = Settings()
        
        # Display configuration status
        console.print("\n[bold green]✓ Configuration validated successfully![/bold green]\n")
        
        # Show warnings
        warnings = settings.validate_all()
        if warnings:
            console.print("[bold yellow]⚠ Configuration Warnings:[/bold yellow]")
            for warning in warnings:
                console.print(f"  • {warning}")
            console.print()
        
        # Display key settings
        table = Table(title="Active Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Environment", settings.ENVIRONMENT)
        table.add_row("Debug Mode", str(settings.DEBUG))
        table.add_row("Log Level", settings.LOG_LEVEL)
        table.add_row("Port", str(settings.PORT))
        table.add_row("Workers", str(settings.WORKERS))
        table.add_row("OpenAI Model", settings.OPENAI_MODEL)
        table.add_row("Max Files", str(settings.MAX_FILES))
        table.add_row("Redis Cache", "Enabled" if settings.ENABLE_REDIS_CACHE else "Disabled")
        
        console.print(table)
        console.print()
        
        return settings
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Configuration validation failed![/bold red]\n")
        console.print(f"[red]Error: {str(e)}[/red]\n")
        console.print("[yellow]Please check your .env file and ensure all required variables are set.[/yellow]")
        sys.exit(1)


if __name__ == "__main__":
    validate_configuration()
