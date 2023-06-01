# name=morning_shef
# displayinmenu=true
# displaytouser=true
# displayinselector=true
'''
Author: IVAN H. NGUYEN USACE-MVS
Last Updated: 05-22-2023
Version: 1.0
Description: The purpose of this script is to import data from CWMS and other schema then convert them to SHEF file format.
'''
from ast                                        	import IsNot
from decimal                                    import Decimal
from hec.data.cwmsRating                      import RatingSet
from hec.script                                 import MessageBox, Constants, AxisMarker
from hec.dataTable                              import HecDataTableToExcel      
from hec.dssgui                                 import ListSelection
from hec.data.tx                                import QualityTx
from hec.heclib.util                            import HecTime
from hec.hecmath                                import TimeSeriesMath
from hec.io                                     import TimeSeriesContainer
from hec.script.Constants                       import TRUE, FALSE
from javax.swing                                import JOptionPane, JDialog, JButton, JPanel
from java.awt.event                             import ActionListener, FocusListener
from java.text                                  import SimpleDateFormat, NumberFormat
from java.awt                                   import BorderLayout, GridLayout, FlowLayout, Toolkit, GraphicsEnvironment, Rectangle, Color, Font
from java.util                                  import Locale, Calendar, TimeZone
from java.io                                    import FileOutputStream, IOException
from java.lang                                  import System
from rma.swing                                  import DateChooser
from javax.swing.border                         import EmptyBorder
from operator                                   import is_not
from rma.services                               import ServiceLookup
from subprocess                                 import Popen
from time                                       import mktime, localtime
import inspect, math
import DBAPI
import os
import urllib
import java                                     
import time,calendar,datetime
import java.lang
import os, sys, inspect, datetime, time, DBAPI



class Object:

	def __init__(self, lake, date_time, outflow):
		self.lake = lake
		self.date_time = date_time
		self.outflow = outflow


def retrieveCarlyle(conn):
    try :
        Carlyle = None
        stmt = conn.prepareStatement('''
                                    select lake, 
                                        date_time,
                                        cwms_util.change_timezone(date_time, 'UTC', 'US/Central') as date_time_cst,
                                        fcst_date,
                                        cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') as fcst_date_cst,
                                        to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'US/Central'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss') as system_date_cst,
                                        to_char(date_time, 'mm-dd-yyyy') as date_time_2, 
                                        outflow
                                    from wm_mvs_lake.qlev_fcst 
                                    where lake = 'CARLYLE'
                                        and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
                                    order by date_time asc
                                    fetch next 6 row only
                                    ''')
        rs = stmt.executeQuery()

        # create object list to store the data (3 cols by 6 rows)
        object_list = []
        while rs.next() : 
           # loop and append which data col to object list
	    object_list.append( Object(  rs.getString(1),rs.getString(2),rs.getString(8) ) )
            
            print "test"
	print object_list

	# create object for each row
	day0 = object_list [0]
	print "day0 = " + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow)
	
	day1 = object_list [1]
	print "day1 = " + str(day1.lake) + " - " + str(day1.date_time) + " - " + str(day1.outflow)

	day2 = object_list [2]
	print "day2 = " + str(day2.lake) + " - " + str(day2.date_time) + " - " + str(day2.outflow)

	day3 = object_list [3]
	print "day3 = " + str(day3.lake) + " - " + str(day3.date_time) + " - " + str(day3.outflow)

	day4 = object_list [4]
	print "day4 = " + str(day4.lake) + " - " + str(day4.date_time) + " - " + str(day4.outflow)

	day5 = object_list [5]
	print "day5 = " + str(day5.lake) + " - " + str(day5.date_time) + " - " + str(day5.outflow)
	
	# check data type
	print "lake type = " + str(type(day1.lake))
	print "date_time type = " + str(type(day1.date_time))
	print "outflow type = " + str(type(day1.outflow))

	

    finally :
        stmt.close()
        rs.close()
    return Carlyle



try :    
    NowTw  = datetime.datetime.now()
    print '='
    print '='
    print '='
    print '=================================================================================='
    print '============================== START LOG RUN AT ' + str(NowTw)
    print '================================================================================== '
    print '='
    print '='
    print '='
    

    # connect to database
    CwmsDb = DBAPI.open()
    CwmsDb.setOfficeId('MVS')
    CwmsDb.setTimeZone('GMT')
    
    # Create a java.sql.Connection
    conn = CwmsDb.getConnection()


    print "test2"

    
    # get Carlyle data
    Carlyle = retrieveCarlyle(conn)
    print "Carlyle" +  str(Carlyle)



    # close the database
    CwmsDb.close()

    print '='
    print '='
    print '='
    print '=================================================================================='
    print '============================== END LOG '
    print '================================================================================== '
    print '='
    print '='
    print '='

    
finally :
    try : CwmsDb.done()
    except : pass

    try : CwmsDb.done()
    except : pass

    try : CwmsDb.close()
    except : pass
