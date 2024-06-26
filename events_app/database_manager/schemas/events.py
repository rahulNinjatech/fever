import uuid

from events_app.database_manager import Base
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID


class EventSchema(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(Integer, nullable=False, index=True)
    base_event_id = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    start_date_time = Column(DateTime, nullable=False, index=True)
    end_date_time = Column(DateTime, nullable=False, index=True)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)

    # Add a UniqueConstraint to base_event_id and event_id
    __table_args__ = (
        UniqueConstraint("base_event_id", "event_id", name="_base_event_id_event_id_uc"),
    )
