import pint
import pytest

from mealie.schema.recipe.recipe_ingredient import CreateIngredientUnit
from mealie.services.parser_services.parser_utils import UnitConverter, UnitNotFound, merge_quantity_and_unit
from tests.utils import random_string


def test_uc_parse_string():
    uc = UnitConverter()
    parsed = uc.parse("cup")

    assert isinstance(parsed, pint.Unit)
    assert (str(parsed)) == "cup"


def test_uc_parse_unit():
    uc = UnitConverter()
    parsed = uc.parse(uc.parse("cup"))

    assert isinstance(parsed, pint.Unit)
    assert (str(parsed)) == "cup"


def test_uc_parse_invalid():
    uc = UnitConverter()
    input_str = random_string()
    parsed = uc.parse(input_str)

    assert not isinstance(parsed, pint.Unit)
    assert parsed == input_str


def test_uc_parse_invalid_strict():
    uc = UnitConverter()
    input_str = random_string()

    with pytest.raises(UnitNotFound):
        uc.parse(input_str, strict=True)


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_can_convert(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pint"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    assert uc.can_convert(unit_1, unit_2)


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_cannot_convert(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pound"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    assert not uc.can_convert(unit_1, unit_2)


def test_cannot_convert_invalid_unit():
    uc = UnitConverter()
    assert not uc.can_convert("cup", random_string())
    assert not uc.can_convert(random_string(), "cup")


def test_can_convert_same_unit():
    uc = UnitConverter()
    assert uc.can_convert("cup", "cup")


def test_can_convert_volume_ounce():
    uc = UnitConverter()
    assert uc.can_convert("ounce", "cup")
    assert uc.can_convert("cup", "ounce")


def test_convert_simple():
    uc = UnitConverter()
    quantity, unit = uc.convert(1, "cup", "pint")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "pint"
    assert quantity == 1 / 2


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_convert_pre_parsed(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pint"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    quantity, unit = uc.convert(1, unit_1, unit_2)
    assert isinstance(unit, pint.Unit)
    assert str(unit) == "pint"
    assert quantity == 1 / 2


def test_convert_weight():
    uc = UnitConverter()
    quantity, unit = uc.convert(16, "ounce", "pound")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "pound"
    assert quantity == 1


def test_convert_zero_quantity():
    uc = UnitConverter()
    quantity, unit = uc.convert(0, "cup", "pint")

    assert isinstance(unit, pint.Unit)
    assert quantity == 0


def test_convert_invalid_unit():
    uc = UnitConverter()

    with pytest.raises(UnitNotFound):
        uc.convert(1, "pound", random_string())


def test_convert_incompatible_units():
    uc = UnitConverter()

    with pytest.raises(pint.errors.DimensionalityError):
        uc.convert(1, "pound", "cup")


def test_convert_volume_ounce():
    uc = UnitConverter()
    quantity, unit = uc.convert(8, "ounce", "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 1


def test_merge_same_unit():
    uc = UnitConverter()
    quantity, unit = uc.merge(1, "cup", 2, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 3


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_merge_compatible_units(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pint"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    quantity, unit = uc.merge(1, unit_1, 1, unit_2)
    assert isinstance(unit, pint.Unit)
    # 1 cup + 1 pint = 1 cup + 2 cups = 3 cups
    assert quantity == 3


def test_merge_weight_units():
    uc = UnitConverter()
    quantity, unit = uc.merge(8, "ounce", 8, "ounce")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "ounce"
    assert quantity == 16


def test_merge_different_weight_units():
    uc = UnitConverter()
    quantity, unit = uc.merge(1, "pound", 8, "ounce")

    assert isinstance(unit, pint.Unit)
    # 1 pound + 8 ounces = 16 ounces + 8 ounces = 24 ounces
    assert str(unit) == "pound"
    assert quantity == 1.5


def test_merge_zero_quantities():
    uc = UnitConverter()
    quantity, unit = uc.merge(0, "cup", 1, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 1


def test_merge_invalid_unit():
    uc = UnitConverter()

    with pytest.raises(UnitNotFound):
        uc.merge(1, "pound", 1, random_string())


def test_merge_incompatible_units():
    uc = UnitConverter()

    with pytest.raises(pint.errors.DimensionalityError):
        uc.merge(1, "pound", 1, "cup")


def test_merge_negative_quantity():
    uc = UnitConverter()
    quantity, unit = uc.merge(-1, "cup", 2, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 1


def test_merge_volume_ounce():
    uc = UnitConverter()
    quantity, unit = uc.merge(4, "ounce", 1, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "fluid_ounce"  # converted automatically from ounce
    assert quantity == 12


def test_merge_quantity_and_unit_simple():
    unit_1 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(1, unit_1, 2, unit_2)

    assert quantity == 3
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_invalid():
    unit_1 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")
    unit_2 = CreateIngredientUnit(name="mealie_random", standard_quantity=1, standard_unit=random_string())

    with pytest.raises(UnitNotFound):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


def test_merge_quantity_and_unit_compatible():
    unit_1 = CreateIngredientUnit(name="mealie_pint", standard_quantity=1, standard_unit="pint")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(1, unit_1, 1, unit_2)

    # 1 pint + 1 cup = 2 pints + 1 cup = 3 cups, converted to pint = 1.5 pint
    assert quantity == 1.5
    assert unit.name == "mealie_pint"


def test_merge_quantity_and_unit_selects_larger_unit():
    unit_1 = CreateIngredientUnit(name="mealie_pint", standard_quantity=1, standard_unit="pint")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(2, unit_1, 4, unit_2)

    # 2 pint + 4 cup = 4 cups + 4 cups = 8 cups, should be returned as pint (larger unit)
    assert quantity == 4
    assert unit.name == "mealie_pint"


def test_merge_quantity_and_unit_selects_smaller_unit():
    unit_1 = CreateIngredientUnit(name="mealie_pint", standard_quantity=1, standard_unit="pint")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(0.125, unit_1, 0.5, unit_2)

    # 0.125 pint + 0.5 cup = 0.25 cup + 0.5 cup = 0.75 cup, should be returned as cup (smaller for < 1)
    assert quantity == 0.75
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_missing_standard_data():
    unit_1 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")
    unit_2 = CreateIngredientUnit(name="mealie_cup_no_std", standard_quantity=None, standard_unit=None)

    with pytest.raises(ValueError):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


def test_merge_quantity_and_unit_volume_ounce():
    unit_1 = CreateIngredientUnit(name="mealie_oz", standard_quantity=1, standard_unit="ounce")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(8, unit_1, 1, unit_2)

    assert quantity == 2
    assert unit.name == "mealie_cup"

def _unit(name: str, qty, std_unit) -> CreateIngredientUnit:
    return CreateIngredientUnit(name=name, standard_quantity=qty, standard_unit=std_unit)

# Implementação dos Testes

# ---------- MC/DC da decisão D1 (CT8 a CT11) ----------
@pytest.mark.parametrize(
    "q1, u1, q2, u2",
    [
        pytest.param(None, "cup", 1, "cup", id="CT8-A-false"),
        pytest.param(1, None, 1, "cup", id="CT9-B-false"),
        pytest.param(1, "cup", None, "cup", id="CT10-C-false"),
        pytest.param(1, "cup", 1, None, id="CT11-D-false"),
    ],
)
def test_merge_quantity_and_unit_mcdc_missing_standard_data(q1, u1, q2, u2):
    unit_1 = _unit("mealie_a", q1, u1)
    unit_2 = _unit("mealie_b", q2, u2)

    with pytest.raises(ValueError):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


# ---------- Complementares (caixa-preta) ----------
def test_merge_quantity_and_unit_zero_standard_quantity():  # CT12
    unit_1 = _unit("mealie_zero", 0, "cup")
    unit_2 = _unit("mealie_cup", 1, "cup")

    with pytest.raises(ValueError):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


def test_merge_quantity_and_unit_invalid_first_unit():  # CT13
    unit_1 = _unit("mealie_random", 1, random_string())
    unit_2 = _unit("mealie_cup", 1, "cup")

    with pytest.raises(UnitNotFound):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


def test_merge_quantity_and_unit_incompatible_units():  # CT14
    unit_1 = _unit("mealie_pound", 1, "pound")
    unit_2 = _unit("mealie_cup", 1, "cup")

    with pytest.raises(pint.errors.DimensionalityError):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


def test_merge_quantity_and_unit_result_exactly_one():  # CT15
    pint_u = _unit("mealie_pint", 1, "pint")
    cup_u = _unit("mealie_cup", 1, "cup")

    quantity, unit = merge_quantity_and_unit(0.5, pint_u, 1, cup_u)

    # 0.5 pint + 1 cup = 1 pint -> abs(1) < 1 é falso, permanece em pint
    assert quantity == pytest.approx(1)
    assert unit.name == "mealie_pint"


def test_merge_quantity_and_unit_result_just_below_one():  # CT16
    pint_u = _unit("mealie_pint", 1, "pint")
    cup_u = _unit("mealie_cup", 1, "cup")

    quantity, unit = merge_quantity_and_unit(0.49, pint_u, 1, cup_u)

    # 0.49 pint + 1 cup = 0.99 pint (<1) -> 1.98 cup
    assert quantity == pytest.approx(1.98)
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_negative_result():  # CT17
    pint_u = _unit("mealie_pint", 1, "pint")
    cup_u = _unit("mealie_cup", 1, "cup")

    quantity, unit = merge_quantity_and_unit(-1, pint_u, 1, cup_u)

    # -1 pint + 1 cup = -1 cup; abs(-0.5 pint) < 1 -> menor unidade
    assert quantity == pytest.approx(-1)
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_zero_result():  # CT18
    pint_u = _unit("mealie_pint", 1, "pint")
    cup_u = _unit("mealie_cup", 1, "cup")

    quantity, unit = merge_quantity_and_unit(1, pint_u, -2, cup_u)

    assert quantity == pytest.approx(0)
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_equal_size_units_returns_first():  # CT19
    unit_1 = _unit("mealie_cup", 1, "cup")
    unit_2 = _unit("mealie_cup_alt", 1, "cup")

    quantity, unit = merge_quantity_and_unit(1, unit_1, 2, unit_2)

    assert quantity == pytest.approx(3)
    assert unit.name == "mealie_cup"  # empate -> unit_1


def test_merge_quantity_and_unit_non_unit_multiplier():  # CT20
    tbsp = _unit("mealie_tbsp", 15, "milliliter")
    cup = _unit("mealie_cup", 240, "milliliter")

    quantity, unit = merge_quantity_and_unit(2, tbsp, 1, cup)

    # 30 ml + 240 ml = 270 ml = 1.125 cup
    assert quantity == pytest.approx(1.125)
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_volume_ounce_second_position():  # CT21
    cup = _unit("mealie_cup", 1, "cup")
    oz = _unit("mealie_oz", 1, "ounce")

    quantity, unit = merge_quantity_and_unit(1, cup, 8, oz)

    # 1 cup + 8 fl oz = 2 cup
    assert quantity == pytest.approx(2)
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_weight_ounce_not_converted():  # CT22
    lb = _unit("mealie_lb", 1, "pound")
    oz = _unit("mealie_oz", 1, "ounce")

    quantity, unit = merge_quantity_and_unit(1, lb, 8, oz)

    assert quantity == pytest.approx(1.5)
    assert unit.name == "mealie_lb"


def test_merge_quantity_and_unit_does_not_leak_definitions():  # CT23
    cup = _unit("mealie_cup", 1, "cup")
    pint_u = _unit("mealie_pint", 1, "pint")

    merge_quantity_and_unit(1, cup, 1, pint_u)

    assert not UnitConverter().can_convert("_mealie_unit_1", "cup")
