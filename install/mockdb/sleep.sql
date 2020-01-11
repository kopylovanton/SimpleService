create or replace NONEDITIONABLE FUNCTION SLEEP 
(from_time in number,to_time number ) 

RETURN VARCHAR2 AS 

k  number;


BEGIN
  
    k := DBMS_RANDOM.VALUE(from_TIME, to_time);
    DBMS_LOCK.sleep(k);

  RETURN to_char(round(k,2));
END SLEEP;
