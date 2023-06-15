'''
Author: IVAN H. NGUYEN USACE-MVS
Last Updated: 05-22-2023
Version: 1.0
Description: The purpose of this script is to import data from CWMS and other schema then convert them to SHEF file format.
'''
from ast                                        import IsNot
from decimal                                    import Decimal
from hec.data.cwmsRating                      	import RatingSet
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

# Oscar Test

#import tkinter
#from tkinter import filedialog as fd



class Object:

	def __init__(self, lake, date_time, outflow, station):
		self.lake = lake
		self.date_time = date_time
		self.outflow = outflow
		self.station = station

class TextFileTop:
    
    def __init__(self, today_date):
        self.line1 = ": TODAYS LAKE FLOW AND 5 DAY FORECAST"
        self.line2 = ".B STL " + str(today_date) + " C DH0600/DC" + str(today_date) + "0600/QT/DRD+1/QTIF/DRD+2/QTIF/DRD+3/QTIF/DRD+4/QTIF/DRD+5/QTIF"
        self.text = self.line1+"\n"+self.line2 

class TextFileButton:
    
    def __init__(self, object_list):
        self.first = str(object_list[0].station)+" "
        self.last = " : "+str(object_list[0].lake)
        string = ""
        length = len(object_list)
        for index,item in enumerate(object_list):
            string += "{:.2f}".format(float(item.outflow)/1000)
            if index < (length-1):
                string += "/"
        self.text = self.first+string+self.last

class TextFileMarkTwain:
    
    def __init__(self, object_list, today_date):
        self.first = ": MARK TWAIN LAKE FLOW YESTERDAY"
        self.second = ".E CDAM7 "+str(today_date)+" C DH0000/DC"+str(today_date)+"0000/QTD/DID1/"+"{:.2f}".format(float(object_list[0].outflow)/1000)
        self.second_text = self.first+"\n"+self.second
        self.third = ": MARK TWAIN LAKE FLOW TODAY + 5 DAYS"
        self.fourth = ".E CDAM7 "+str(today_date[0:2])+str(int(today_date[2:4])+1)+" C DH0000/DC"+str(today_date)+"0630/QTDF/DID1/"+"{:.2f}".format(float(object_list[1].outflow)/1000)+"/"+"{:.2f}".format(float(object_list[2].outflow)/1000)+"/"+"{:.2f}".format(float(object_list[3].outflow)/1000)+"/"+"{:.2f}".format(float(object_list[4].outflow)/1000)+"/"+"{:.2f}".format(float(object_list[5].outflow)/1000)+"/"+"{:.2f}".format(float(object_list[6].outflow)/1000)
        self.third_text = self.third+"\n"+self.fourth

#def on_closing():
#    root.destroy()

today_date = datetime.datetime.now().strftime('%m%d')

# Name for the shef file
txt_file_name = "morning_shef"

## Pop-up and pick location to save ##
# root = tkinter.Tk()
# data_type = [('Shef file', '*.shef')]
# dial_directory = fd.asksaveasfilename(title="Save As", filetypes=data_type, initialfile="Outflow_text_file", defaultextension=("Shef file",".shef"))
#root.protocol("WM_DELETE_WINDOW", on_closing())

