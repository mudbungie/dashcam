# Database backend for dashcam synchronization.
# Tables:
# 	users: username, password, registration_ip, authorized
#		videos:	file_hash, path, upload_time, upload_name, size

import slqlachemy as sqla
from sqlalchemy import *
from sqlalchemy.ext.declarative import declaraative_base
from datetime import datetime

engine = create_engine('sqlite:///dashcam.db')
meta = MetaData()
Base = declarative_base(metadata=meta)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

class User(Base):
	username = Column(String(32), primary_key=True) # Is a UUID.
	password = Column(String(129)) # Is a sha512 hex digest.
	registration_ip = Column(String(39) # Because IPv6-compatible, why not?
	authorized = Column(Boolean, default=False)

class Videos(Base):
	file_hash = Column(String(129), primary_key=True) # sha512
	path = Column(Text)
	upload_time = Column(Datetime)
	upload_name = Column(Text)
	size = Column(Integer)
