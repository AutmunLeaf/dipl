from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class CalculationResult(BaseModel):
    """Результат расчета акта."""
    volume: Decimal = Field(description="Объем работ")
    price: Decimal = Field(description="Цена за единицу")
    total: Decimal = Field(description="Сумма без НДС")
    vat_rate: Decimal = Field(description="Ставка НДС (%)")
    vat_amount: Decimal = Field(description="Сумма НДС")
    grand_total: Decimal = Field(description="Итоговая сумма с НДС")

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}


class CalculatorError(Exception):
    """Исключение при ошибках калькулятора."""
    pass


def calculate_act_total(
    volume: float | str | Decimal,
    price: float | str | Decimal,
    vat_rate: Optional[float | str | Decimal] = 20.0
) -> CalculationResult:
    """
    Расчет стоимости работ по акту.
    
    Args:
        volume: Объем выполненных работ
        price: Цена за единицу работы
        vat_rate: Ставка НДС в процентах (по умолчанию 20%)
    
    Returns:
        CalculationResult с расчетами
    
    Raises:
        CalculatorError: При невалидных входных данных
    """
    try:
        # Конвертация в Decimal для точных вычислений
        vol = Decimal(str(volume))
        prc = Decimal(str(price))
        vat = Decimal(str(vat_rate)) if vat_rate is not None else Decimal("20.0")
        
        # Валидация значений
        if vol < 0:
            raise CalculatorError("Объем работ не может быть отрицательным")
        
        if prc < 0:
            raise CalculatorError("Цена не может быть отрицательной")
        
        if vat < 0:
            raise CalculatorError("Ставка НДС не может быть отрицательной")
        
        # Расчеты
        total = vol * prc
        vat_amount = total * (vat / Decimal("100"))
        grand_total = total + vat_amount
        
        return CalculationResult(
            volume=vol.quantize(Decimal("0.0001")),
            price=prc.quantize(Decimal("0.01")),
            total=total.quantize(Decimal("0.01")),
            vat_rate=vat,
            vat_amount=vat_amount.quantize(Decimal("0.01")),
            grand_total=grand_total.quantize(Decimal("0.01"))
        )
        
    except InvalidOperation as e:
        raise CalculatorError(f"Некорректный формат чисел: {e}")
    except Exception as e:
        if isinstance(e, CalculatorError):
            raise
        raise CalculatorError(f"Ошибка при расчете: {e}")


def calculate_with_discount(
    volume: float | str | Decimal,
    price: float | str | Decimal,
    discount_percent: float | str | Decimal = 0,
    vat_rate: Optional[float | str | Decimal] = 20.0
) -> Dict[str, Any]:
    """
    Расчет стоимости со скидкой.
    
    Args:
        volume: Объем работ
        price: Цена за единицу
        discount_percent: Процент скидки (0-100)
        vat_rate: Ставка НДС
    
    Returns:
        Dict с детализацией расчета
    """
    discount = Decimal(str(discount_percent))
    
    if discount < 0 or discount > 100:
        raise CalculatorError("Скидка должна быть в диапазоне от 0 до 100 процентов")
    
    base_calc = calculate_act_total(volume, price, vat_rate)
    
    # Применяем скидку к сумме без НДС
    discounted_total = base_calc.total * (Decimal("100") - discount) / Decimal("100")
    discounted_vat = discounted_total * (base_calc.vat_rate / Decimal("100"))
    discounted_grand_total = discounted_total + discounted_vat
    
    return {
        "base_calculation": base_calc.model_dump(),
        "discount_percent": discount,
        "discounted_total": float(discounted_total),
        "discounted_vat": float(discounted_vat),
        "discounted_grand_total": float(discounted_grand_total),
        "savings": float(base_calc.grand_total - discounted_grand_total)
    }


def validate_act_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Валидация данных для акта перед сохранением.
    
    Args:
        data: Словарь с данными акта
    
    Returns:
        Проверенные данные с рассчитанными полями
    
    Raises:
        CalculatorError: При ошибках валидации
    """
    required_fields = ["volume", "price"]
    
    for field in required_fields:
        if field not in data:
            raise CalculatorError(f"Отсутствует обязательное поле: {field}")
        
        if data[field] is None:
            raise CalculatorError(f"Поле {field} не может быть пустым")
    
    # Рассчитываем итоговые значения
    calc_result = calculate_act_total(
        volume=data["volume"],
        price=data["price"],
        vat_rate=data.get("vat_rate", 20.0)
    )
    
    # Если в данных есть total, проверяем его корректность
    if "total" in data and data["total"] is not None:
        expected_total = calc_result.total
        actual_total = Decimal(str(data["total"]))
        if abs(expected_total - actual_total) > Decimal("0.01"):
            raise CalculatorError(
                f"Несоответствие суммы: ожидается {expected_total}, получено {actual_total}"
            )
    
    # Добавляем рассчитанные значения
    validated_data = data.copy()
    validated_data["total"] = float(calc_result.total)
    validated_data["vat_amount"] = float(calc_result.vat_amount)
    validated_data["grand_total"] = float(calc_result.grand_total)
    
    return validated_data
