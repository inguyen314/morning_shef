'''
Author: IVAN H. NGUYEN USACE-MVS
Last Updated: 06-26-2023
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

# Oscar NEW COMMENT

#import tkinter
#from tkinter import filedialog as fd

class Object_LD:
    
    def __init__(self, value1, value2, value3, value4, value5, value6, value7):
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
        self.value4 = value4
        self.value5 = value5
        self.value6 = value6
        self.value7 = value7

class TextFileLD:
    def __init__(self, object_1, object_2, object_3, date):
        self.line1 = ": TODAYS OVSERVED POOL AND 5 DAY FORECAST ABOVE GAGE ZERO"
        self.line2 = ".B STL "+ str(date)+" C DH0600/DC0"+str(date)+"700/HP/DRD+1/HPIF/DRD+2/HPIF/DRD+3/HPIF"
        self.body = str(object_1[2].value5)+"  "+"{:.2f}".format(float(object_1[2].value3)/1000)+"/"+"{:.2f}".format(float(object_2[10].value3)/1000)+"/"+"{:.2f}".format(float(object_2[11].value3)/1000)+"/"+"{:.2f}".format(float(object_2[12].value3)/1000)+"/"
        self.body += "{:.2f}".format(float(object_2[13].value3)/1000)+"/"+"{:.2f}".format(float(object_2[14].value3)/1000)+" : CLARKSVILLE LD 24 --> HINGE PT LOUSIANA "+"{:.1f}".format(float(object_3[4].value3))+" - "+"{:.1f}".format(float(object_3[5].value3))+" "+str(object_3[4].value2).upper()+"\n"
        self.body += str(object_1[1].value5)+"  "+"{:.2f}".format(float(object_1[1].value3)/1000)+"/"+"{:.2f}".format(float(object_2[5].value3)/1000)+"/"+"{:.2f}".format(float(object_2[6].value3)/1000)+"/"+"{:.2f}".format(float(object_2[7].value3)/1000)+"/"
        self.body += "{:.2f}".format(float(object_2[8].value3)/1000)+"/"+"{:.2f}".format(float(object_2[9].value3)/1000)+" : WINFIELD LD 25 --> HINGE PT MOSIER LDG "+"{:.1f}".format(float(object_3[2].value3))+" - "+"{:.1f}".format(float(object_3[3].value3))+" "+str(object_3[2].value2).upper()+"\n"
        self.body += str(object_1[0].value5)+"  "+"{:.2f}".format(float(object_1[0].value3)/1000)+"/"+"{:.2f}".format(float(object_2[0].value3)/1000)+"/"+"{:.2f}".format(float(object_2[1].value3)/1000)+"/"+"{:.2f}".format(float(object_2[2].value3)/1000)+"/"
        self.body += "{:.2f}".format(float(object_2[3].value3)/1000)+"/"+"{:.2f}".format(float(object_2[4].value3)/1000)+" : ALTON LD 26 --> HINGE PT GRAFTON "+"{:.1f}".format(float(object_3[0].value3))+" - "+"{:.1f}".format(float(object_3[1].value3))+" "+str(object_3[0].value2).upper()+"\n.END"

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

def retrieveLD(conn):
    try :
        LD = None
        stmt = conn.prepareStatement('''
                                    select location_level_id, level_unit, constant_level, specified_level_id
                                    from CWMS_20.AV_LOCATION_LEVEL 
                                    where specified_level_id in ('Hinge Max','Hinge Min') 
                                    and unit_system = 'EN' 
                                    and location_id in ('Grafton-Mississippi','Louisiana-Mississippi','Mosier Ldg-Mississippi')
                                    ''')
        rs = stmt.executeQuery()
        
        # create object list to store the data (3 cols by 6 rows)
        object_list_1 = []
        while rs.next() : 
            # loop and append which data col to object list
            object_list_1.append(Object_LD(rs.getString(1),rs.getString(2),rs.getString(3),rs.getString(4),None,None,None))
                     
           
        print object_list_1
            
        for obj in object_list_1:
            print obj.value1
	

    finally :
        stmt.close()
        rs.close()
    return LD


def retrieveLD_2(conn):
    try :
        LD_2 = None
        print "retrieveLD_222"
        stmt = conn.prepareStatement('''
                                    with cte_pool as 
