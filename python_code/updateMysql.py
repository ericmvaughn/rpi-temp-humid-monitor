#!/usr/bin/python
##
## Script to import the temperature and humidity into a MySQL database
##
import sys
import MySQLdb
import time

def main(temp, humid, power, host, db, user, passwd, logging, sql_retries, sql_timeout):
    logging.debug('Temp = {0} *F, Hum = {1} %, Power = {2} W'.format(temp, humid, power))
    logging.debug('Updating MySQL database next ...')
    try:
        logging.info('Creating connection to the database')
        connection = MySQLdb.connect(host,user,passwd,db, connect_timeout=60)
    except MySQLdb.Error, e:
        logging.error('MySQL error %d: %s', (e.args[0], e.args[1]))
    
    cursor=connection.cursor()
    sqltemp=format(temp, '5.1f')
    sqlhumid=format(humid, '5.1f')
    sqlpower=format(power, '5.1f')
    logging.info('Temperature: {0}*F Humidity: {1}% Power: {2}W... updating to MySQL database'.format(sqltemp, sqlhumid, sqlpower))
    sql = """INSERT INTO TempHumid (ComputerTime, Temperature, Humidity, Power) VALUES (unix_timestamp(now()), %s, %s, %s)""" 
    args = (sqltemp, sqlhumid, sqlpower)

    success = False
    attempts = 0
    while attempts < sql_retries and not success:
        try:
            cursor.execute(sql, args)
            connection.commit()
            cursor.close()
            success = True
            logging.debug('The MySQL database was successfully updated.')
        except MySQLdb.Error, e:
            #logging.warn('The MySQL database could not be updated and returned the following error %d: %s', (e.args[0], e.args[1]))
            logging.warn('The MySQL database could not be updated and returned the following error {0} {1}'.format(e.args[0], e.args[1]))
            attempts += 1
            if attempts == sql_retries:
                logging.error('All configured attempts to update the MySQL database have failed. We are going to skip this attempt.')
            time.sleep(sql_timeout)
    return 0