# Dictionary to hold the data for all lakes
lake_dict = {}
markTwain_list = []

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
                                        outflow,
                                        'CAYI2' as station
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
           object_list.append( Object(  rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9) ) )
                     
           print "test"
        
        lake_dict["Carlyle"] = object_list
        print lake_dict
           
	print object_list

	
	# create object for each row
	day0 = object_list [0]
	print "day0 = " + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
	
	day1 = object_list [1]
	print "day1 = " + str(day1.lake) + " - " + str(day1.date_time) + " - " + str(day1.outflow) + " - " + str(day0.station)

	day2 = object_list [2]
	print "day2 = " + str(day2.lake) + " - " + str(day2.date_time) + " - " + str(day2.outflow) + " - " + str(day0.station)

	day3 = object_list [3]
	print "day3 = " + str(day3.lake) + " - " + str(day3.date_time) + " - " + str(day3.outflow) + " - " + str(day0.station)

	day4 = object_list [4]
	print "day4 = " + str(day4.lake) + " - " + str(day4.date_time) + " - " + str(day4.outflow) + " - " + str(day0.station)

	day5 = object_list [5]
	print "day5 = " + str(day5.lake) + " - " + str(day5.date_time) + " - " + str(day5.outflow) + " - " + str(day0.station)
	
	# check data type
	print "lake type = " + str(type(day1.lake))
	print "date_time type = " + str(type(day1.date_time))
	print "outflow type = " + str(type(day1.outflow))

	#text_file = TextFile(today_date, object_list)

    #with open("C:/scripts/cwms/morning_shef/" + txt_file_name + ".shef", "w") as f:
    #    f.write(text_file.text)
    #    print("Text file created")

	#C:\scripts\cwms\morning_shef		
	## To save file in specific location
	# with open(str(dial_directory), "w") as f:
	#     f.write(text_file.text)
	#     print("Text file created")
	# root.destroy()

    finally :
        stmt.close()
        rs.close()
    return Carlyle


def retrieveWappapello(conn):
    try :
        Wappapello = None
        stmt = conn.prepareStatement('''
                                    select lake, 
									    date_time,
									    cwms_util.change_timezone(date_time, 'UTC', 'US/Central') as date_time_cst,
									    fcst_date,
									    cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') as fcst_date_cst,
									    to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'US/Central'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss') as system_date_cst,
									    to_char(date_time, 'mm-dd-yyyy') as date_time_2, 
									    outflow,
									    'WPPM7' as station
									from wm_mvs_lake.qlev_fcst 
									where lake = 'WAPPAPELLO'
									    and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
									order by date_time asc
									fetch next 6 row only
                                    ''')
        rs = stmt.executeQuery()

        # create object list to store the data (3 cols by 6 rows)
        object_list = []
        while rs.next() : 
           # loop and append which data col to object list
           object_list.append( Object(  rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9) ) )
           print "test"
        lake_dict["Wappapello"] = object_list
        print lake_dict
           
	print object_list
    
    
	# create object for each row
	day0 = object_list [0]
	print "day0 = " + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
	
	day1 = object_list [1]
	print "day1 = " + str(day1.lake) + " - " + str(day1.date_time) + " - " + str(day1.outflow) + " - " + str(day0.station)

	day2 = object_list [2]
	print "day2 = " + str(day2.lake) + " - " + str(day2.date_time) + " - " + str(day2.outflow) + " - " + str(day0.station)

	day3 = object_list [3]
	print "day3 = " + str(day3.lake) + " - " + str(day3.date_time) + " - " + str(day3.outflow) + " - " + str(day0.station)

	day4 = object_list [4]
	print "day4 = " + str(day4.lake) + " - " + str(day4.date_time) + " - " + str(day4.outflow) + " - " + str(day0.station)

	day5 = object_list [5]
	print "day5 = " + str(day5.lake) + " - " + str(day5.date_time) + " - " + str(day5.outflow) + " - " + str(day0.station)
	
	# check data type
	print "lake type = " + str(type(day1.lake))
	print "date_time type = " + str(type(day1.date_time))
	print "outflow type = " + str(type(day1.outflow))

	#text_file = TextFile(today_date, object_list)

	#with open("C:/scripts/cwms/morning_shef/" + txt_file_name + ".shef", "w") as f:
    		#f.write(text_file.text)
    		#print("Text file created")
			
	#C:\scripts\cwms\morning_shef		
	## To save file in specific location
	# with open(str(dial_directory), "w") as f:
	#     f.write(text_file.text)
	#     print("Text file created")
	# root.destroy()

    finally :
        stmt.close()
        rs.close()
    return Wappapello


