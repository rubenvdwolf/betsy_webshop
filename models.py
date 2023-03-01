from peewee import Model, SqliteDatabase, CharField, ForeignKeyField, IntegerField, DecimalField, TextField

db = SqliteDatabase("betsydb.db")

class BaseModel(Model):
  class Meta:
    database = db

# Models go here
class User(BaseModel):
  #id = AutoField()
  name = CharField(max_length=50)

class Address(BaseModel):
  #id = AutoField()
  street = CharField(max_length=50)
  number = IntegerField()
  number_addition = CharField(max_length=5)
  zip_code = CharField(max_length=6) #only for dutch users '1234AB'
  city = CharField(max_length=50)
  country = CharField(max_length=50)

class UserAddresses(BaseModel):
  #id = AutoField()
  user_id = ForeignKeyField(User)
  home_address_id = ForeignKeyField(Address)
  billing_address_id = ForeignKeyField(Address)

class Tag(BaseModel):
  #id = AutoField()
  tag = CharField(max_length=20)

class Product(BaseModel):
  #id = AutoField()
  name = CharField(max_length=30)
  description = TextField()
  price_per_unit = DecimalField(decimal_places=2, rounding='ROUND_HALF_UP')
  amount_in_stock = IntegerField()

class ProductTag(BaseModel):
  #id = AutoField()
  tag_id = ForeignKeyField(Tag)
  product_id = ForeignKeyField(Product)

class UsersOwnProducts(BaseModel):
  #id = AutoField()
  user_id = ForeignKeyField(User, backref='products')
  product_id = ForeignKeyField(Product)

class Transaction(BaseModel):
  #id = AutoField()
  buyer_id = ForeignKeyField(User)
  seller_id = ForeignKeyField(User)
  product_id = ForeignKeyField(Product)
  quantity = IntegerField()
