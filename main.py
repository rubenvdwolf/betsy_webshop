__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

from models import (db, User, Address, UserAddresses, Tag, Product, ProductTag, UsersOwnProducts, Transaction)
from peewee import *
from fuzzywuzzy import process
import os

def search(term):
    # look up all the products and descriptions, and their spelling ratio
    products_for_search = []
    descriptions_for_search = []
    for product in Product.select():
        products_for_search.append(product.name)
        descriptions_for_search.append(product.description)
    product_terms_to_search = process.extract(term, products_for_search)
    descriptions_to_search = process.extract(term, descriptions_for_search)

    # add all products (by product name or description) to products list if the ratio is high enough
    products = []
    for product in product_terms_to_search:
        if product[1] > 75:
            if product[0] not in products:
                products.append(product[0])
    for description in descriptions_to_search:
        if description[1] > 50:
            product_description = Product.get(Product.description == description[0])
            product_name = product_description.name
            if product_name not in products:
                products.append(product_name)

    #print the list of products if they exist
    if products == []:
        print('No products with that name')
    else:
        print(products)

def list_user_products(user_id):
    user_products = []
    
    #select the products by joining the connector model (UsersOwnProducts) and User model, and 'filter' by user_id
    for user_product in Product.select().join(UsersOwnProducts).join(User).where(User.id == user_id):
        user_products.append(user_product.name)
    
    #print list of users products if they exist
    if user_products == []:
        print('User has no products')
    else:
        print(user_products)

def list_products_per_tag(tag):
    found_products = []
    
    #Select products and join the Tag model, filter on products that have the tag and add those to found_products
    for product in Product.select().join(ProductTag).join(Tag).where(fn.LOWER(Tag.tag) == tag.lower()):
        found_products.append(product.name)
    
    #print list of products if they exist
    if found_products == []:
        print('No products with that tag')
    else:
        print(found_products)

def add_product_to_catalog(user_id, product, tag_name):
    # check if tag exists and create product, else create tag and create product
    if not Tag.select().where(Tag.tag == tag_name).exists():
        Tag.create(tag=tag_name)
        tag = Tag.get(Tag.tag == tag_name)
        Product.create(name=product[0], description=product[1], price_per_unit=product[2], amount_in_stock=product[3])
        product_id = Product.get(Product.name == product[0])
        ProductTag.create(tag_id=tag, product_id=product_id)
    else:
        tag = Tag.get(Tag.tag == tag_name)
        Product.create(name=product[0], description=product[1], price_per_unit=product[2], amount_in_stock=product[3])
        product_id = Product.get(Product.name == product[0])
        ProductTag.create(tag_id=tag, product_id=product_id)

    # get user and product
    user = User.get(User.id == user_id)
    new_product = Product.get(Product.name == product[0])
    
    #create new connection between user and product
    UsersOwnProducts.create(user_id=user, product_id=new_product)

def remove_product(product_id):
    #remove product
    Product.delete_by_id(product_id)
    
    #remove connection between user an product
    UsersOwnProducts.delete().where(UsersOwnProducts.product_id == product_id).execute()

    #remove connection between product and tag
    ProductTag.delete().where(ProductTag.product_id == product_id).execute()

def update_stock(product_id, new_quantity):
    #remove product from a user
    Product.update(amount_in_stock=new_quantity).where(Product.id == product_id).execute()

def purchase_product(product_id, buyer_id, quantity):
    # bijvoorbeeld product 1 (bruine schoenen) wordt gekocht door gebruiker 2, aantal = 2

    # get product, buyer, seller
    product = Product.get(Product.id == product_id)
    buyer = User.get(User.id == buyer_id)
    seller = User.select().join(UsersOwnProducts).join(Product).where(Product.id == product_id)
    # check if there is enough product in stock.
    # if not, print 'Not enough in stock!'
    if quantity > product.amount_in_stock:
        print('Not enough in stock!')
    # if quantity is as much as in stock, add transaction, update stock to 0, remove user-product connection
    elif quantity == product.amount_in_stock:
        Transaction.create(buyer_id=buyer, seller_id=seller, product_id=product, quantity=quantity)
        update_stock(product_id, 0)
        UsersOwnProducts.delete().where(UsersOwnProducts.product_id == product_id).execute()
    # else quantity < stock, add trasaction, update amount in stock
    else:
        Transaction.create(buyer_id=buyer, seller_id=seller, product_id=product, quantity=quantity)
        new_stock = product.amount_in_stock - quantity
        update_stock(product_id, new_stock)



