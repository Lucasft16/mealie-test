"""
Testes unitários de `clean_int` (mealie/services/scraper/cleaner.py).
Decisões:
    D1  val is None or isinstance(val, int)    (A or B)
    D2  not filtered_val
    D3  min is None or max is None             (A or B)
    D4  not (min <= val <= max)                (not (A and B))
"""

import pytest

from mealie.services.scraper.cleaner import clean_int

# Caixa-preta: particionamento de equivalência (classes válidas)
VALID_CASES = [
    pytest.param("3", 1, 5, 3, id="string numérica no intervalo"),
    pytest.param("Nota: 4 estrelas", 1, 5, 4, id="string alfanumérica"),
    pytest.param("42", None, None, 42, id="sem limites"),
    # Análise de valor limite (min=1, max=5)
    pytest.param("1", 1, 5, 1, id="bva: val = min"),
    pytest.param("2", 1, 5, 2, id="bva: val = min + 1"),
    pytest.param("4", 1, 5, 4, id="bva: val = max - 1"),
    pytest.param("5", 1, 5, 5, id="bva: val = max"),
]


@pytest.mark.parametrize(("val", "min_val", "max_val", "expected"), VALID_CASES)
def test_valid_clean_int(val: str | int | None, min_val: int | None, max_val: int | None, expected: int) -> None:
    assert clean_int(val, min=min_val, max=max_val) == expected


# Caixa-preta: classes inválidas
INVALID_CASES = [
    pytest.param(None, 1, 5, id="none"),
    pytest.param("", 1, 5, id="vazia"),
    pytest.param("abc", 1, 5, id="sem dígitos"),
    # Análise de valor limite: fora do intervalo (D4)
    pytest.param("0", 1, 5, id="bva: val = min - 1"),
    pytest.param("6", 1, 5, id="bva: val = max + 1"),
]


@pytest.mark.parametrize(("val", "min_val", "max_val"), INVALID_CASES)
def test_invalid_inputs_return_none(val: str | int | None, min_val: int | None, max_val: int | None) -> None:
    assert clean_int(val, min=min_val, max=max_val) is None


# Caixa-branca: MC/DC
MCDC_D1_CASES = [
    pytest.param(None, 1, 5, None, id="T1: A=V B=F"),
    pytest.param(10, 1, 5, 10, id="T2: A=F B=V"),
    pytest.param("3", 1, 5, 3, id="T3: A=F B=F"),
]


@pytest.mark.parametrize(("val", "min_val", "max_val", "expected"), MCDC_D1_CASES)
def test_mcdc_d1(val: str | int | None, min_val: int | None, max_val: int | None, expected: int | None) -> None:
    assert clean_int(val, min=min_val, max=max_val) == expected


MCDC_D3_CASES = [
    pytest.param("99", None, 5, 99, id="T1: A=V B=F"),
    pytest.param("0", 1, None, 0, id="T2: A=F B=V"),
    pytest.param("3", 1, 5, 3, id="T3: A=F B=F"),
]


@pytest.mark.parametrize(("val", "min_val", "max_val", "expected"), MCDC_D3_CASES)
def test_mcdc_d3(val: str | int | None, min_val: int | None, max_val: int | None, expected: int | None) -> None:
    assert clean_int(val, min=min_val, max=max_val) == expected


MCDC_D4_CASES = [
    pytest.param("0", 1, 5, None, id="T1: A=F B=V"),
    pytest.param("6", 1, 5, None, id="T2: A=V B=F"),
    pytest.param("3", 1, 5, 3, id="T3: A=V B=V"),
]


@pytest.mark.parametrize(("val", "min_val", "max_val", "expected"), MCDC_D4_CASES)
def test_mcdc_d4(val: str | int | None, min_val: int | None, max_val: int | None, expected: int | None) -> None:
    assert clean_int(val, min=min_val, max=max_val) == expected
