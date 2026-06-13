from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any


@dataclass(frozen=True)
class SolveResult:
    status: str
    model: dict[str, Any] = field(default_factory=dict)
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"status": self.status}
        if self.status == "unknown" and self.reason:
            data["reason"] = self.reason
        data["model"] = self.model
        return data


def model_to_python(model: object | None) -> dict[str, Any]:
    if model is None:
        return {}

    values: dict[str, Any] = {}
    for decl in sorted(model.decls(), key=lambda item: item.name()):
        interp = model[decl]
        if interp is not None:
            values[decl.name()] = z3_value_to_python(interp)
    return values


def z3_value_to_python(value: Any) -> Any:
    import z3

    if z3.is_true(value):
        return True
    if z3.is_false(value):
        return False
    if z3.is_int_value(value):
        return value.as_long()
    if z3.is_rational_value(value):
        return _rational_to_python(value)
    if z3.is_bv_value(value):
        width = value.size()
        digits = max(1, (width + 3) // 4)
        return {
            "value": value.as_long(),
            "hex": f"0x{value.as_long():0{digits}x}",
            "width": width,
        }
    if isinstance(value, z3.ArrayRef):
        return _array_to_python(value)
    return str(value)


def _rational_to_python(value: Any) -> int | float:
    fraction = Fraction(value.numerator_as_long(), value.denominator_as_long())
    if fraction.denominator == 1:
        return fraction.numerator
    return float(fraction)


def _array_to_python(value: Any) -> dict[str, Any]:
    import z3

    default = None
    entries: list[dict[str, Any]] = []
    current = value

    while z3.is_store(current):
        entries.append(
            {
                "index": z3_value_to_python(current.arg(1)),
                "value": z3_value_to_python(current.arg(2)),
            }
        )
        current = current.arg(0)

    if z3.is_const_array(current):
        default = z3_value_to_python(current.arg(0))
    else:
        default = str(current)

    entries.reverse()
    return {"entries": entries, "default": default}
