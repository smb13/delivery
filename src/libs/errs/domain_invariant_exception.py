from __future__ import annotations

from libs.errs.error import Error


class DomainInvariantException(Exception):
    def __init__(self, error: Error) -> None:
        super().__init__(f"Domain invariant violated: {error.message}")
        self.error = error
