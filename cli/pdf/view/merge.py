from rich.panel import Panel
from stepper import Stepper, StepperTheme, StepStatus

from cli.pdf.models import MergeResult
from cli.utils import rp
from cli.utils.console import console


def show_merge_result(result: MergeResult) -> None:
    rp.success(f"Merged {len(result.input_files)} files into {result.total_pages} pages")

    console.print()

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
        for f in result.input_files:
            step_idx = stepper.add_step(
                f,
                status=StepStatus.ACTIVE,
                step_description="Processing...",
            )
            stepper.log(step_idx, "Merged")
            stepper.set_step_progress(step_idx, 1.0)
            stepper.set_step_status(step_idx, StepStatus.COMPLETED)

    console.print()

    parts = [
        f"[bold]Output:[/bold] {result.output_path}",
        f"[bold]Files merged:[/bold] {len(result.input_files)}",
        f"[bold]Total pages:[/bold] {result.total_pages}",
    ]
    if result.skipped_files:
        parts.append(f"[bold]Skipped files:[/bold] {', '.join(result.skipped_files)}")

    console.print(
        Panel(
            "\n".join(parts),
            title="[bold green]Merge Complete[/bold green]",
            border_style="green",
        )
    )
