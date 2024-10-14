from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# MySQL database URI (replace credentials with your MySQL configuration)
DATABASE_URL = "mysql+mysqlconnector://user:password@192.168.144.2/dashboardDB"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define the Item model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(255), index=True)


# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# POST endpoint to insert an item
@app.post("/items/")
def create_item(name: str, description: str, db: Session = Depends(get_db)):
    item = Item(name=name, description=description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
