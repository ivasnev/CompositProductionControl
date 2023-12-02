from sqlalchemy import Column, Float, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Productionline(Base):
    __tablename__ = 'productionline'
    __table_args__ = {'comment': 'Прооизводственная линия', 'schema': 'armatura'}

    id_productionline = Column(Integer, primary_key=True)
    address = Column(String(255))
    lastinspection = Column(TIMESTAMP)
    name = Column(String(200))

    sensors = relationship('Sensors', back_populates='productionline')


class Zone(Base):
    __tablename__ = 'zone'
    __table_args__ = {'comment': 'Место размещения датчика печь, ванна и т.д.', 'schema': 'armatura'}

    id_zone = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    sensors = relationship('Sensors', back_populates='zone')


class Typedata(Base):
    __tablename__ = 'typedata'
    __table_args__ = {'comment': 'Тип данных градусы и тд.', 'schema': 'classifiers'}

    id_typedata = Column(Integer, primary_key=True)
    stype = Column(String(5), nullable=False)
    type = Column(String(50), nullable=False)

    typesensor = relationship('Typesensor', back_populates='typedata')


class Typeerror(Base):
    __tablename__ = 'typeerror'
    __table_args__ = {'schema': 'classifiers'}

    id_typeerror = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False)
    message = Column(String(255))

    sensorserror = relationship('Sensorserror', back_populates='typeerror')


class Typesensor(Base):
    __tablename__ = 'typesensor'
    __table_args__ = {'comment': 'Тип датчика, датчик температуры и т.п.', 'schema': 'classifiers'}

    id_typesensor = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    id_typedata = Column(ForeignKey('classifiers.typedata.id_typedata'), index=True)

    typedata = relationship('Typedata', back_populates='typesensor')
    sensors = relationship('Sensors', back_populates='typesensor')


class Sensors(Base):
    __tablename__ = 'sensors'
    __table_args__ = {'schema': 'armatura'}

    id_sensor = Column(Integer, primary_key=True)
    id_typesensor = Column(ForeignKey('classifiers.typesensor.id_typesensor'), nullable=False, index=True)
    id_zone = Column(ForeignKey('armatura.zone.id_zone'), nullable=False, index=True)
    id_productionline = Column(ForeignKey('armatura.productionline.id_productionline'), nullable=False, index=True)

    productionline = relationship('Productionline', back_populates='sensors')
    typesensor = relationship('Typesensor', back_populates='sensors')
    zone = relationship('Zone', back_populates='sensors')
    sensorserror = relationship('Sensorserror', back_populates='sensors')
    sensorvalue = relationship('Sensorvalue', back_populates='sensors')
    settings = relationship('Curentsettings', backref='sensors', uselist=False)


class Curentsettings(Sensors):
    __tablename__ = 'curentsettings'
    __table_args__ = {'schema': 'armatura'}

    id_sensor = Column(ForeignKey('armatura.sensors.id_sensor'), primary_key=True)
    bestvalue = Column(Float, nullable=False)
    delta = Column(Float, nullable=False)


class Sensorserror(Base):
    __tablename__ = 'sensorserror'
    __table_args__ = {'schema': 'armatura'}

    id_sensorerror = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    id_typeerror = Column(ForeignKey('classifiers.typeerror.id_typeerror'), nullable=False, index=True)
    id_sensor = Column(ForeignKey('armatura.sensors.id_sensor'), nullable=False, index=True)

    sensors = relationship('Sensors', back_populates='sensorserror')
    typeerror = relationship('Typeerror', back_populates='sensorserror')


class Sensorvalue(Base):
    __tablename__ = 'sensorvalue'
    __table_args__ = {'schema': 'armatura'}

    id_sensorvalue = Column(Integer, primary_key=True)
    time = Column(TIMESTAMP, nullable=False)
    value = Column(Float, nullable=False)
    id_sensor = Column(ForeignKey('armatura.sensors.id_sensor'), nullable=False, index=True)

    sensors = relationship('Sensors', back_populates='sensorvalue')
