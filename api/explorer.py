import datetime
import json,requests
from services.cache import cache
import config
import logging
from logging.handlers import TimedRotatingFileHandler
from pymongo import MongoClient
import json, q3
from bson import json_util
from bson.objectid import ObjectId
import traceback,os
import smtplib
from services import qmail


import json
from collections import OrderedDict
from graphenebase.types import (
    Uint8, Int16, Uint16, Uint32, Uint64,
    Varint32, Int64, String, Bytes, Void,
    Array, PointInTime, Signature, Bool,
    Set, Fixed_array, Optional, Static_variant,
    Map, Id, VoteId
)
from graphenebase.objects import GrapheneObject, isArgsThisClass
from graphenebase.ecdsa import sign_message, verify_message
from graphenebase.account import PublicKey
import hashlib
from binascii import unhexlify, hexlify


logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/tmp/kyc_backend.log',
                filemode='w')
logHandler = TimedRotatingFileHandler(filename = '/tmp/kyc_backend.log',
                when = 'D', interval = 1, encoding='utf-8'
)
logger = logging.getLogger('pubAdmin')
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

client = MongoClient(config.MONGODB_DB_URL)
db = client[config.MONGODB_DB_NAME_KYC]
import cybex

cybex.cybex.cybex_debug_config(config.chain_id)
inst = cybex.Cybex(config.ws_conn)

try:
    inst.wallet.create(config.passwd)
except:
    print('failed to create wallet')
inst.wallet.unlock(config.passwd)

try:
    inst.wallet.addPrivateKey(config.privk)
except:
    print('failed to add key')

# constrain_dict = {}

_token = '12345678'
smtpObj = smtplib.SMTP(host = '127.0.0.1',  timeout = 26)


class Tx(GrapheneObject):
    def __init__(self, *args, **kwargs):
    # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('account', String(kwargs["account"])),
            ]))


def genCode(account):
    qconn =  q3.q(host = config.Q_HOST, port = config.Q_PORT, user = config.Q_USER)
    sql = 'genCode["%s"]'% (account)
    try:
        res = qconn.k3(str(sql))
    except:
        res = None
        logger.error(traceback.format_exc())
        logger.error(sql)
    qconn.close()
    return res
def sendVerifyCode(code, dest, ttype):
    if ttype == 0:
        # cmd = 'mail -s "Verificatoin Code from Cybex" %s <<< "Verificatoin Code is: %s"' % (dest , code)
        msg =  code
        try:
            # smtpObj.sendmail(config.sender, [dest], msg)
            qmail.mail([], dest, msg)
        except smtplib.SMTPException:
            logger.error("Error: unable to send email")
            return "Error: unable to send email"
        return 'email sent, please check!'
    elif ttype == 1:
        return "sms not defined now"
    return 'ttype not supported!'

def verifyCode(code, account):
    qconn =  q3.q(host = config.Q_HOST, port = config.Q_PORT, user = config.Q_USER)
    sql = 'verifyCode[`%s;"%s"]' % (code, account)
    try:
        res = bool(qconn.k3(str(sql)))
    except:
        res = False
        logger.error(traceback.format_exc())
        logger.error(sql)
    qconn.close()
    return res

def getKYC_golden(account, signature):
    obj = {}
    obj['account'] = account
    obj['signature'] = signature
    if verify_tx(obj):
        logger.info('pass')
    else:
        logger.error('verify failed')
        return {'msg':'failed to read, as wrong signature!'}
    try:
        res = list(db.golden.find({ "name" : account} , {'_id': False}))
    except:
        logger.error("get golden KYC failed when query " + account)
        return None
    if len(res) == 0:
        return None
    return res


def getKYC(account, signature):
    obj = {}
    obj['account'] = account
    obj['signature'] = signature
    if verify_tx(obj):
        logger.info('pass')
    else:
        logger.error('verify failed')
        return {'msg':'failed to read, as wrong signature!'}
    try:
        res = list(db.kyc.find({ "name" : account} , {'_id': False}))
    except:
        logger.error("getKYC failed when query " + account)
        return None
    if len(res) == 0:
        return None
    return res

