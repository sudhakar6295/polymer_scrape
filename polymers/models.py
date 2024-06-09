from sqlalchemy import Column, DateTime, Integer, String,TEXT,JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine,ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Create a base class for your models
Base = declarative_base()
#engine = create_engine('mysql://root:sudhakar@localhost/polymer')
engine = create_engine('mariadb+mariadbconnector://polymer:uEL50aB1IRRl9DMn@localhost/polymer')
# Define your models as subclasses of the base class


class Products(Base):
    __tablename__ = 'products'
    sku = Column(String(50), primary_key=True, index=True)
    product_url = Column(String(255))
    product_title = Column(String(255))
    normal_price =Column(String(50))
    discount_price = Column(String(50))
    stock = Column(JSON)
    categories = Column(String(255))
    subcategories = Column(String(255))
    breadcrumb = Column(String(255))
    weight = Column(String(50))
    dimension = Column(String(255))
    height = Column(String(50))
    width = Column(String(50))
    length = Column(String(50))
    approximate_weight = Column(String(50))
    descriptions = Column(TEXT)
    short_description = Column(TEXT)
    LastScrappeddate = Column(DateTime, onupdate=func.now())
    Updateddate = Column(DateTime, onupdate=func.now())
    Createddate = Column(DateTime, default=func.now())
    Status = Column(String(50))
    main_image_url = Column(String(255))


class Images(Base):
    __tablename__ = 'images'
    image_url = Column(String(255), primary_key=True)
    sku = Column(String(50), ForeignKey('products.sku'))
# Create the engine and connect to the database


# Create the tables in the database
Base.metadata.create_all(engine)

