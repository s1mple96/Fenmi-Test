try:
    from utils.mysql_util import MysqlUtil
except ImportError:
    MysqlUtil = None

def check_db(order_id, logger=None):
    if not MysqlUtil:
        if logger:
            logger.info("未找到MysqlUtil，无法校验数据库！")
        return None
    db = MysqlUtil()
    sql = f"SELECT * FROM rtx_etcapply_order WHERE order_id='{order_id}'"
    result = db.query(sql)
    if logger:
        logger.info(f"数据库校验结果: {result}")
    return result 