def kycCreate(data):
    obj = {}
    obj['account'] = data['name'] 
    obj['signature'] = data['signature'] 
    if verify_tx(obj):
        logger.info('pass')
        data.pop('signature')
    else:
        logger.error('verify failed')
        return {'msg':'can not create'}
    constrain_data = list(db.schemas.find())
    if len(constrain_data) == 0 :
        return {'msg':'invalid as no constrain found for ' + data['name']}
    else:
        kyc_id = data['kyc_id']
        if not  _constrain(data, kyc_id):
            return {'msg':'failed when checking constrain'}
    try:
        db.kyc.insert_one(data )
    except:
        logger.error("failed to insert kyc" + str(data) )
        logger.error(traceback.format_exc())
        return {'msg':'failed to insert kyc ' + data['name']}
    for x in data.keys():
        if x in ('name','signature', 'kyc_id'):
            continue
        tmp_ = data.get(x, "")
        try:
            db.golden.update_one( { "name" : data['name'] }, { '$set' : { x : tmp_} }, True)
        except:
            data.pop('_id')
            logger.error(json.dumps(data) + "\t failed at "+ x)
            return {'msg':'failed to insert mongodb golden table!\t' +  json.dumps(data)}
    return {}


def kycRmv(account, signature):
    obj = {}
    obj['account'] = account
    obj['signature'] = signature
    if verify_tx(obj):
        logger.info('pass')
    else:
        logger.error('verify failed')
        return {'msg':'can not remove'}
    try:
        db.kyc.delete_many( { "name" : account })
        db.golden.delete_one( { "name" : account })
    except:
        logger.error()
        return {'msg':'failed to remove form mongodb.', 'err_code':1}
    return {}

def kycUpd(data): # only update on golden table
    obj = {}
    obj['account'] = data['name'] 
    obj['signature'] = data['signature'] 
    if verify_tx(obj):
        logger.info('pass')
    else:
        logger.error('verify failed')
        return {'msg':'can not update'}
    name = data['name']
    # kyc_id = data['kyc_id']
    for x in data.keys():
        if x in ('name','signature', 'kyc_id'):
            continue
        tmp_ = data.get(x, "")
        try:
            db.golden.update_one( { "name" : name }, { '$set' : { x : tmp_} }, True )
        except:
            logger.error(x + ':' + tmp_)
            return {'msg':'failed to update mongodb'}
    return {}

def get_account(account):
    d = {"jsonrpc":"2.0","method":"get_account_by_name","params":[account],"id":1}
    rsp = requests.post(url = config.CHAIN, data = json.dumps(d),  verify = True).json()
    logger.info(str(rsp))
    return rsp['result']
    
#  db.kyc.createIndex({'name':1}, { unique: true })
def register_naked(active, owner, memo, name):
    try:
        account = cybex.account.Account(name, cybex_instance = inst)
        return {'msg':'account already exist!', 'err_code':1}
    except:
        logger.info('account not exist, you can register it!')
    try:
        res = inst.create_account(name,registrar = config.faucet_account, referrer = config.faucet_account, active_key = active, owner_key=owner, memo_key = memo)
        return res
    except:
        return {'msg':'account failed to register!', 'err_code':1}

def register_constrain(schema, kyc_id):
    v = schema.split(',')
    if kyc_id == 'null':
        kyc_id = datetime.datetime.utcnow().strftime('%s')
    d = {}
    d['schema'] = v
    d['kyc_id'] = kyc_id
    try: # db.schemas.createIndex({'kyc_id':1}, {unique:true})
        db.schemas.insert_one(d)
    except:
        logger.error('kyc_id exists, please change your id')
        return {'msg':'kyc_id exists, please change your id'}
    # constrain_dict[k] = v
    return kyc_id
def unregister_contrain(k):
    db.schemas.delete_one({'kyc_id':k})
    # constrain_dict.pop(k)
    return {}
    
def _constrain(obj, kyc_id):
    try:
        #conts = set(constrain_dict[kyc_id])
        conts = set(list(db.schemas.find({'kyc_id':kyc_id}))[0]['schema'])
    except:
        return False
    if len(conts & set(obj.keys())) == len(conts):
        return True
    return False

def view_constrains(token):
    if token == _token:
        try:
            res = list(db.schemas.find({}, {'_id': False}))
            return res
        except:
            return {'msg':'error mongo!'}
        # return constrain_dict
    else:
        return {'msg':'error token'}

