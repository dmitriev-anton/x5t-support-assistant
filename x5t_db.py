from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from sqlalchemy import func

import os
from dotenv import load_dotenv

load_dotenv()

db_link = os.getenv('SQLACLHEMY_URL')



Base = automap_base()


# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine(db_link)

Base.prepare(autoload_with=engine, schema="core-waybills-schema")
Base.prepare(autoload_with=engine, schema="core-vehicle-schema")

session = Session(engine)

print([Base.classes])







