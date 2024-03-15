from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from uuid import uuid4
from datetime import datetime, timezone


class BaseModel:
    id = Column(String(150), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    def __init__(self):
        self.id = str(uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def save(self):
        from ..__init__ import storage1
        self.updated_at = datetime.now(timezone.utc)
        storage1.new(self)
        storage1.save()

    @classmethod
    def all(cls):
        """Returns all the instances of the class in storage"""
        from ..__init__ import storage1
        return storage1.all(cls)
    
    @classmethod
    def search(cls, **kwargs):
        from ..__init__ import storage1
        return storage1.search(cls, **kwargs)
    
    def to_dict(self):
        """Returns a dictionary representation of the model object"""
        dictionary = self.__dict__.copy()
        dictionary.pop('_sa_instance_state', None)
        return dictionary
