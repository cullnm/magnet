from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, String, UniqueConstraint

from app.models.base import Base

class SubnetState(Base):
    __tablename__ = "subnet_state"

    id = Column(Integer, primary_key=True)

    netuid = Column(Integer, index=True, unique=True, nullable=False)

    # chain / dynamic info
    name = Column(String, nullable=True)
    symbol = Column(String, nullable=True)

    tempo = Column(Integer, nullable=True)
    last_step = Column(Integer, nullable=True)

    emission = Column(Float, nullable=True)        # subnet.emission (TAO)
    alpha_in = Column(Float, nullable=True)
    alpha_out = Column(Float, nullable=True)
    tao_in = Column(Float, nullable=True)
    alpha_price = Column(Float, nullable=True)     # subnet.price (TAO per alpha)
    moving_price = Column(Float, nullable=True)

    # owner
    owner_hotkey = Column(String, nullable=True)
    owner_coldkey = Column(String, nullable=True)
    owner_uid = Column(Integer, nullable=True)
    owner_incentive = Column(Float, nullable=True)  # your burn rate

    # lifecycle
    network_registered_at = Column(Integer, nullable=True)  # block

    # housekeeping
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("netuid", name="uq_subnet_states_netuid"),
    )