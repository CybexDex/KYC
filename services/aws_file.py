# -*- coding: utf-8 -*-
import os
import logging
import traceback
from boto3.session import Session

# AccessKeyr_ID = 'LTAI4FjsgBVYLauRYbCpjYoH'
# AccessKeySecret = '07qLC0zHZXwfz1nvt5gm7GgDz4t8rK'
# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
class CybexKYCFilesLocate():
    def __init__(self, AccessKey_ID, AccessKeySecret, ENDPOINT, BUCKET_NAME):
        session = Session(aws_access_key_id=AccessKey_ID, aws_secret_access_key=AccessKeySecret, region_name=ENDPOINT)
        s3 = session.resource('s3')
        # client = session.client('s3')
        self.bucket = s3.Bucket(BUCKET_NAME)
    def upload_str(self, obj_name, ustr):
        try:
            file_obj = self.bucket.put_object(Key = obj_name,Body= ustr)
            logging.info(file_obj)
        except Exception as e:
            logging.error(e)
            return {'err_msg': "error when try to upload"}
        return {'result':True}
    def view(self):
        # 遍历文件目录
        l = []
        for b in self.bucket.objects.all():
            print(b.key)
            l.append(b.key)
        return l

def test_upload(inst):
    name = 'this_is_just_a_test_for_migration/test'
    content = 'hello, this is sunxiaoqi'
    rsp = inst.upload_str(name, content)
    print(rsp)
    return rsp

   
if __name__ == '__main__':
    # i = CybexKYCFilesLocate(config.AccessKeyr_ID, config.AccessKeySecret, config.ENDPOINT, config.BUCKET_NAME)
    i = CybexKYCFilesLocate('','','','')
    rsp = test_upload(i)
    list_rsp = i.view()


