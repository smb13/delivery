from __future__ import annotations

_SEPARATOR = "||"


class Error:
    def __init__(self, code: str, message: str) -> None:
        if code is None or message is None:
            raise ValueError("code and message must not be None")
        self._code = code
        self._message = message

    @staticmethod
    def of(code: str, message: str) -> Error:
        return Error(code, message)

    @property
    def code(self) -> str:
        return self._code

    @property
    def message(self) -> str:
        return self._message

    def serialize(self) -> str:
        return f"{self._code}{_SEPARATOR}{self._message}"

    @staticmethod
    def deserialize(serialized: str) -> Error:
        if serialized == "A non-empty request body is required.":
            from libs.errs.general_errors import GeneralErrors

            return GeneralErrors.value_is_required("serialized")

        parts = serialized.split(_SEPARATOR, 1)
        if len(parts) < 2:
            raise ValueError(f"Invalid error serialization: '{serialized}'")
        return Error(parts[0], parts[1])

    @staticmethod
    def throw_if(error: Error | None) -> None:
        if error is not None:
            from libs.errs.domain_invariant_exception import DomainInvariantException

            raise DomainInvariantException(error)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Error):
            return False
        return self._code == other._code and self._message == other._message

    def __hash__(self) -> int:
        return hash((self._code, self._message))

    def __repr__(self) -> str:
        return f"Error(code={self._code!r}, message={self._message!r})"
