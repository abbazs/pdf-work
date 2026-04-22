from rich.panel import Panel
from stepper import Stepper, StepperTheme, StepStatus

from cli.pdf.models import ExtractedPage, ExtractResult
from cli.pdf.utils import format_size
from cli.utils import rp
from cli.utils.console import console


def show_extract_result(result: ExtractResult) -> None:
    if not result.extracted:
        rp.warning("No pages were extracted. Check that page numbers are valid.")
        console.print()
        return

    rp.success(
        f"Extracted {result.pages_extracted} page(s) from {result.total_pages}-page PDF"
    )

    console.print()

    theme = StepperTheme(
        show_elapsed_time=True,
        show_bar=True,
        bar_width=15,
        max_log_rows=3,
        log_prefix="\u203a",
        completed_style="green bold",
        active_style="yellow bold",
        pending_style="bright_black",
        step_gap=0,
    )

    with Stepper(console=console, theme=theme) as stepper:
        for page in result.extracted:
            label = f"Page {page.page_number}"
            step_idx = stepper.add_step(
                label,
                status=StepStatus.ACTIVE,
                step_description="Extracting...",
            )

            size_info = _format_size_info(page)
            stepper.log(step_idx, f"{size_info} → {page.output_path}")
            stepper.set_step_progress(step_idx, 1.0)
            stepper.set_step_status(step_idx, StepStatus.COMPLETED)

    console.print()
    _show_summary(result)


def _format_size_info(page: ExtractedPage) -> str:
    size_str = format_size(page.file_size)
    if page.compressed:
        if page.size_limit and page.file_size > page.size_limit:
            return f"{size_str} [red](exceeds {format_size(page.size_limit)} limit)[/red]"
        return f"{size_str} [cyan](compressed)[/cyan]"
    return size_str


def _show_summary(result: ExtractResult) -> None:
    parts: list[str] = [
        f"[bold]Input:[/bold]  {result.input_path}",
        f"[bold]Total pages:[/bold] {result.total_pages}",
        f"[bold]Extracted:[/bold] {result.pages_extracted} page(s)",
    ]

    if result.skipped_pages:
        parts.append(
            f"[bold]Skipped:[/bold] {', '.join(str(p) for p in result.skipped_pages)} (out of range)"
        )

    size_limit = next((p.size_limit for p in result.extracted if p.size_limit), None)
    if size_limit:
        parts.append(f"[bold]Size limit:[/bold] {format_size(size_limit)} per page")

    console.print(
        Panel(
            "\n".join(parts),
            title="[bold green]Extract Complete[/bold green]",
            border_style="green",
        )
    )
