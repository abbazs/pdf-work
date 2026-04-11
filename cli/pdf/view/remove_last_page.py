from rich.panel import Panel

from cli.pdf.models import PageRemoveResult
from cli.utils import rp
from cli.utils.console import console


def show_remove_result(result: PageRemoveResult) -> None:
    rp.success(f"Removed page {result.removed_page} from PDF")

    console.print()

    parts = [
        f"[bold]Input:[/bold]  {result.input_path}",
        f"[bold]Output:[/bold] {result.output_path}",
        f"[bold]Original pages:[/bold] {result.original_pages}",
        f"[bold]New pages:[/bold] {result.new_pages}",
        f"[bold]Removed page:[/bold] {result.removed_page}",
    ]

    console.print(
        Panel(
            "\n".join(parts),
            title="[bold green]Page Removed[/bold green]",
            border_style="green",
        )
    )
