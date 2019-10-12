# -*- coding: utf-8 -*-
import os
import logging
import oss2
from itertools import islice
import traceback


# AccessKeyr_ID = 'LTAI4FjsgBVYLauRYbCpjYoH'
# AccessKeySecret = '07qLC0zHZXwfz1nvt5gm7GgDz4t8rK'
# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
class CybexKYCFilesLocate():
    def __init__(self, AccessKeyr_ID, AccessKeySecret, ENDPOINT, BUCKET_NAME):
        auth = oss2.Auth(AccessKeyr_ID, AccessKeySecret)
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        self.bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
    def upload_f(self, filedir, obj_name):
        try:
            self.bucket.put_object_from_file(obj_name, filedir)
        except:
            return {'err_msg': "error when try to upload file"}
        return {'result':true}
    def upload_str(self, obj_name, ustr):
        try:
            result = self.bucket.put_object(obj_name, ustr)
            logging.info('http status: {0}'.format(result.status))
            logging.info('request_id: {0}'.format(result.request_id))
            logging.info('ETag: {0}'.format(result.etag))
        except Exception as e:
            logging.error(e)
            return {'err_msg': "error when try to upload"}
        return {'result':True}
    def view(self):
        # 遍历文件目录
        for b in islice(oss2.ObjectIterator(self.bucket), 10):
            print(b.key)

def test_upload(inst):
    name = 'mhd/test2'
    content = 'hello, this is sunxiaoqi'
    rsp = inst.upload_str(name, content)
    print(rsp)

   
if __name__ == '__main__':
    # i = CybexKYCFilesLocate(config.AccessKeyr_ID, config.AccessKeySecret, config.ENDPOINT, config.BUCKET_NAME)
    log_file_path = "/tmp/ali_file.log"
    # 开启日志
    oss2.set_file_logger(log_file_path, 'oss2', logging.DEBUG)
    i = CybexKYCFilesLocate('LTAI4FjsgBVYLauRYbCpjYoH','07qLC0zHZXwfz1nvt5gm7GgDz4t8rK','http://oss-cn-beijing.aliyuncs.com','candybull-ieo-kyc')
    i.view()


