
genCode:{[account]
 time:.z.P;
 a:(md5 ";" sv (string(time); account)) ;
 code:`$("" sv string(-3#a));
 ele:`acct xkey enlist (`acct`time`code!)(`$account; time; code);
 codeTable,::ele;
 code }

verifyCode:{[code; account]
 res:((raze (select code from codeTable where acct = `$account)`code)@0) ~ code;
 if[res=1;codeTable::delete from codeTable where acct=`$account];
 res }

delExpire:{[]
 codeTable::delete from codeTable where (.z.P - time.timestamp) > 00:05:00;}

.z.ts:{delExpire[];}

\t 60000
/\t 0
