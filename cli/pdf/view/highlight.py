"""Rich terminal output for the highlight command."""

from rich.panel import Panel
from stepper import Stepper, StepperTheme, StepStatus

from cli.pdf.models import HighlightResult
from cli.utils import rp
from cli.utils.console import console


def show_highlight_result(
    result: HighlightResult,
    mask_line: bool = False,
    insensitive: bool = False,
    color: str = "yellow",
    opacity: float = 0.4,
) -> None:
    """Render the result of a highlight operation to the terminal.

    Displays an options summary line, a per-pattern stepper showing match
    counts, a details panel listing matches by page, and a summary panel.
    """
    mode = "whole-line" if mask_line else "exact-text"
    options = [f"mode={mode}", f"color={color!r}", f"opacity={opacity}"]
    if insensitive:
        options.append("case-insensitive")
    rp.info(f"Highlighting with: {', '.join(options)}")

    if result.total_highlights == 0:
        rp.warning("No matching text found. Output file created with no changes.")
        console.print()
        return

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

    pattern_counts: dict[str, int] = {}
    for match in result.matches:
        pattern_counts[match.pattern] = pattern_counts.get(match.pattern, 0) + match.count

    with Stepper(console=console, theme=theme) as stepper:
        for pattern in result.patterns:
            count = pattern_counts.get(pattern, 0)
            label = repr(pattern)
            step_idx = stepper.add_step(
                label,
                status=StepStatus.ACTIVE,
                step_description="Searching...",
            )

            if count > 0:
                stepper.log(
                    step_idx,
                    f"Found {count} occurrence{'s' if count != 1 else ''}"
                    + (" — line highlighted" if mask_line else ""),
                )
                stepper.set_step_progress(step_idx, 1.0)
                stepper.set_step_status(step_idx, StepStatus.COMPLETED)
            else:
                stepper.log(step_idx, "No matches found")
                stepper.set_step_progress(step_idx, 1.0)
                stepper.set_step_status(step_idx, StepStatus.COMPLETED)

    console.print()
    _show_details(result)
    _show_summary(result, mask_line=mask_line, insensitive=insensitive, color=color, opacity=opacity)


def _show_details(result: HighlightResult) -> None:
    """Render a panel listing per-page match details."""
    lines: list[str] = []
    for page_num in result.pages_affected:
        page_matches = [m for m in result.matches if m.page_number == page_num]
        pattern_parts = [f"[yellow]{m.pattern!r}[/yellow] ({m.count})" for m in page_matches]
        lines.append(f"  [bold]Page {page_num}:[/bold]  {', '.join(pattern_parts)}")

    if lines:
        console.print(
            Panel(
                "\n".join(lines),
                title="[bold]Highlight Details[/bold]",
                border_style="yellow",
            )
        )
        console.print()


def _show_summary(
    result: HighlightResult,
    mask_line: bool = False,
    insensitive: bool = False,
    color: str = "yellow",
    opacity: float = 0.4,
) -> None:
    """Render the final summary panel."""
    options: list[str] = [f"color={color!r}", f"opacity={opacity}"]
    if mask_line:
        options.append("line-mode")
    if insensitive:
        options.append("case-insensitive")
    option_str = f" [dim]({', '.join(options)})[/dim]" if options else ""

    parts = [
        f"[bold]Input:[/bold]  {result.input_path}",
        f"[bold]Output:[/bold] {result.output_path}",
        f"[bold]Patterns:[/bold] {', '.join(repr(p) for p in result.patterns)}",
        f"[bold]Total highlights:[/bold] {result.total_highlights}",
        f"[bold]Pages affected:[/bold] {result.pages_with_matches}"
        f" ({', '.join(str(p) for p in result.pages_affected)})",
    ]

    console.print(
        Panel(
            "\n".join(parts),
            title=f"[bold green]Highlight Complete{option_str}[/bold green]",
            border_style="green",
        )
    )
