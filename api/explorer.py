import datetime
import json,requests
import urllib2
from services.cache import cache
import config
import logging
from logging.handlers import TimedRotatingFileHandler
from pymongo import MongoClient
import json,zmq, q
from bson import json_util
from bson.objectid import ObjectId
import q,traceback,os
import smtplib


logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='mydebug.log',
                filemode='w')
logHandler = TimedRotatingFileHandler(filename = 'mydebug.log',
                when = 'D', interval = 1, encoding='utf-8'
)
logger = logging.getLogger('pubAdmin')
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

client = MongoClient(config.MONGODB_DB_URL)
db = client[config.MONGODB_DB_NAME_KYC]


smtpObj = smtplib.SMTP(host = '127.0.0.1',  timeout = 26)


def genCode(account):
    qconn =  q.q(host = config.Q_HOST, port = config.Q_PORT, user = config.Q_USER)
    sql = 'genCode["%s"]'% (account)
    try:
        res = qconn.k(str(sql))
    except:
        res = None
        logger.error(traceback.format_exc())
        logger.error(sql)
    qconn.close()
    return res
def sendVerifyCode(code, dest, ttype):
    if ttype == 0:
        cmd = 'mail -s "Verificatoin Code from Cybex" %s <<< "Verificatoin Code is: %s"' % (dest , code)
        msg =  code
        try:
            smtpObj.sendmail(config.sender, [dest], msg)
        except smtplib.SMTPException:
            logger.error("Error: unable to send email")
        return cmd
    elif ttype == 1:
        return "sms not defined now"
    return ['sendVerifyCode']

def verifyCode(code, account):
    qconn =  q.q(host = config.Q_HOST, port = config.Q_PORT, user = config.Q_USER)
    sql = 'verifyCode[`%s;"%s"]' % (code, account)
    try:
        res = bool(qconn.k(str(sql)))
    except:
        res = False
        logger.error(traceback.format_exc())
        logger.error(sql)
    qconn.close()
    return res

def getKYC(account):
    try:
        res = list(db.kyc.find({ "name" : account} , {'_id': False}))[0]
    except:
        logger.error("getKYC failed when query " + account)
        return None
    if len(res) == 0:
        return None
    return res

def kycCreate(data):
    try:
        db.kyc.insert_one(data )
    except:
        logger.error("failed to insert " + str(data) )
        logger.error(traceback.format_exc())


def kycRmv(account):
    try:
        db.kyc.delete_one( { "name" : account })
    except:
        logger.error()


def kycUpd(data):
    name = data['name']
    email = data['email']
    phone = data['phone']
    accid = data['accid']
    try:
        if email != "":
            db.kyc.update_one( { "name" : name }, { '$set' : { "email" : email } })
        if phone != "":
            db.kyc.update_one( { "name" : name }, { '$set' : { "phone" : phone } })
        if accid != "":
            db.kyc.update_one( { "name" : name }, { '$set' : { "accid" : accid } })
    except: 
        logger.error()

def get_account(account):
    d = {"jsonrpc":"2.0","method":"get_account_by_name","params":[account],"id":1}
    rsp = requests.post(url = config.CHAIN, data = json.dumps(d),  verify = True).json()
    logger.info(str(rsp))
    return rsp['result']
    
#  db.kyc.createIndex({'name':1}, { unique: true })
def register(obj):
    data = {}
    data['email'] = obj['email']
    data['phone'] = obj['phone']
    is_create = obj['new']
    obj.pop('email')
    obj.pop('phone')
    obj.pop('new')
    d = {'account' : obj}
    if is_create == True:
        try:
            rsp = requests.post(url = config.FAUCET_register, json = d).json()
            accid = rsp['account']['trx']['operation_results'][0][1]
        except:
            logger.error(d)
            logger.error(traceback.format_exc())
            return "failed to register as name confilict."
    else:
        try:
            accid = get_account(obj['name'])['id']
        except:
            return "failed to create as account name not exist on the chain!"
        # get accid from chain to accid
    data['name'] = obj['name']
    data['accid'] = accid
    kycCreate(data)
    return [accid,data['name']]

def is_success(account, accid):
    data = {'name':account,'id':accid}
    rsp2 = requests.get(url = config.FAUCET_status, params = data, verify = False).json()
    if rsp2.has_key('libConfirmed') and rsp2['libConfirmed'] == True :
        if rsp2['code'] == 0:
            return True
        else:
            return False
    else:
        if rsp2['code'] == 0:
            return 'yet not lib'
        return None

def finalize_kyc(account):
    rsp = getKYC(account)
    try:
        accid = rsp['accid']
    except:
        logger.error(rsp)
        return None
    name = rsp['name']
    data = {'name':name , 'id':accid }
    rsp2 = requests.get(url = config.FAUCET_status, params = data, verify = False).json()
    if rsp2.has_key('libConfirmed') and rsp2['libConfirmed'] == True :
        if rsp2['code'] == 0:
            return True
        else:
            kycRmv(name)
            return False
    else:
        logger.info(rsp2)
        return None