def retrieveRend(conn):
    try :
        Rend = None
        stmt = conn.prepareStatement('''
                                    select lake, 
									    date_time,
									    cwms_util.change_timezone(date_time, 'UTC', 'US/Central') as date_time_cst,
									    fcst_date,
									    cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') as fcst_date_cst,
									    to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'US/Central'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss') as system_date_cst,
									    to_char(date_time, 'mm-dd-yyyy') as date_time_2, 
									    outflow,
									    'RNDI2' as station
									from wm_mvs_lake.qlev_fcst 
									where lake = 'REND'
									    and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
									order by date_time asc
									fetch next 6 row only
                                    ''')
        rs = stmt.executeQuery()

        # create object list to store the data (3 cols by 6 rows)
        object_list = []
        print "Rend Test"
        while rs.next() : 
           # loop and append which data col to object list
           object_list.append( Object(  rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9) ) )
           print "test"
        lake_dict["Rend"] = object_list
        print lake_dict
           
	print object_list

	# create object for each row
	day0 = object_list [0]
	print "day0 = " + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
	
	day1 = object_list [1]
	print "day1 = " + str(day1.lake) + " - " + str(day1.date_time) + " - " + str(day1.outflow) + " - " + str(day0.station)

	day2 = object_list [2]
	print "day2 = " + str(day2.lake) + " - " + str(day2.date_time) + " - " + str(day2.outflow) + " - " + str(day0.station)

	day3 = object_list [3]
	print "day3 = " + str(day3.lake) + " - " + str(day3.date_time) + " - " + str(day3.outflow) + " - " + str(day0.station)

	day4 = object_list [4]
	print "day4 = " + str(day4.lake) + " - " + str(day4.date_time) + " - " + str(day4.outflow) + " - " + str(day0.station)

	day5 = object_list [5]
	print "day5 = " + str(day5.lake) + " - " + str(day5.date_time) + " - " + str(day5.outflow) + " - " + str(day0.station)
	
	# check data type
	print "lake type = " + str(type(day1.lake))
	print "date_time type = " + str(type(day1.date_time))
	print "outflow type = " + str(type(day1.outflow))

	#text_file = TextFile(today_date, object_list)

	#with open("C:/scripts/cwms/morning_shef/" + txt_file_name + ".shef", "w") as f:
    		#f.write(text_file.text)
    		#print("Text file created")
			
	#C:\scripts\cwms\morning_shef		
	## To save file in specific location
	# with open(str(dial_directory), "w") as f:
	#     f.write(text_file.text)
	#     print("Text file created")
	# root.destroy()

    finally :
        stmt.close()
        rs.close()
    return Rend


def retrieveShelbyville(conn):
    try :
        Shelbyville = None
        stmt = conn.prepareStatement('''
                                    select lake, 
									    date_time,
									    cwms_util.change_timezone(date_time, 'UTC', 'US/Central') as date_time_cst,
									    fcst_date,
									    cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') as fcst_date_cst,
									    to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'US/Central'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss') as system_date_cst,
									    to_char(date_time, 'mm-dd-yyyy') as date_time_2, 
									    outflow,
									    'SBYI2' as station
									from wm_mvs_lake.qlev_fcst 
									where lake = 'SHELBYVILLE'
									    and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
									order by date_time asc
									fetch next 6 row only
                                    ''')
        rs = stmt.executeQuery()

        # create object list to store the data (3 cols by 6 rows)
        object_list = []
        while rs.next() : 
           # loop and append which data col to object list
           object_list.append( Object(  rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9) ) )
           print "test"
        lake_dict["Shelbyville"] = object_list
        print lake_dict
           
	print object_list

	# create object for each row
	day0 = object_list [0]
	print "day0 = " + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
	
	day1 = object_list [1]
	print "day1 = " + str(day1.lake) + " - " + str(day1.date_time) + " - " + str(day1.outflow) + " - " + str(day0.station)

	day2 = object_list [2]
	print "day2 = " + str(day2.lake) + " - " + str(day2.date_time) + " - " + str(day2.outflow) + " - " + str(day0.station)

	day3 = object_list [3]
	print "day3 = " + str(day3.lake) + " - " + str(day3.date_time) + " - " + str(day3.outflow) + " - " + str(day0.station)

	day4 = object_list [4]
	print "day4 = " + str(day4.lake) + " - " + str(day4.date_time) + " - " + str(day4.outflow) + " - " + str(day0.station)

	day5 = object_list [5]
	print "day5 = " + str(day5.lake) + " - " + str(day5.date_time) + " - " + str(day5.outflow) + " - " + str(day0.station)
	
	# check data type
	print "lake type = " + str(type(day1.lake))
	print "date_time type = " + str(type(day1.date_time))
	print "outflow type = " + str(type(day1.outflow))

	#text_file = TextFile(today_date, object_list)

	#with open("C:/scripts/cwms/morning_shef/" + txt_file_name + ".shef", "w") as f:
    		#f.write(text_file.text)
    		#print("Text file created")
			
	#C:\scripts\cwms\morning_shef		
	## To save file in specific location
	# with open(str(dial_directory), "w") as f:
	#     f.write(text_file.text)
	#     print("Text file created")
	# root.destroy()

    finally :
        stmt.close()
        rs.close()
    return Shelbyville


