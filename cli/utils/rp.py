from rich.console import Console


class RichPrint:
    def __init__(self, console: Console | None = None):
        self._console = console

    @property
    def console(self) -> Console:
        if self._console is None:
            from cli.utils.console import console

            self._console = console
        return self._console

    def success(self, message: str) -> None:
        self.console.print(f"[bold green]\u2713[/bold green] {message}")

    def error(self, message: str) -> None:
        self.console.print(f"[bold red]\u2717[/bold red] {message}")

    def warning(self, message: str) -> None:
        self.console.print(f"[bold yellow]\u26a0[/bold yellow] {message}")

    def info(self, message: str) -> None:
        self.console.print(f"[bold blue]i[/bold blue] {message}")


rp = RichPrint()
