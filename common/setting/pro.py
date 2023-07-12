class ProConfault():
    SECRET_KEY = "qwacwehQWRGT%^&*(*^&*(%^&*()qwawef12423@#$%^"
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/p8zyh'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_ECHO = False
    JWT_SECRET = "dfghjkRTYUIODFGHJKLertyui1235"
    # QQ登录相关配置
    QQ_APP_ID = '101474184'
    QQ_APP_KEY = 'c6ce949e04e12ecc909ae6a8b09b637c'
    QQ_REDIRECT_URL = 'http://www.meiduo.site:8080/oauth_callback.html'
    QQ_STATE = '/'
    # 钉钉登录相关配置
    DING_APP_ID = 'dingoajf8cqgyemqarekhr'
    DING_REDIRECT_URI = 'http://127.0.0.1:8080/dingding_back'
    DING_SECRET_KEY = 'Fcah25vIw-koApCVN0mGonFwT2nSze14cEe6Fre8i269LqMNvrAdku4HRI2Mu9VK'
