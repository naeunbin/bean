CREATE TABLE register ( user_id varchar(20), user_pw varchar(100), user_em varchar(30),nname varchar(30),pnum varchar(15));
CREATE TABLE board (idx INTEGER  primary key autoincrement, pid INTEGER, title varchar(30), data varchar(100000),reply_data varchar(100), user_id varchar(20),time date default current_timestamp, upload TEXT,file_ blob);
CREATE TABLE contexttb (idx INTEGER primary key autoincrement, pid INTEGER default 0, context varchar(1000),user_id varchar(20),myindex integer);
