class AppException(Exception):
    """Base application exception."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{self.code}: {self.message}")


# Coupon Errors (E-COUP-...)
class CouponException(AppException):
    pass


class CouponNotFoundException(CouponException):
    def __init__(self, code_or_id: str | int):
        super().__init__(
            code="E-COUP-NOT-FOUND",
            message="Купон не найден.",
            details={"coupon": str(code_or_id)},
        )


class CouponInvalidStatusException(CouponException):
    def __init__(self, status: str):
        super().__init__(
            code="E-COUP-INVALID-STATUS",
            message=f"Неверный статус купона: {status}.",
            details={"status": status},
        )


class CouponExpiredException(CouponException):
    def __init__(self):
        super().__init__(
            code="E-COUP-EXPIRED",
            message="Срок действия купона истёк.",
        )


class CouponAlreadyRedeemedException(CouponException):
    def __init__(self):
        super().__init__(
            code="E-COUP-ALREADY-REDEEMED",
            message="Купон уже был погашен.",
        )


class CouponMinPurchaseNotMetException(CouponException):
    def __init__(self, min_purchase: float, amount: float):
        super().__init__(
            code="E-COUP-MIN-PURCHASE",
            message=f"Минимальная сумма покупки ({min_purchase}) не достигнута.",
            details={"min_purchase": min_purchase, "amount": amount},
        )


class CouponConditionsNotMetException(CouponException):
    def __init__(self, reason: str):
        super().__init__(
            code="E-COUP-CONDITIONS",
            message=f"Условия для применения купона не выполнены: {reason}",
            details={"reason": reason},
        )


class CouponUsageLimitExceededException(CouponException):
    def __init__(self):
        super().__init__(
            code="E-COUP-LIMIT",
            message="Превышен лимит использований купона.",
        )


class CouponPerUserLimitExceededException(CouponException):
    def __init__(self):
        super().__init__(
            code="E-COUP-LIMIT",
            message="Превышен лимит использований купона для данного клиента.",
        )


class CouponClientMismatchException(CouponException):
    def __init__(self):
        super().__init__(
            code="E-COUP-CONDITIONS",
            message="Купон не принадлежит данному клиенту.",
        )


class CouponTemplateNotFoundException(CouponException):
    def __init__(self, template_id: int):
        super().__init__(
            code="E-COUP-TPL-NOT-FOUND",
            message="Шаблон купона не найден.",
            details={"template_id": template_id},
        )


# Other Errors
class ClientNotFoundException(AppException):
    def __init__(self, client_ref: str):
        super().__init__(
            code="E-CLIENT-NOT-FOUND",
            message="Клиент не найден.",
            details={"client_ref": client_ref},
        )
