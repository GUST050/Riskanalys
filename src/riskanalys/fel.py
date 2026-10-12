"""Gemensam basklass för fel som visas för användaren."""


class RiskanalysFel(Exception):
    """Ett fel som användaren kan åtgärda. Kommandoraden visar meddelandet utan stackspårning."""
