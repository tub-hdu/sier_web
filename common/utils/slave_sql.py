import pymysql


class DB(object):
    """
    原生sql的封装
    """

    def __init__(self, host, port, user, password, database_name):
        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, db=database_name,
                                    charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        self.cousor = self.conn.cursor()

    def update(self, sql):
        """
        添加，修改，删除
        select * from name where name='admin'
        """
        self.cousor.execute(sql)
        self.conn.commit()

    def find(self, sql):
        """
        查询单个
        """
        self.cousor.execute(sql)
        res = self.cousor.fetchone()
        return res

    def find_all(self, sql):
        """
        查询所有
        """
        self.cousor.execute(sql)
        res = self.cousor.fetchall()
        return res

    def close(self):
        """
        关闭
        """
        self.cousor.close()
        self.conn.close()