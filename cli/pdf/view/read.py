from rich.panel import Panel
from rich.text import Text
from stepper import Stepper, StepperTheme, StepStatus

from cli.pdf.models import PdfReadResult
from cli.utils import rp
from cli.utils.console import console


def show_pdf_text(result: PdfReadResult) -> None:
    if not result.pages:
        rp.warning("No pages found in PDF.")
        return

    theme = StepperTheme(
        show_elapsed_time=True,
        show_bar=True,
        bar_width=15,
        max_log_rows=2,
        log_prefix="\u203a",
        completed_style="green bold",
        active_style="cyan bold",
        pending_style="bright_black",
        step_gap=0,
    )

    with Stepper(console=console, theme=theme) as stepper:
        for page in result.pages:
            label = f"Page {page.page_number}"
            step_idx = stepper.add_step(
                label,
                status=StepStatus.ACTIVE,
                step_description=f"{page.char_count} chars",
            )

            if page.has_text:
                stepper.log(step_idx, f"Extracted {page.char_count} characters")
                stepper.set_step_progress(step_idx, 1.0)
                stepper.set_step_status(step_idx, StepStatus.COMPLETED)
            else:
                stepper.log(step_idx, "No extractable text on this page")
                stepper.set_step_progress(step_idx, 1.0)
                stepper.set_step_status(step_idx, StepStatus.COMPLETED)

    console.print()

    for page in result.pages:
        if not page.has_text:
            continue

        header = Text(f"Page {page.page_number}", style="bold cyan")
        content = Text(page.text)
        panel = Panel(content, title=header, border_style="cyan", expand=False)
        console.print(panel)
        console.print()

    _show_summary(result)


def _show_summary(result: PdfReadResult) -> None:
    parts = [
        f"[bold]File:[/bold] {result.file_path}",
        f"[bold]Total pages:[/bold] {result.total_pages}",
        f"[bold]Pages with text:[/bold] {result.pages_with_text}",
        f"[bold]Total characters:[/bold] {result.total_chars:,}",
    ]
    if result.empty_pages:
        parts.append(f"[bold]Empty pages:[/bold] {', '.join(str(p) for p in result.empty_pages)}")

    panel = Panel("\n".join(parts), title="[bold]Summary[/bold]", border_style="green")
    console.print(panel)
