from rich.panel import Panel
from stepper import Stepper, StepperTheme, StepStatus

from cli.pdf.models import MaskResult
from cli.utils import rp
from cli.utils.console import console


def show_mask_result(
    result: MaskResult,
    mask_line: bool = False,
    insensitive: bool = False,
    color: str = "black",
) -> None:
    if result.total_redactions == 0:
        rp.warning("No matching text found. Output file created with no changes.")
        console.print()
        return

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
                stepper.log(step_idx, f"Found {count} occurrence{'s' if count != 1 else ''}")
                stepper.set_step_progress(step_idx, 1.0)
                stepper.set_step_status(step_idx, StepStatus.COMPLETED)
            else:
                stepper.log(step_idx, "No matches found")
                stepper.set_step_progress(step_idx, 1.0)
                stepper.set_step_status(step_idx, StepStatus.COMPLETED)

    console.print()
    _show_details(result)
    _show_summary(result, mask_line=mask_line, insensitive=insensitive, color=color)


def _show_details(result: MaskResult) -> None:
    lines: list[str] = []
    for page_num in result.pages_affected:
        page_matches = [m for m in result.matches if m.page_number == page_num]
        pattern_parts = [f"[yellow]{m.pattern!r}[/yellow] ({m.count})" for m in page_matches]
        lines.append(f"  [bold]Page {page_num}:[/bold]  {', '.join(pattern_parts)}")

    if lines:
        console.print(
            Panel(
                "\n".join(lines),
                title="[bold]Redaction Details[/bold]",
                border_style="red",
            )
        )
        console.print()


def _show_summary(
    result: MaskResult,
    mask_line: bool = False,
    insensitive: bool = False,
    color: str = "black",
) -> None:
    options: list[str] = [f"color={color!r}"]
    if mask_line:
        options.append("line-mode")
    if insensitive:
        options.append("case-insensitive")
    option_str = f" [dim]({', '.join(options)})[/dim]" if options else ""

    parts = [
        f"[bold]Input:[/bold]  {result.input_path}",
        f"[bold]Output:[/bold] {result.output_path}",
        f"[bold]Patterns:[/bold] {', '.join(repr(p) for p in result.patterns)}",
        f"[bold]Total redactions:[/bold] {result.total_redactions}",
        f"[bold]Pages affected:[/bold] {result.pages_with_matches} ({', '.join(str(p) for p in result.pages_affected)})",
    ]

    console.print(
        Panel(
            "\n".join(parts),
            title=f"[bold green]Mask Complete{option_str}[/bold green]",
            border_style="green",
        )
    )
