from scrapy import Request
from scrapy import Spider
import os,requests
from bs4 import BeautifulSoup

class PolymershapesSpider(Spider):
    name = "polymershapes"
    allowed_domains = ["polymershapes.cl"]
    start_urls = ["https://polymershapes.cl/shop/"]
     

    def parse(self, response):
        categorys = response.xpath('//*[@class="product-categories"]/li')
        for category in categorys:
            category_url = category.xpath('.//a/@href').get()
            category_name = category.xpath('.//a/text()').get()
            yield Request(category_url, callback = self.parse_category,meta={"category":category_name})


    def parse_category(self, response):

        category = response.meta.get("category")
        products = response.xpath('//*[@class="name product-title woocommerce-loop-product__title"]/a/@href').extract()
        for product in products:
            yield Request(product, callback=self.parse_product,meta={"category":category})

        next_page_url = response.xpath('//a[@class="next page-number"]/@href').extract_first()
        if next_page_url:
            yield Request(next_page_url,callback=self.parse_category,meta={"category":category})

    def check_file_in_folder(self,folder, file):
        # Check if the file exists in the given folder
        if os.path.exists(os.path.join(folder,file)):
            return True
        else:
            return False

    def save_image(self, temp_images,folder="Image"):
        for url in temp_images:
            abs_url = url
            if not os.path.exists(folder):
                        os.makedirs(folder)
            file_exits = self.check_file_in_folder(folder, url)
            if  file_exits:
                continue
            file_name = url.split('/')[-1]
            filepath = os.path.join(folder,file_name)
            
            response = requests.get(abs_url)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                    print(f"Image saved as {filepath}")
            else:
                print(f"Failed to download image from {filepath}") 
    def clean_description(self,description):
        try:
            soup = BeautifulSoup(description, 'lxml')
            # Find all <img> tags and decompose (remove) them
            for img_tag in soup.find_all('img'):
                img_tag.decompose()
            # Get the modified HTML content
            modified_html = str(soup)
            return modified_html
        except Exception as e:
            return description
        
    def clean_text(self,text):
        try:
            if text:
                return text.strip()
        except:
            return None
        return None


    def parse_product(self, response):


        category = response.meta.get("category")
        categories = category

        product_url = response.url
        product_title = response.xpath('//h1[@class="product-title product_title entry-title"]//text()').get().strip()
        images = response.xpath('.//*[contains(@class,"woocommerce-product-gallery__image slide")]/a/@href').extract()

        self.save_image(images)

        stock_rows = response.xpath('.//*[@id="slw_item_stock_location_simple_product"]//option')
        stock_dict = {}
        for stock_row in stock_rows:
            qty = stock_row.xpath('.//@data-quantity').get()
            option = stock_row.xpath('.//text()').get()
            price = stock_row.xpath('.//@data-price').get()
            prioirty = stock_row.xpath('.//@data-priority').get()
            
            if 'Seleccionar' in option:
                continue

            stock_dict[option] = {}
            stock_dict[option]['qty'] = qty
            stock_dict[option]['price'] = price
            if prioirty:
                stock_dict[option]['prioirty'] = prioirty
        sku = response.xpath('//span[@class="sku"]/text()').extract_first()
        categories_lst = response.xpath('//*[@class="woocommerce-breadcrumb breadcrumbs uppercase"]/a/text()').extract()
        
        subcategories = categories_lst[-1]
        #social_share = response.xpath('//div[@class="social-icons share-icons share-row relative"]/a/@aria-label').extract()
        breadcrumbs = response.xpath('//nav/a/text()').extract()
        breadcrumb = ", ".join(breadcrumbs)
        descriptions = response.xpath('//div[@id="tab-description"]').get()
        if descriptions:
            descriptions = self.clean_description(descriptions)
        try:
            short_description = response.xpath('//div[@class="product-short-description"]//text()').extract()
            if short_description:
                short_description = " ".join([x.strip() for x in short_description if x.strip()])
            else:
                short_description = None
        except:
            short_description = None
        normal_price = response.xpath('//*[@class="product-info summary entry-summary col col-fit product-summary"]//text()[contains(.,"precio original era")]').get()
        discount_price = response.xpath("//*[@class='product-info summary entry-summary col col-fit product-summary']//text()[contains(.,'precio actual')]").get()
        if not normal_price:
            normal_price = response.xpath('//*[@class="product-info summary entry-summary col col-fit product-summary"]//*[@class="woocommerce-Price-amount amount"]//span/following-sibling::text()').get()

        weight = response.xpath('//th[contains(.,"Peso")]/following-sibling::td/text()').extract_first()
        dimension = response.xpath('//th[contains(.,"Dimensiones")]/following-sibling::td/text()').extract_first()
        height = response.xpath('//th[contains(.,"Altura (cm)")]/following-sibling::td/p/text()').extract_first()
        width = response.xpath('//th[contains(.,"Ancho (cm)")]/following-sibling::td/p/text()').extract_first()
        length = response.xpath('//th[contains(.,"Largo (cm)")]/following-sibling::td/p/text()').extract_first()
        approximate_weight = response.xpath('//th[contains(.,"Peso (kg)")]/following-sibling::td/p/text()').extract_first()

        if images:
            images = [image.split('/')[-1] for image in images]
            main_image_url = images[0]
            images.pop(0)
        else:
            images = []
            main_image_url = None
  


        item = {
            "product_url": product_url,
            "product_title": product_title,
            "sku": sku,
            "images": images,
            "normal_price": normal_price,
            "discount_price": discount_price,
            "stock": stock_dict,
            "categories": categories,
            "subcategories": subcategories,
            "breadcrumb": breadcrumb,
            "weight": self.clean_text(weight),
            "dimension": self.clean_text(dimension),
            "height": self.clean_text(height),
            "width": self.clean_text(width),
            "length": self.clean_text(length),
            "approximate_weight": self.clean_text(approximate_weight),
            "descriptions": descriptions,
            "short_description": self.clean_text(short_description),
            "main_image_url": main_image_url
        }
            

        yield item





