from time import gmtime, strftime
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, orm

engine = create_engine('mysql://scraper@localhost/newegg_data')

meta = MetaData()

table_name = strftime('%d_%m_%Y_%H_%M_%S', gmtime())

data_table = Table(table_name, meta,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('description', String(10000)),
                   Column('link', String(1024)),
                   Column('stock', String(254)),
                   Column('shipping', String(10000)),
                   Column('price', String(1024)),
                   Column('mail_rebate', String(1024)),
                   Column('instant_rebate', String(254)),
                   Column('final_price', String(254)),
                   Column('item_number', String(254))
                   )

meta.create_all(engine)


class Data(object):
    def __init__(self, description, link, stock, shipping, price, mail_rebate, instant_rebate, final_price, item_number):
        self.description = description
        self.link = link
        self.stock = stock
        self.shipping = shipping
        self.price = price
        self.mail_rebate = mail_rebate
        self.instant_rebate = instant_rebate
        self.final_price = final_price
        self.item_number = item_number


from sqlalchemy.orm import mapper
mapper(Data, data_table)


from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)


session = Session()