def build_tx(account, WIF):
    message = account
    signature = Signature(sign_message(message, WIF))
    # signature2 = Signature(sign_message(account, WIF))
    # logger.info(hexlify(signature2.data).decode('ascii'))
    d = {'account':account}
    d['signature'] = hexlify(signature.data).decode('ascii')
    return d

def debug_verify_tx(sig, account):
    d = {'signature':sig, 'account':account}
    return verify_tx(d)

def verify_tx(d):
    sig = d['signature']
    name = d['account']
    account = cybex.account.Account(name , cybex_instance = inst)
    del d['signature']
    message = name
    p = verify_message(message, unhexlify(sig))
    pkey = PublicKey(hexlify(p).decode('ascii'), prefix = 'CYB')
    # return str(pkey)
    _pubkey = account['active']['key_auths'][0][0]
    if str(pkey) == _pubkey:
        return True
    return False


def register_acct(obj ):
    is_create = obj['new']
    # d = {'account' : obj}
    if is_create == True:
        try:
            # rsp = requests.post(url = config.FAUCET_register, json = d).json()
            # accid = rsp['account']['trx']['operation_results'][0][1]
            res = register_naked(obj['active_key'], obj['owner_key'], obj['memo_key'], obj['name'])
            if 'err_code' in res.keys():
                return "error when try to naked register: " + json.dumps(res)
        except:
            logger.error(d)
            logger.error(traceback.format_exc())
            return "failed to register as name confilict."
    try:
        accid = get_account(obj['name'])['id']
    except:
        return "failed to create as account name not exist on the chain!"
        # get accid from chain to accid
    obj['accid'] = accid
    kycCreate(obj)
    return [accid,obj['name']]

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



#######################  ETO RELATED BELOW #######################
# db.survey.createIndex({'eto_id':1, 'account':1},{ unique: true })
# db.eto_subscription.createIndex({'eto_id':1, 'account':1},{ unique: true })

def get_survey(eto_id, account):
    try:
        res = list(db.survey.find({'eto_id':eto_id,'account':account}))[0]
        res.pop('_id')
    except:
        return {'err_msg':'faile to fetch from survey'}
    return res

def survey(obj ):
    d = obj.copy()
    try:
        db.survey.insert_one(d)
    except:
        return {'err_msg':'faile to insert survey'}
    return {'msg':'succeed'}


def rmv_survey(eto_id, account):
    try:
        db.survey.delete_one({'account':account, 'eto_id':eto_id })
    except:
        return {'err_msg':'faile to delete survey'}
    return {'msg':'succeed'}

def get_eto_subscription(eto_id, account):
    try:
        res = list(db.eto_subscription.find({'eto_id':eto_id,'account':account}))[0]
        res.pop('_id')
    except:
        return {'err_msg':'faile to fetch from survey'}
    return res

def eto_subscription(obj ):
    d = obj.copy()
    try:
        db.eto_subscription.insert_one(d)
    except:
        return {'err_msg':'faile to insert survey'}
    return {'msg':'succeed'}


def rmv_eto_subscription(eto_id,account):
    d = obj.copy()
    try:
        db.eto_subscription.delete_one({'eto_id':eto_id,'account':account})
    except:
        return {'err_msg':'faile to delete survey'}
    return {'msg':'succeed'}


def update_eto_subscription(obj ):
    d = obj.copy()
    account = d['account']
    eto_id = d['eto_id']
    new_asset = d['asset_id']
    new_symbol = d['symbol']
    try:
        db.eto_subscription.update_one({'eto_id':eto_id,'account':account},{'$set' : { 'asset_id' : new_asset, 'symbol':new_symbol }},True)
    except:
        return {'err_msg':'faile to update survey'}
    return {'msg':'succeed'}



# db.eto_subscription.createIndex({'eto_id':1})
def get_accounts_by_kyc(kyc_id):
    res = []
    try:
        it = db.kyc.find({'kyc_id':kyc_id})
        for i in it:
            accid = i.get('accid',None)
            if accid is None:
                logger.error('accid is null, will use account name as a replacement.')
                accid = i.get('name', None)
                if accid is None:
                    logger.error('panic as name is null, not expected! ')
                    continue
            res.append(accid) 
    except:
        logger.error('failed to get accounts by eto subscription:' + str(kyc_id))
    return res






