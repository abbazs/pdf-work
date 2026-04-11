from rich.panel import Panel

from cli.pdf.models import PasswordResult
from cli.utils import rp
from cli.utils.console import console


def show_password_result(result: PasswordResult) -> None:
    if result.was_encrypted:
        rp.success(f"PDF decrypted successfully ({result.total_pages} pages)")
    else:
        rp.warning("PDF was not encrypted — file copied without changes")

    console.print()

    parts = [
        f"[bold]Input:[/bold]  {result.input_path}",
        f"[bold]Output:[/bold] {result.output_path}",
        f"[bold]Encrypted:[/bold] {'Yes' if result.was_encrypted else 'No'}",
        f"[bold]Total pages:[/bold] {result.total_pages}",
    ]

    status = (
        "[bold green]Decrypted[/bold green]"
        if result.was_encrypted
        else "[bold yellow]Copied (not encrypted)[/bold yellow]"
    )
    console.print(Panel("\n".join(parts), title=status, border_style="green"))
