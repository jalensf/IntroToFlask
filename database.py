from datetime import datetime

import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

products_db = myclient["products"]

order_management_db = myclient["order_management"]


def get_product(code):
    products_coll = products_db["products"]

    product = products_coll.find_one({"code":code},{"_id":0})

    return product

def get_products():
    product_list = []

    products_coll = products_db["products"]

    for p in products_coll.find({},{"_id":0}):
        product_list.append(p)

    return product_list

def get_branch(code):
    branches_coll = products_db["branches"]

    branch = branches_coll.find_one({"code": code})

    return branch

def get_branches():
    branch_list = []

    branches_coll = products_db["branches"] 

    for branch in branches_coll.find({}):
        branch_list.append(branch)

    return branch_list

def get_user(username):
    customers_coll = order_management_db['customers']
    user=customers_coll.find_one({"username":username})
    return user

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)

def get_past_orders(username):
    orders_coll = order_management_db['orders']

   
    past_orders_cursor = orders_coll.find({"username": username}).sort("orderdate", -1)

    past_orders = []

    for order in past_orders_cursor:
       
        order['orderdate'] = order['orderdate'].strftime('%Y-%m-%d %H:%M:%S')

        past_orders.append(order)

    return past_orders

def update_password(username, new_password):
    customers_coll = order_management_db['customers']
    customers_coll.update_one({'username': username}, {'$set': {'password': new_password}})


