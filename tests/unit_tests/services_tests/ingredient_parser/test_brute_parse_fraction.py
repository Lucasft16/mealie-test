"""
Testes unitários de `parse_fraction` (mealie/services/parser_services/brute/process.py).
Decisões:
    D1  len(x) == 1 and "fraction" in unicodedata.decomposition(x)    (A and B)
    D2  len(x.split("/")) != 2
    D3  except ZeroDivisionError
"""

import pytest

from mealie.services.parser_services.brute.process import parse_fraction

# Caixa-preta: particionamento de equivalência (classes válidas)
VALID_CASES = [
    pytest.param("½", 0.5, id="unicode"),
    pytest.param("⅓", 1 / 3, id="unicode, dízima"),
    pytest.param("3/4", 0.75, id="ascii própria"),
    pytest.param("7/2", 3.5, id="ascii imprópria"),
    # Caixa-preta: análise de valor limite
    pytest.param("0/1", 0.0, id="bva: numerador 0"),
    pytest.param("1/1", 1.0, id="bva: numerador = denominador"),
    pytest.param("2/1", 2.0, id="bva: numerador = denominador + 1"),
]


@pytest.mark.parametrize(("value", "expected"), VALID_CASES)
def test_valid_fractions(value: str, expected: float) -> None:
    assert parse_fraction(value) == pytest.approx(expected)


# Caixa-preta: classes inválidas
INVALID_CASES = [
    pytest.param("", id="vazia"),
    pytest.param("abc", id="texto"),
    pytest.param("1", id="inteiro sem barra"),
    pytest.param("a/b", id="partes não numéricas"),
    pytest.param("1/", id="denominador ausente"),
    pytest.param("/2", id="numerador ausente"),
    pytest.param("²", id="caractere único que não é fração"),
    # Análise de valor limite: denominador = 0 (D3)
    pytest.param("1/0", id="bva: denominador 0"),
    pytest.param("0/0", id="bva: 0/0"),
    # D2 verdadeiro
    pytest.param("1/2/3", id="duas barras"),
]


@pytest.mark.parametrize("value", INVALID_CASES)
def test_invalid_inputs_raise_value_error(value: str) -> None:
    with pytest.raises(ValueError):
        parse_fraction(value)


def test_zero_denominator_is_chained_from_zero_division() -> None:
    """Branch D3: ZeroDivisionError é traduzido para ValueError, mantendo a causa."""
    with pytest.raises(ValueError) as exc_info:
        parse_fraction("5/0")

    assert isinstance(exc_info.value.__cause__, ZeroDivisionError)


MCDC_D1_CASES = [
    pytest.param("½", 0.5, id="T1: A=V B=V"),
    pytest.param("a", None, id="T2: A=V B=F"),
    pytest.param("1/2", 0.5, id="T3: A=F"),
]


@pytest.mark.parametrize(("value", "expected"), MCDC_D1_CASES)
def test_mcdc_d1(value: str, expected: float | None) -> None:
    if expected is None:
        with pytest.raises(ValueError):
            parse_fraction(value)
    else:
        assert parse_fraction(value) == pytest.approx(expected)
