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


@router.post(
    "/",
    response_model=Campaign,
    summary="Create a new campaign",
    description="Creates a new campaign with the specified details.",
)
def create_campaign(
    *,
    campaign_in: CampaignCreate,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    return campaign_service.create_campaign(db, campaign_in=campaign_in)


@router.get(
    "/{campaign_id}",
    response_model=Campaign,
    summary="Get a specific campaign by ID",
    description="Retrieves the details of a specific campaign by its unique ID.",
)
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


@router.get(
    "/",
    response_model=list[Campaign],
    summary="Get all campaigns",
    description="Retrieves a list of all campaigns.",
)
def read_campaigns(
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    return campaign_service.get_all_campaigns(db)


@router.put(
    "/{campaign_id}",
    response_model=Campaign,
    summary="Update a campaign",
    description="Updates the details of an existing campaign.",
)
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


@router.delete(
    "/{campaign_id}",
    response_model=Campaign,
    summary="Delete a campaign",
    description="Deletes a campaign by its unique ID.",
)
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


@router.post(
    "/{campaign_id}/activate",
    response_model=Campaign,
    summary="Activate a campaign",
    description="Sets a campaign's status to 'active'.",
)
def activate_campaign(
    *,
    campaign_id: int,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_service.activate_campaign(db, campaign=campaign)


@router.post(
    "/{campaign_id}/deactivate",
    response_model=Campaign,
    summary="Deactivate a campaign",
    description="Sets a campaign's status to 'paused'.",
)
def deactivate_campaign(
    *,
    campaign_id: int,
    campaign_service: CampaignService = Depends(get_campaign_service),
    db: Session = Depends(get_db),
):
    campaign = campaign_service.get_campaign(db, campaign_id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign_service.deactivate_campaign(db, campaign=campaign)
