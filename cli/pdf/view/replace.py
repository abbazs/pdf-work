from rich.panel import Panel
from stepper import Stepper, StepperTheme, StepStatus

from cli.pdf.models import ReplaceResult
from cli.utils import rp
from cli.utils.console import console


def show_replace_result(result: ReplaceResult) -> None:
    if result.total_replacements == 0:
        rp.warning("No matching text found. Output file created with no changes.")
        console.print()
        return

    rp.success(
        f"Replaced {result.total_replacements} occurrence(s) across {result.pages_with_matches} page(s)"
    )

    console.print()

    theme = StepperTheme(
        show_elapsed_time=True,
        show_bar=True,
        bar_width=15,
        max_log_rows=2,
        log_prefix="\u203a",
        completed_style="green bold",
        active_style="yellow bold",
        pending_style="bright_black",
        step_gap=0,
    )

    with Stepper(console=console, theme=theme) as stepper:
        for match in result.matches:
            label = f"Page {match.page_number}"
            step_idx = stepper.add_step(
                label,
                status=StepStatus.ACTIVE,
                step_description="Scanning...",
            )
            stepper.log(step_idx, f"Replaced {match.count} occurrence(s)")
            stepper.set_step_progress(step_idx, 1.0)
            stepper.set_step_status(step_idx, StepStatus.COMPLETED)

    console.print()
    _show_details(result)
    _show_summary(result)


def _show_details(result: ReplaceResult) -> None:
    lines: list[str] = []
    for page_num in result.pages_affected:
        page_matches = [m for m in result.matches if m.page_number == page_num]
        count = sum(m.count for m in page_matches)
        lines.append(f"  [bold]Page {page_num}:[/bold] {count} replacement(s)")

    if lines:
        console.print(
            Panel(
                "\n".join(lines),
                title="[bold]Replacement Details[/bold]",
                border_style="blue",
            )
        )
        console.print()


def _show_summary(result: ReplaceResult) -> None:
    parts = [
        f"[bold]Input:[/bold]  {result.input_path}",
        f"[bold]Output:[/bold] {result.output_path}",
        f"[bold]Pattern:[/bold] {result.pattern!r}",
        f"[bold]Replacement:[/bold] {result.replacement!r}",
        f"[bold]Total replacements:[/bold] {result.total_replacements}",
        f"[bold]Pages affected:[/bold] {result.pages_with_matches} ({', '.join(str(p) for p in result.pages_affected)})",
    ]

    console.print(
        Panel(
            "\n".join(parts),
            title="[bold green]Replace Complete[/bold green]",
            border_style="green",
        )
    )
