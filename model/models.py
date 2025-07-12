from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

Base = declarative_base()

# SQLAlchemy 모델 (데이터베이스 테이블)
class Host(Base):
    __tablename__ = "hosts"
    
    id = Column(Integer, primary_key=True, index=True)
    host_name = Column(String(255), unique=True, index=True, nullable=False)
    cpu_percentage = Column(Float)
    cpu_cores = Column(Integer)
    cpu_threads = Column(Integer)
    memory_usage = Column(Float)
    memory_percentage = Column(Float)
    get_datetime = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    containers = relationship("Container", back_populates="host")

class Container(Base):
    __tablename__ = "containers"
    
    id = Column(Integer, primary_key=True, index=True)
    engine_type = Column(String(100), nullable=False)
    cluster_name = Column(String(255), nullable=False)
    node_name = Column(String(255), nullable=False)
    container_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    cpu_percentage = Column(Float)
    memory_usage = Column(Float)
    memory_percentage = Column(Float)
    get_datetime = Column(DateTime, default=datetime.utcnow)
    
    # 외래키 설정
    host_id = Column(Integer, ForeignKey("hosts.id"))
    
    # 관계 설정
    host = relationship("Host", back_populates="containers")

# Pydantic 모델 (API 요청/응답용)
class HostData(BaseModel):
    host_name: str
    cpu_percentage: float
    cpu_cores: int
    cpu_threads: int
    memory_usage: float
    memory_percentage: float
    get_datetime: str

class ContainerData(BaseModel):
    engine_type: str
    cluster_name: str
    node_name: str
    container_name: str
    status: str
    cpu_percentage: float
    memory_usage: float
    memory_percentage: float
    get_datetime: str

class SystemResourceData(BaseModel):
    host: HostData
    containers: List[ContainerData]

# 응답 모델
class HostResponse(BaseModel):
    id: int
    host_name: str
    cpu_percentage: float
    cpu_cores: int
    cpu_threads: int
    memory_usage: float
    memory_percentage: float
    get_datetime: datetime
    
    class Config:
        from_attributes = True

class ContainerResponse(BaseModel):
    id: int
    engine_type: str
    cluster_name: str
    node_name: str
    container_name: str
    status: str
    cpu_percentage: float
    memory_usage: float
    memory_percentage: float
    get_datetime: datetime
    host_id: int
    
    class Config:
        from_attributes = True

 