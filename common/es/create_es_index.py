from elasticsearch import Elasticsearch


class ES():
    def __init__(self, index_name):
        self.es = Elasticsearch(
            hosts="http://47.107.59.164/:9200"
        )
        self.index_name = index_name

    def get_doc(self, uid):
        """获取index_name 所在的文件"""
        return self.es.get(index=self.index_name, id=uid)

    def insert_one(self, doc: dict):
        """创建或更新文档的索引"""
        self.es.index(index=self.index_name, body=doc)

    def insert_array(self, docs: list):
        for doc in docs:
            self.es.index(index=self.index_name, body=doc)

    def search(self, query, count: int = 30, fields=None):
        fields = fields if fields else ["title", 'pub_date']
        dsl = {
            "query": {
                # 全文检索
                "multi_match": {
                    "query": query, # 检索的关键字
                    "fields": fields # 从fileds进行匹配, fields是数据表中的字段
                },
            },
            # 匹配到的文字显示高亮
            "highlight": {
                "fields": {
                    "title": {}
                }
            }
        }
        match_data = self.es.search(index=self.index_name, body=dsl, size=count)
        return match_data

    def create_index(self):
        if self.es.indices.exists(index=self.index_name) is True:
            self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name, ignore=400)

    def delete_index(self):
        try:
            self.es.indices.delete(index=self.index_name)
        except:
            pass