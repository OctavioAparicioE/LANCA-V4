from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer
#from app.database import Base
from app.database2 import Base

class User(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))


class DatosMedicionPrincipal(Base):
    __tablename__ = "datos_medicion_principal"

    id_datos_medicion = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(String)
    responsable_medicion = Column(String)
    id_variables = Column(Integer, ForeignKey("variables_antena.id_variables"))
    identificador = Column(String, ForeignKey("mediciones.identificador"))
    id_start_stop = Column(Integer, ForeignKey("start_stop.id_start_stop"))

    # Relaciones
    variables = relationship("VariablesAntena")
    medicion = relationship("Mediciones")
    start_stop = relationship("StartStop")

class StartStop(Base):
    __tablename__ = "start_stop"

    id_start_stop = Column(Integer, primary_key=True, index=True)
    scan_start = Column(Float)
    scan_stop = Column(Float)
    step_start = Column(Float)
    step_stop = Column(Float)
    total_scan = Column(Float)
    total_step = Column(Float)
    point_scan = Column(Float)
    point_step  = Column(Float)


    # Relación con datos_medicion_principal
    datos_medicion_principal = relationship("DatosMedicionPrincipal", back_populates="start_stop")

class VariablesAntena(Base):
    __tablename__ = "variables_antena"
    
    id_variables = Column(Integer, primary_key=True, index=True)
    ganancia = Column(Float)
    polarizacion = Column(String)
    tiempo_medicion = Column(String)

    # Relación con datos_medicion_principal
    datos_medicion_principal = relationship("DatosMedicionPrincipal", back_populates="variables")

class Mediciones(Base):
    __tablename__ = "mediciones"

    id_medicion = Column(Integer, primary_key=True, index=True)
    identificador = Column(String, unique=True, index=True)
    
    # Relación con puntos_medicion
    puntos_medicion = relationship("PuntosMedicion", back_populates="medicion")

    # Relación con frecuencias
    frecuencias_r = relationship("Frecuencias", back_populates="medicion")
    
    # Relación con datos_medicion_principal
    datos_medicion_principal = relationship("DatosMedicionPrincipal", back_populates="medicion")

class PuntosMedicion(Base):
    __tablename__ = "puntos_medicion"

    id_puntos_medicion = Column(Integer, primary_key=True, index=True)
    id_medicion = Column(Integer, ForeignKey("mediciones.id_medicion"))
    scan = Column(Float)
    rinc = Column(Float)
    frecuencia = Column(Float)
    amplitud1 = Column(Float)
    fase1 = Column(Float)
    amplitud2 = Column(Float)
    fase2 = Column(Float)
    amplitud3 = Column(Float)
    fase3 = Column(Float)
    amplitud4 = Column(Float)
    fase4 = Column(Float)
    amplitud5 = Column(Float)
    fase5 = Column(Float)
    amplitud6 = Column(Float)
    fase6 = Column(Float)
    
    # Relación con la tabla mediciones
    medicion = relationship("Mediciones", back_populates="puntos_medicion")

class Frecuencias(Base):
    __tablename__ = "frecuencias"

    id_frecuencia = Column(Integer, primary_key=True, index=True)
    id_medicion = Column(Integer, ForeignKey("mediciones.id_medicion"), nullable=False)
    frecuencia = Column(Float)

    medicion = relationship("Mediciones", back_populates="frecuencias_r")