def populate_test_database():
    # connect to database
    db.connect()
    
    # create tables
    models = [User, Address, UserAddresses, Tag, Product, ProductTag, UsersOwnProducts, Transaction]
    db.create_tables(models)

    # add users
    user_details = ['Bob', 'Larry', 'Junior', 'Mr. Lunt', 'Pa Grape']
    for user in user_details:
        User.create(name=user)
    print('Users added!')

    # add addresses
    addresses = [
        ('Teststraateen', 1, '', '1234AB', 'Rotterdam', 'The Netherlands'),
        ('Teststraattwee', 34, '', '5678CD', 'Amsterdam', 'The Netherlands'),
        ('Teststraateen', 65, 'B', '1123CD', 'Rotterdam', 'The Netherlands'),
        ('Teststraatdrie', 8, '', '4542HV', 'Utrecht', 'The Netherlands'),
        ('Teststraatvier', 136, 'A2', '9264JG', 'Zwolle', 'The Netherlands'),
        ('Teststraattwee', 4, '', '5814GT', 'Zierikzee', 'The Netherlands'),
        ('Teststraatvijf', 57, 'C', '3866JU', 'Droomstad', 'The Netherlands')
    ]
    Address.insert_many(addresses, fields=[Address.street, Address.number, Address.number_addition, Address.zip_code, Address.city, Address.country]).execute()
    print('Addresses added!')


    # add UserAddresses
    user_addresses = [
        (1, 1, 1),
        (2, 2, 2),
        (3, 3, 4),
        (4, 5, 5),
        (5, 6, 7)  
    ]
    for user_id, home_address_id, billing_address_id in user_addresses:
        user = User.get(User.id == user_id)
        home_address = Address.get(Address.id == home_address_id)
        billing_address = Address.get(Address.id == billing_address_id)
        UserAddresses.create(user_id=user, home_address_id=home_address, billing_address_id=billing_address)
    print('UsersAdresses added!')

    # add tags
    tags = ['Schoenen', 'Keyboards', 'Schrijfwaren']
    for tag in tags:
        Tag.create(tag=tag)
    print('Tags added!')

    # add products
    products = [
        ('Bruine Schoenen', 'Hele mooie bruine schoenen!', 25.99, 1),
        ('Keyboard', 'Degelijke Logitech keyboard', 10.00, 2),
        ('Pen', 'Goed schrijvende pen', 3.00, 20),
        ('Kicks', 'Nieuwe schonen van Asics, gewonnen bij een kansspel', 37.00, 1)
    ]
    for name, description, price_per_unit, amount_in_stock in products:
        Product.create(name=name, description=description, price_per_unit=price_per_unit, amount_in_stock=amount_in_stock)
    print('Products added!')

    # connect products to tags
    product_tags = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 1)
    ]
    for product, tag in product_tags:
        product_id = Product.get(Product.id == product)
        tag_id = Tag.get(Tag.id == tag)
        ProductTag.create(product_id=product_id, tag_id=tag_id)
    print('ProductTags added!')

    # add users own products
    user_own_products = [
        (1, 1),
        (1, 3),
        (3, 2),
        (5, 4)
    ]
    for user, product in user_own_products:
        user_id = User.get(User.id == user)
        product_id = Product.get(Product.id == product)
        UsersOwnProducts.create(user_id=user_id, product_id=product_id)
    print('UserOwnProducts added!')

    #close the database
    db.close()

def delete_database():
    cwd = os.getcwd()
    database_path = os.path.join(cwd, "betsydb.db")
    if os.path.exists(database_path):
        os.remove(database_path)
