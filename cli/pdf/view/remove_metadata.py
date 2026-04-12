from rich.panel import Panel

from cli.pdf.models import MetadataResult
from cli.utils import rp
from cli.utils.console import console


def show_metadata_result(result: MetadataResult) -> None:
    """Display the outcome of a metadata removal operation."""
    if result.fields_cleared:
        rp.success(f"Metadata stripped ({len(result.fields_cleared)} field(s) cleared)")
    else:
        rp.warning("No metadata found — file saved without changes")

    console.print()

    cleared_display = (
        ", ".join(result.fields_cleared) if result.fields_cleared else "[dim]none[/dim]"
    )

    parts = [
        f"[bold]Input:[/bold]   {result.input_path}",
        f"[bold]Output:[/bold]  {result.output_path}",
        f"[bold]Pages:[/bold]   {result.total_pages}",
        f"[bold]Cleared:[/bold] {cleared_display}",
    ]

    status = (
        "[bold green]Metadata Removed[/bold green]"
        if result.fields_cleared
        else "[bold yellow]No Metadata Found[/bold yellow]"
    )
    console.print(Panel("\n".join(parts), title=status, border_style="green"))
