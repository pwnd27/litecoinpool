from sqlalchemy import ForeignKey, String
from datetime import datetime
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Worker(Base):
    __tablename__ = 'workers'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30))


class WorkerInfo(Base):
    __tablename__ = 'worker_info'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey('workers.id', ondelete='CASCADE'))
    hash_rate: Mapped[int]
    connected: Mapped[bool]
    time: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    worker: Mapped['Worker'] = relationship()