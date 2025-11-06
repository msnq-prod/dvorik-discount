from sqlalchemy.orm import Session

from app.db.models.promotions import Campaign
from app.db.repositories.promotions import CampaignRepository
from app.schemas.promotions import CampaignCreate, CampaignUpdate


class CampaignService:
    def __init__(self, campaign_repository: CampaignRepository):
        self.campaign_repository = campaign_repository

    def create_campaign(
        self, db: Session, *, campaign_in: CampaignCreate
    ) -> Campaign:
        return self.campaign_repository.create(db, obj_in=campaign_in)

    def get_campaign(self, db: Session, campaign_id: int) -> Campaign | None:
        return self.campaign_repository.get(db, id=campaign_id)

    def get_all_campaigns(self, db: Session) -> list[Campaign]:
        return self.campaign_repository.get_all(db)

    def update_campaign(
        self, db: Session, *, campaign: Campaign, campaign_in: CampaignUpdate
    ) -> Campaign:
        return self.campaign_repository.update(
            db, db_obj=campaign, obj_in=campaign_in
        )

    def remove_campaign(self, db: Session, *, campaign_id: int) -> Campaign:
        return self.campaign_repository.remove(db, id=campaign_id)