def retrieveMarkTwain(conn):
    try :
        MarkTwain = None
        stmt = conn.prepareStatement('''
                                    select lake, 
									    date_time,
									    cwms_util.change_timezone(date_time, 'UTC', 'US/Central') as date_time_cst,
									    fcst_date,
									    cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') as fcst_date_cst,
									    to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'US/Central'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss') as system_date_cst,
									    to_char(date_time, 'mm-dd-yyyy') as date_time_2, 
									    outflow,
									    'CDAM7' as station
									from wm_mvs_lake.qlev_fcst 
									where lake = 'MT'
									    and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
									order by date_time asc
									fetch next 7 row only
                                    ''')
        rs = stmt.executeQuery()

        # create object list to store the data (3 cols by 6 rows)
        while rs.next() : 
           # loop and append which data col to object list
           markTwain_list.append( Object(  rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9) ) )
           print "test"  
             
        print markTwain_list

        # create object for each row
        day0 = markTwain_list [0]
        print "day0 = " + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)

        day1 = markTwain_list [1]
        print "day1 = " + str(day1.lake) + " - " + str(day1.date_time) + " - " + str(day1.outflow) + " - " + str(day0.station)

        day2 = markTwain_list [2]
        print "day2 = " + str(day2.lake) + " - " + str(day2.date_time) + " - " + str(day2.outflow) + " - " + str(day0.station)

        day3 = markTwain_list [3]
        print "day3 = " + str(day3.lake) + " - " + str(day3.date_time) + " - " + str(day3.outflow) + " - " + str(day0.station)

        day4 = markTwain_list [4]
        print "day4 = " + str(day4.lake) + " - " + str(day4.date_time) + " - " + str(day4.outflow) + " - " + str(day0.station)

        day5 = markTwain_list [5]
        print "day5 = " + str(day5.lake) + " - " + str(day5.date_time) + " - " + str(day5.outflow) + " - " + str(day0.station)

	    # check data type
	    #print "lake type = " + str(type(day1.lake))
	    #print "date_time type = " + str(type(day1.date_time))
	    #print "outflow type = " + str(type(day1.outflow))

        # text_file = TextFile(today_date, object_list)

    finally :
        stmt.close()
        rs.close()
    return MarkTwain

    


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
    print lake_dict

    
    # get Carlyle data
    Carlyle = retrieveCarlyle(conn)
    print "Carlyle" +  str(Carlyle)

    # get Wappapello data
    Wappapello = retrieveWappapello(conn)
    print "Wappapello" +  str(Wappapello)
    
    # get Rend data
    Rend = retrieveRend(conn)
    print "Rend" +  str(Rend)

    # get Shelbyville data
    Shelbyville = retrieveShelbyville(conn)
    print "Shelbyville" +  str(Shelbyville)
    
    # get MarkTwain data
    MarkTwain = retrieveMarkTwain(conn)
    print "MarkTwain" +  str(MarkTwain)

    #Create Text File
    with open("C:/scripts/cwms/morning_shef/" + txt_file_name + ".shef", "w") as f:
        text = TextFileTop(today_date).text+"\n"
        data_text = ""
        for key, value in lake_dict.items():
            data_text += TextFileButton(value).text+"\n"
        end_text = ".END"
        text += data_text
        text += end_text
        text += "\n\n"
        second_text = TextFileMarkTwain(markTwain_list, today_date).second_text
        second_text += "\n\n"
        third_text = TextFileMarkTwain(markTwain_list, today_date).third_text
        f.write(text+second_text+third_text)
        print("Text file created")
    
        
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
