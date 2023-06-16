import pymysql
from elasticsearch import Elasticsearch

def get_mysql_data(table_name):
    """获取指定表的全部数据"""
    client = pymysql.connect(host='127.0.0.1',port=3306,
                    password='123456',user='root', db='p8_flask')
    sql = 'select * from %s'% table_name
    # 创建游标
    course= client.cursor()
    # 执行sql语句
    course.execute(sql)
    # 查询全部
    rest = course.fetchall()
    # 关闭连接
    course.close()
    return rest


def into_es(table_name):
    """把数据导入es"""
    es = Elasticsearch(hosts="http://47.107.59.164/:9200")
    rest = get_mysql_data(table_name)
    print('rest>>', rest)
    # 把数据库中数据写入es
    # 先清空指定表的索引
    es.indices.delete(index=table_name)
    for i in rest:
        print(i)
        try:
            es.index(index=table_name, body={
                'id': i,
                'table_name': table_name,
                'title': i[5],
                'desc': i[6],
            })
        except Exception as e:
            print("es 创建索引错误, 原因是",e)


if __name__ == '__main__':
    into_es('tb_course')