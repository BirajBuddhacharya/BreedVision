from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import sys; sys.path.append('.')
from dotenv import load_dotenv
from backend.scripts.logger import load_logger

# logging 
logger = load_logger()

# Database  configuration
load_dotenv()
try: 
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL) # database engine 
    Base = declarative_base()
    SessionLocal = sessionmaker(bind=engine, future=True)
except Exception as e: 
    logger.error(f"Error configuring database: {e}")
    exit(0)

# Model 
class Breed(Base): 
    __tablename__ = 'Breed'
    id = Column(Integer, primary_key=True, index = True)
    breed = Column(String, nullable=False)
    img_url = Column(String, nullable=False)
    
# initializing databse 
Base.metadata.create_all(engine)

def main(): 
    with SessionLocal() as session: 
        testData = Breed(breed = "test", img_url = "test")
        session.add(testData)
        session.commit()
        
    with SessionLocal() as session: 
        data = session.query(Breed)
        
        for row in data: 
            logger.info(f"{row.breed} {row.img_url}")
    
if __name__ == "__main__": 
    main()
        