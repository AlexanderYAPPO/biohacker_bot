import logging

import pymongo

logger = logging.getLogger(__name__)


def get_user_collection():
    conn = pymongo.MongoClient()
    return conn.prod.users


def get_logs_collection():
    conn = pymongo.MongoClient()
    return conn.prod.logs


def add_user_info(user_dict):
    coll = get_user_collection()
    logger.info('adding %s' % user_dict)
    coll.insert_one(user_dict)


def add_log_record(log_dict):
    coll = get_logs_collection()
    logger.info('adding %s' % log_dict)
    coll.insert_one(log_dict)
