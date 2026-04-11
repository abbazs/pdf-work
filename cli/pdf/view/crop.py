from rich.panel import Panel

from cli.pdf.models import CropResult
from cli.utils import rp
from cli.utils.console import console


def show_crop_result(result: CropResult) -> None:
    rp.success(f"Cropped {result.pages_cropped} pages (height={result.height})")

    console.print()

    parts = [
        f"[bold]Input:[/bold]  {result.input_path}",
        f"[bold]Output:[/bold] {result.output_path}",
        f"[bold]Crop height:[/bold] {result.height}",
        f"[bold]Total pages:[/bold] {result.total_pages}",
        f"[bold]Pages cropped:[/bold] {result.pages_cropped}",
    ]
    if result.pages_skipped:
        parts.append(f"[bold]Pages skipped (too short):[/bold] {result.pages_skipped}")

    console.print(
        Panel(
            "\n".join(parts),
            title="[bold green]Crop Complete[/bold green]",
            border_style="green",
        )
    )
