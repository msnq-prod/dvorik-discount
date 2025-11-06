from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories.promotions import CampaignRepository
from app.schemas.promotions import Campaign, CampaignCreate, CampaignUpdate
from app.services.campaigns import CampaignService

router = APIRouter()


def get_campaign_service(db: Session = Depends(get_db)) -> CampaignService:
    campaign_repository = CampaignRepository()
    return CampaignService(campaign_repository)


@router.post("/", response_model=Campaign)
def create_campaign(
    *,
    campaign_in: CampaignCreate,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    return campaign_service.create_campaign(db, campaign_in=campaign_in)


@router.get("/{campaign_id}", response_model=Campaign)
def read_campaign(
    *,
    campaign_id: int,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/", response_model=list[Campaign])
def read_campaigns(
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    return campaign_service.get_all_campaigns(db)


@router.put("/{campaign_id}", response_model=Campaign)
def update_campaign(
    *,
    campaign_id: int,
    campaign_in: CampaignUpdate,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_service.update_campaign(
        db, campaign=campaign, campaign_in=campaign_in
    )


@router.delete("/{campaign_id}", response_model=Campaign)
def delete_campaign(
    *,
    campaign_id: int,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_service.remove_campaign(db, campaign_id=campaign_id)
