class Product:
    count_id =0

    def __init__(self, product_name, description, price, image=None):
        Product.count_id += 1
        self.__product_id = Product.count_id
        self.__product_name = product_name
        self.__description = description
        self.__price = price
        self.__image = image

    def get_product_id(self):
        return self.__product_id

    def set_product_id(self, product_id):
        self.__product_id = product_id

    def get_product_name(self):
        return self.__product_name

    def set_product_name(self, product_name):
        self.__product_name = product_name

    def get_description(self):
        return self.__description

    def set_description(self, description):
        self.__description = description

    def get_price(self):
        return self.__price

    def set_price(self, price):
        self.__price = price
        
    def get_image(self):
        return self.__image

    def set_image(self, image):
        self.__image = image


    def to_dict(self):
        return {
            "product_id": self.get_product_id(),
            "name": self.get_product_name(),
            "description": self.get_description(),
            "price": self.get_price()
        }
