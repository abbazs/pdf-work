import re

_SIZE_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*(kb|mb|gb|b)?$", re.IGNORECASE)

_MULTIPLIERS: dict[str, int] = {
    "b": 1,
    "kb": 1024,
    "mb": 1024 * 1024,
    "gb": 1024 * 1024 * 1024,
}


def parse_size(value: str) -> int:
    """Parse a human-readable size string (e.g. '500Kb', '1Mb') into bytes."""
    match = _SIZE_RE.match(value.strip())
    if not match:
        raise ValueError(
            f"Invalid size format: {value!r}. "
            "Expected a number followed by an optional unit (B, KB, MB, GB), e.g. '500Kb' or '1MB'"
        )

    number = float(match.group(1))
    unit = (match.group(2) or "b").lower()

    return int(number * _MULTIPLIERS[unit])


def format_size(bytes_size: int) -> str:
    """Format a byte count into a human-readable string."""
    if bytes_size < 1024:
        return f"{bytes_size}B"
    if bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f}KB"
    if bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f}MB"
    return f"{bytes_size / (1024 * 1024 * 1024):.1f}GB"
