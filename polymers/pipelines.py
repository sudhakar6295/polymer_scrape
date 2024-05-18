# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from polymers.models import Images,Products


class PolymersPipeline:

    def  __init__(self):
        #engine = create_engine('mysql://root:sudhakar@localhost/polymer')
        engine = create_engine('mariadb+mariadbconnector://polymer:uEL50aB1IRRl9DMn@localhost/polymer')
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
       
        # Create a session
        session = self.Session()

        try:
            # Query the database for the record you want to update
            record = session.query(Products).filter_by(sku=item['sku']).first()

            # Update the record if found
            if record:
                record.normal_price = item['normal_price']
                record.discount_price = item['discount_price']
                record.product_title = item['product_title']
                record.categories = item['categories']
                record.stock = item['stock']
                record.product_url = item['product_url']
                record.main_image_url = item['main_image_url']
                record.subcategories = item['subcategories']
                record.short_description = item['short_description']
                record.descriptions = item['descriptions']
                
                # Commit the changes to the database
                session.commit()
                spider.logger.info("Record updated successfully.")   
            else:
                new_record = Products(
                product_url = item['product_url'],
                product_title = item['product_title'],
                sku = item['sku'],
                normal_price = item['normal_price'],
                discount_price = item['discount_price'],
                stock = item['stock'],
                categories = item['categories'],
                subcategories = item['subcategories'],
                breadcrumb = item['breadcrumb'],
                weight = item['weight'],
                dimension = item['dimension'],
                height = item['height'],
                width = item['width'],
                length = item['length'],
                approximate_weight = item['approximate_weight'],
                descriptions = item['descriptions'],
                short_description = item['short_description'],
                main_image_url = item['main_image_url']
                  )
                
                # Add more columns and values as needed
            
                # Add the new record to the session
                session.add(new_record)
                
                # Commit the changes to the database
                session.commit()
                spider.logger.info("New record created successfully.")
        except Exception as e:
            # Rollback the changes in case of an error
            session.rollback()
            spider.logger.error("Failed to update record:", e)
        

        images = item['images']
        try:
            for image_value in images:
                img_record = session.query(Images).filter_by(image_url = image_value).first()
                if not img_record:
                    image_record = Images(image_url = image_value, sku = item['sku'])
                    session.add(image_record)
                    session.commit()
                    spider.logger.info("Image record created successfully.")
                else:
                    img_record.image_url = image_value
                    session.add(img_record)
                    session.commit()
                    spider.logger.info("Image updated.")
        except Exception as e:
            session.rollback()
            spider.logger.error("Failed to create image record:", e)    
        finally:
            # Close the session
            session.close()
        

        return item





           














    








