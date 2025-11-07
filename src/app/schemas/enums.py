import enum


class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    unknown = "unknown"


class CouponStatusEnum(str, enum.Enum):
    draft = "draft"
    active = "active"
    issued = "issued"
    redeemed = "redeemed"
    expired = "expired"
    voided = "voided"


class EmployeeRoleEnum(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    marketer = "marketer"
    hr = "hr"
    support = "support"
    readonly = "readonly"
    cashier = "cashier"


class ShiftStatusEnum(str, enum.Enum):
    planned = "planned"
    done = "done"
    approved = "approved"


class CampaignStatusEnum(str, enum.Enum):
    draft = "draft"
    active = "active"
    paused = "paused"
    ended = "ended"


class BroadcastStatusEnum(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    sending = "sending"
    done = "done"
    canceled = "canceled"
    failed = "failed"


class CampaignEventTypeEnum(str, enum.Enum):
    click = "click"
    issue = "issue"
    redeem = "redeem"


class ActorTypeEnum(str, enum.Enum):
    admin = "admin"
    bot = "bot"
    employee = "employee"
    client = "client"


class DiscountTypeEnum(str, enum.Enum):
    percent = "percent"
    fixed = "fixed"
    gift = "gift"


class SubscriptionStatusEnum(str, enum.Enum):
    subscribed = "subscribed"
    not_subscribed = "not_subscribed"
    unknown = "unknown"


class EventNameEnum(str, enum.Enum):
    COUPON_ISSUED = "coupon_issued"
    COUPON_REDEEMED = "coupon_redeemed"
    PURCHASE_RECORDED = "purchase_recorded"
