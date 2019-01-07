# Infra
![Image of Yaktocat]
(https://github.com/CybexDex/KYC/blob/master/KYC.jpg)

# Prepare
- install & setup pure faucet, git addr is: https://github.com/CybexDex/CybexFaucet.git
- install & setup mongodb, create db cybex_faucet_test
    * setup user&password as faucet,faucet123, same with pm2.json(below is just a example):
    ```
    {
      "apps": [
        {
          "name": "CybexFaucet",
          "script": "server/server.js",
          "env": {
            "NODE_ENV": "development",
            "NODE_API": "wss://shenzhen.51nebula.com/",
            "FAUCET_ACCOUNT": "sunxiaoqi-01",
            "FAUCET_ACCOUNT_WIF": "5KWTrrQMyD7Ez62viB36r75ur9ZJ6DPu3qkSa2eDcpE99XfD8ye",
            "PORT": 8087,
            "DB_URL": "mongodb://localhost:27017/",
            "DB_NAME": "cybex_faucet_test",
            "DB_USER": "faucet",
            "DB_PASS": "faucet123"
          },
          "env_test": {
            "NODE_ENV": "test",
            "NODE_API": "wss://shenzhen.51nebula.com/",
            "FAUCET_ACCOUNT": "sunxiaoqi-01",
            "FAUCET_ACCOUNT_WIF": "5KWTrrQMyD7Ez62viB36r75ur9ZJ6DPu3qkSa2eDcpE99XfD8ye",
            "DB_URL": "mongodb://localhost:27017/",
            "PORT": 8087,
            "DB_NAME": "cybex_faucet_test",
            "DB_USER": "faucet",
            "DB_PASS": "faucet123"
          },
          "env_production": {
            "NODE_ENV": "production",
            "NODE_API": "wss://shanghai.51nebula.com/",
            "FAUCET_ACCOUNT": "",
            "FAUCET_ACCOUNT_WIF": "",
            "DB_URL": "mongodb://localhost:27017/",
            "DB_NAME": "cybex_faucet",
            "DB_USER": "",
            "DB_PASS": ""
          }
        }
      ]
    }
    ```
    * create collection kyc, add index:
    ```
    > db.kyc.createIndex({'cybex_faucet_test.kyc':1})
    > db.kyc.getIndexes()
    [
            {
                    "v" : 2,
                    "key" : {
                            "_id" : 1
                    },
                    "name" : "_id_",
                    "ns" : "cybex_faucet_test.kyc"
            },
            {
                    "v" : 2,
                    "unique" : true,
                    "key" : {
                            "name" : 1
                    },
                    "name" : "name_1",
                    "ns" : "cybex_faucet_test.kyc"
            }
    ]
    ```
- install & setup kdb+/q, git addr: https://github.com/CybexDex/kdbSync.qpy , also need to set access control (q -u passfile, e.g script/q/pass)
    * q $BASE/script/q/kyc.q -u <pass> -p <port >
    ```
    q)\f
    `delExpire`genCode`verifyCode
    q)\a
    ,`codeTable
    
    ```
- install sendmail(python lib need it), mailutils
    * apt-get install sendmail,mailutils
- pip install -r production.pip

# Run
```
 ./start.sh > log.log 2>&1 &
```
open http://host:port/apidocs and check log.log and mydebug.log