(select 'LD 24 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code, 'CLKM7' as damlock
from cwms_v_tsv_dqu  tsv
where 
     tsv.cwms_ts_id = 'LD 24 Pool-Mississippi.Stage.Inst.30Minutes.0.29' 
     and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss') 
     and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
     and tsv.office_id = 'MVS' 
     and tsv.aliased_item is null
union all
select 'LD 25 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code, 'CAGM7' as damlock
from cwms_v_tsv_dqu  tsv
where 
     tsv.cwms_ts_id = 'LD 25 Pool-Mississippi.Stage.Inst.30Minutes.0.29' 
     and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
     and tsv.office_id = 'MVS' 
     and tsv.aliased_item is null   
union all
select 'Mel Price Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code, 'ALNI2' as damlock
from cwms_v_tsv_dqu  tsv
where 
     tsv.cwms_ts_id = 'Mel Price Pool-Mississippi.Stage.Inst.15Minutes.0.29' 
     and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
     and tsv.office_id = 'MVS' 
     and tsv.aliased_item is null     
order by location_id asc 
FETCH FIRST 3 ROWS ONLY),

 

tainter as 
(select 'LD 24 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code, 'CLKM7' as damlock
from cwms_v_tsv_dqu  tsv
where 
     tsv.cwms_ts_id = 'LD 24 Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
     and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss') 
     and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
     and tsv.office_id = 'MVS' 
     and tsv.aliased_item is null
union all
select 'LD 25 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code, 'CAGM7' as damlock
from cwms_v_tsv_dqu  tsv
where 
     tsv.cwms_ts_id = 'LD 25 Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
     and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
     and tsv.office_id = 'MVS' 
     and tsv.aliased_item is null   
union all
select 'Mel Price Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code, 'ALNI2' as damlock
from cwms_v_tsv_dqu  tsv
where 
     tsv.cwms_ts_id = 'Mel Price Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
     and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
     and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
     and tsv.office_id = 'MVS' 
     and tsv.aliased_item is null     
order by location_id asc 
FETCH FIRST 3 ROWS ONLY)

 


select cte_pool.location_id
    ,cte_pool.date_time
    ,cte_pool.value
    ,cte_pool.unit_id
    ,cte_pool.quality_code
    ,tainter.value as tainter_value
    ,cte_pool.damlock
from cte_pool
left join tainter on cte_pool.location_id = tainter.location_id
                                    ''')
        print "retrieveLD_2"
        print stmt
        rs = stmt.executeQuery()
        
        print "retrieveLD_22"
        
        # create object list to store the data (3 cols by 6 rows)
        object_list_2 = []
        while rs.next() : 
            # loop and append which data col to object list
            object_list_2.append(Object_LD(rs.getString(1),rs.getString(2),rs.getString(3),rs.getString(4),rs.getString(5),None,None))
                     
        print object_list_2
        
        for obj in object_list_2:
            print obj.value7
	
    finally :
        stmt.close()
        rs.close()
    return LD_2


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
        print "lake type = " + str(type(day1.lake))
        print "date_time type = " + str(type(day1.date_time))
        print "outflow type = " + str(type(day1.outflow))

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
    print "retrieveLD test2"
    print lake_dict


    LD_2 = retrieveLD_2(conn)
    print "LD_2" +  str(LD_2)
    
    LD = retrieveLD(conn)
    print "LD" +  str(LD)
    
    
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
        # third_text += "\n\n"
        # fourth_text = TextFile(object_list_1, object_list_2, object_list_3, today_date).line1+"\n"
        # fourth_text += TextFile(object_list_1, object_list_2, object_list_3, today_date).line2+"\n"
        # fourth_text += TextFile(object_list_1, object_list_2, object_list_3, today_date).body
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

#except: 
    #print "error"
 
    
finally :
    try : CwmsDb.done()
    except : pass

    try : CwmsDb.done()
    except : pass

    try : CwmsDb.close()
    except : pass
