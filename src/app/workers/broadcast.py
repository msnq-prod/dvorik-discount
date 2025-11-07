import asyncio
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.repositories.broadcasts import BroadcastRepository
from app.services.segmentation import SegmentationService
from bots.bot import client_bot

logger = get_task_logger(__name__)


from app.db.models.loyalty import Client
from app.db.repositories.loyalty import ClientRepository

@celery_app.task
def send_broadcast(broadcast_id: int):
    logger.info(f"Starting broadcast {broadcast_id}")
    db: Session = SessionLocal()
    broadcast_repo = BroadcastRepository()
    broadcast = broadcast_repo.get(db, id=broadcast_id)
    if not broadcast:
        logger.error(f"Broadcast {broadcast_id} not found.")
        return

    segmentation_service = SegmentationService()
    client_ids = segmentation_service.get_client_ids(
        db, audience_filter=broadcast.audience_filter
    )

    clients = db.query(Client).filter(Client.id.in_(client_ids)).all()

    loop = asyncio.get_event_loop()
    for client in clients:
        try:
            loop.run_until_complete(
                client_bot.send_message(
                    chat_id=client.tg_id, text=broadcast.content["text"]
                )
            )
            broadcast.sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send message to {client.tg_id}: {e}")
            broadcast.fail_count += 1

    broadcast_repo.update(db, db_obj=broadcast, obj_in={})
    db.close()
    logger.info(f"Broadcast {broadcast_id} finished.")
