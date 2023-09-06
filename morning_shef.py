'''
Author: IVAN H. NGUYEN USACE-MVS
Last Updated: 06-29-2023
Version: 1.5
Description: The purpose of this script is to import data from CWMS and other schema then convert them to SHEF file format.
'''
from ast                                        import IsNot
from decimal                                    import Decimal
from hec.data.cwmsRating                        import RatingSet
from hec.script                                 import MessageBox, Constants, AxisMarker, Plot, Tabulate
from hec.dataTable                              import HecDataTableToExcel      
from hec.dssgui                                 import ListSelection
from hec.data.tx                                import QualityTx
from hec.heclib.util                            import HecTime
from hec.hecmath                                import TimeSeriesMath
from hec.io                                     import TimeSeriesContainer
from hec.script.Constants                       import TRUE, FALSE
from hec.heclib.dss                             import HecDss
from hec.heclib.util                            import HecTime
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
from subprocess                                 import check_call
from time                                       import mktime, localtime
from javax.swing                                import JOptionPane, JDialog, JButton, JPanel, JTextArea, JFrame, JFileChooser 
from datetime                                   import timedelta
from java.awt.event                             import WindowEvent, WindowAdapter
from javax.swing.filechooser                    import FileNameExtensionFilter
from java.io                                    import File
from email.mime.text                            import MIMEText
import inspect, math
import DBAPI
import os
import urllib
import java                                     
import time,calendar,datetime
import java.lang
import os, sys, inspect, datetime, time, DBAPI
import smtplib
#from GUI_test import save_window

#=======================================================================================================================
#=======================================================================================================================
# OBJECTS
#=======================================================================================================================
#=======================================================================================================================

# object class to store current lock and dam stage data. (required 7 data columns)
class Object_LD:
    
    def __init__(self, value1, value2, value3, value4, value5, value6, value7):
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
        self.value4 = value4
        self.value5 = value5
        self.value6 = value6
        self.value7 = value7
        

# object class to store lake forecast flow data. (required 4 data columns)
class Object:
    
    def __init__(self, lake, date_time, outflow, station):
        self.lake = lake
        self.date_time = date_time
        self.outflow = outflow
        self.station = station

#=======================================================================================================================
#=======================================================================================================================
# CLASSES
#=======================================================================================================================
#=======================================================================================================================

# text for 5 lakes
class TextFileLake:
    
    def __init__(self, today_date):
        self.line1 = ": TODAYS LAKE FLOW AND 5 DAY FORECAST"
        self.line2 = ".B STL " + str(today_date) + " C DH0600/DC" + str(today_date) + "0600/QT/DRD+1/QTIF/DRD+2/QTIF/DRD+3/QTIF/DRD+4/QTIF/DRD+5/QTIF"
        self.text = self.line1+"\n"+self.line2 

# text for mark twain yesterday flow
class TextFileMarkTwainYesterday:
    
    def __init__(self, object_list, today_date):
        self.line1 = ": MARK TWAIN LAKE GENERATION YESTERDAY"
        self.line2 = ".E CDAM7 "+str(today_date)+" C DH0000/DC"+str(today_date)+"0000/QTD/DID1/"+"{:.2f}".format(float(object_list[0].outflow)/1000)
        self.mark_twain_text = self.line1+"\n"+self.line2

# text for lock and dam current and forecast data
class TextFileLockDam:
    
    def __init__(self, dictionary, date):
        self.object_1 = dictionary["LockDamStage"]
        self.object_2 = dictionary["LockDamNetmissForecast"]
        self.object_3 = dictionary["HingePoint"]
        self.line1 = ": TODAYS OVSERVED POOL 6AM AND 5 DAY FORECAST IN DATUM NGVD29"
        self.line2 = ".B STL "+ str(date)+" C DH0600/DC0"+str(date)+"700/HP/DRD+1/HPIF/DRD+2/HPIF/DRD+3/HPIF"
        
        self.body = str(self.object_1[0].value7)+"  "+"{:.2f}".format(float(self.object_1[0].value3))+"/"+"{:.2f}".format(float(self.object_2[0].value3))+"/"+"{:.2f}".format(float(self.object_2[1].value3))+"/"+"{:.2f}".format(float(self.object_2[2].value3))+"/"
        self.body += "{:.2f}".format(float(self.object_2[3].value3))+"/"+"{:.2f}".format(float(self.object_2[4].value3))+" : CLARKSVILLE LD 24 --> HINGE PT LOUSIANA "+"{:.1f}".format(float(self.object_3[3].value3))+" - "+"{:.1f}".format(float(self.object_3[2].value3))+" "+str(self.object_3[4].value2).upper()+"\n"
        
        self.body += str(self.object_1[1].value7)+"  "+"{:.2f}".format(float(self.object_1[1].value3))+"/"+"{:.2f}".format(float(self.object_2[5].value3))+"/"+"{:.2f}".format(float(self.object_2[6].value3))+"/"+"{:.2f}".format(float(self.object_2[7].value3))+"/"
        self.body += "{:.2f}".format(float(self.object_2[8].value3))+"/"+"{:.2f}".format(float(self.object_2[9].value3))+" : WINFIELD LD 25 --> HINGE PT MOSIER LDG "+"{:.1f}".format(float(self.object_3[5].value3))+" - "+"{:.1f}".format(float(self.object_3[4].value3))+" "+str(self.object_3[2].value2).upper()+"\n"
        
        self.body += str(self.object_1[2].value7)+"  "+"{:.2f}".format(float(self.object_1[2].value3))+"/"+"{:.2f}".format(float(self.object_2[10].value3))+"/"+"{:.2f}".format(float(self.object_2[11].value3))+"/"+"{:.2f}".format(float(self.object_2[12].value3))+"/"
        self.body += "{:.2f}".format(float(self.object_2[13].value3))+"/"+"{:.2f}".format(float(self.object_2[14].value3))+" : ALTON LD 26 --> HINGE PT GRAFTON "+"{:.1f}".format(float(self.object_3[1].value3))+" - "+"{:.1f}".format(float(self.object_3[0].value3))+" "+str(self.object_3[0].value2).upper()+"\n.END"

# text
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

# text for comments for five lakes
class Lake_comments:
    
    def __init__(self, value1, value2, value3, value4, value5):
        self.text = ""
        self.text = ": CEMVS RESERVOIR NOTES\n"
        self.text += "CARLYLE - "+value1+"\n"
        self.text += "SHELBYVILLE - "+value2+"\n"
        self.text += "MARKTWAIN - "+value3+"\n"
        self.text += "REND - "+value4+"\n"
        self.text += "WAPPAPPELLO - "+value5

# text for comments for five lakes
class LD_comments:
    
    def __init__(self, value1, value2, value3):
        self.text = ""
        self.text = ": CEMVS LD NOTES\n"
        self.text += "LD24 - "+value1+"\n"
        self.text += "LD25 - "+value2+"\n"
        self.text += "MEL PRICE - "+value3+"\n"


# send email setup  
def send_email(body):
    
    print "Send email"

    bodymail = body
    sender     = "NoReply@mvs.usace.army.mil"
    recipients = ["DLL-CEMVS-WATER-MANAGERS@usace.army.mil","allen.phillips@usace.army.mil","oscar.r.cordero-perez@usace.army.mil","jonathon.thornburg@noaa.gov","scott.stockhaus@noaa.gov","brian.connelly@noaa.gov"]
    #recipients = ["sr-orn.all@noaa.gov","DLL-CEMVS-WATER-MANAGERS@usace.army.mil","allen.phillips@usace.army.mil"]
    #recipients = ["ivan.h.nguyen@usace.army.mil"]
    subject    = "MVS Morning Shef Sent to NWS " + str(today_date_full)
    
    print "recipients = " + str(recipients)
    
    message = MIMEText(bodymail)
    message["From"]    = sender
    message["To"]      = ",".join(recipients)
    message["Subject"] = subject
    
    smtp = smtplib.SMTP("gw2.usace.army.mil")
    smtp.sendmail(sender, recipients, message.as_string())
    smtp.quit()
    print "Sent MVS Morning Shef Email."

def save_window(directory, file_name, date, window_name):
    
    # Default Directory    
    save_file = JFileChooser()
    save_file.setDialogTitle(window_name)
    
    file_filter = FileNameExtensionFilter("Shef Files (*.shef)", ["shef"])
    
    save_file.setFileFilter(file_filter)
    
    default_name = File(file_name + "_" + date + ".shef")
    save_file.setSelectedFile(default_name)
    
    # Default Directory    
    default_directory = File(directory)
    save_file.setCurrentDirectory(default_directory)
    dialog_result = save_file.showSaveDialog(None)
    
    
    if dialog_result == JFileChooser.APPROVE_OPTION:
        selected_file = save_file.getSelectedFile()
        
    else:
        MessageBox.showInformation('No path selected. File no created.', 'Alert')
    
    cut_name = str(selected_file).split('.')
    new_name = cut_name[0].split('\\')[-1]
    
    directory = cut_name[0].split('\\')[:-1]
    path = '\\'.join(directory)
    
    file_path = path+"\\"+new_name
    print "File path created"
    
    return file_path


txt_file_name = "morning_shef"

today_date = datetime.datetime.now().strftime('%m%d')
print "today_date = " + str(today_date)

today_date_full = datetime.datetime.now().strftime('%Y%m%d')
print "today_date_full = " + str(today_date_full)


#=======================================================================================================================
#=======================================================================================================================
# DICTIONARY
#=======================================================================================================================
#=======================================================================================================================

# getCarlyle, getWappapello, getRend, getShelbyville, getMarkTwain
lake_dict = {}

# getLockDamStage, getHingePoint, getLockDamNetmissForecast
lock_dam_dict = {}

# getMarkTwainYesterday
markTwainYesterday_list = []

#=======================================================================================================================
#=======================================================================================================================
# QUERY
#=======================================================================================================================
#=======================================================================================================================
def getLockDamStage(conn):
    try :
        print "getLockDamStage Query Start"
        LockDamStage = None
        stmt = conn.prepareStatement('''
                                    with cte_pool as 
                                    (select cwms_util.split_text(cwms_ts_id, 1, '.') as location_id
                                        ,cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT') as date_time
                                        ,value
                                        ,unit_id
                                        ,quality_code
                                        ,'CLKM7' as damlock
                                    from cwms_v_tsv_dqu  tsv
                                    where 
                                         tsv.cwms_ts_id = 'LD 24 Pool-Mississippi.Stage.Inst.30Minutes.0.29'
                                         and tsv.unit_id = 'ft'
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  >= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '06:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  <= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '06:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and tsv.office_id = 'MVS' 
                                         and tsv.aliased_item is null
                                    union all
                                    select cwms_util.split_text(cwms_ts_id, 1, '.') as location_id
                                        ,cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT') as date_time
                                        ,value
                                        ,unit_id
                                        ,quality_code
                                        ,'CAGM7' as damlock
                                    from cwms_v_tsv_dqu  tsv
                                    where 
                                         tsv.cwms_ts_id = 'LD 25 Pool-Mississippi.Stage.Inst.30Minutes.0.29' 
                                         and tsv.unit_id = 'ft'
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  >= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '06:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  <= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '06:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and tsv.office_id = 'MVS' 
                                         and tsv.aliased_item is null 
                                    union all
                                    select cwms_util.split_text(cwms_ts_id, 1, '.') as location_id
                                        ,cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT') as date_time
                                        ,value
                                        ,unit_id
                                        ,quality_code
                                        ,'ALNI2' as damlock
                                    from cwms_v_tsv_dqu  tsv
                                    where 
                                         tsv.cwms_ts_id = 'Mel Price Pool-Mississippi.Stage.Inst.15Minutes.0.29' 
                                         and tsv.unit_id = 'ft'
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  >= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '06:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  <= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '06:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and tsv.office_id = 'MVS' 
                                         and tsv.aliased_item is null     
                                    order by location_id asc 
                                    FETCH FIRST 3 ROWS ONLY),
                                    
                                    tainter as 
                                    (select cwms_util.split_text(cwms_ts_id, 1, '.') as location_id
                                        ,cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT') as date_time
                                        ,value
                                        ,unit_id
                                        ,quality_code
                                        ,'CLKM7' as damlock
                                    from cwms_v_tsv_dqu  tsv
                                    where 
                                         tsv.cwms_ts_id = 'LD 24 Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
                                         and tsv.unit_id = 'ft'
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  >= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '07:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  <= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '07:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and tsv.office_id = 'MVS' 
                                         and tsv.aliased_item is null
                                    union all
                                    select cwms_util.split_text(cwms_ts_id, 1, '.') as location_id
                                        ,cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT') as date_time
                                        ,value
                                        ,unit_id
                                        ,quality_code
                                        ,'CAGM7' as damlock
                                    from cwms_v_tsv_dqu  tsv
                                    where 
                                         tsv.cwms_ts_id = 'LD 25 Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
                                         and tsv.unit_id = 'ft'
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  >= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '07:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  <= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '07:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and tsv.office_id = 'MVS' 
                                         and tsv.aliased_item is null   
                                    union all
                                    select cwms_util.split_text(cwms_ts_id, 1, '.') as location_id
                                        ,cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT') as date_time
                                        ,value
                                        ,unit_id
                                        ,quality_code
                                        ,'ALNI2' as damlock
                                    from cwms_v_tsv_dqu  tsv
                                    where 
                                         tsv.cwms_ts_id = 'Mel Price Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
                                         and tsv.unit_id = 'ft'
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  >= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '07:00:00','mm-dd-yyyy hh24:mi:ss')
                                         and cwms_util.change_timezone(date_time, 'UTC', 'CST6CDT')  <= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'), 'mm-dd-yyyy') || '07:00:00','mm-dd-yyyy hh24:mi:ss')
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
                                    order by cte_pool.location_id asc
                                    ''')
        
        rs = stmt.executeQuery()
        
        # create object list to store the data (3 columns by 6 rows)
        object_list_lock_dam_stage = []
        while rs.next() :
            # ignore tainter value rs.getString(6)
            # exit if you have incomplete forecast data
            # TODO: check to have 3 rows
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(3) == None or rs.getString(4) == None or rs.getString(5) == None or rs.getString(7) == None:
                print "No data for Current LockDamStage"
                MessageBox.showInformation('No data for Current LockDamStage', 'Alert')
                sys.exit()
            else:
                # loop and append which data column to object list
                object_list_lock_dam_stage.append(Object_LD(rs.getString(1),rs.getString(2),rs.getString(3),rs.getString(4),rs.getString(5),rs.getString(6),rs.getString(7)))
        
        lock_dam_dict["LockDamStage"] = object_list_lock_dam_stage
        print lock_dam_dict
        
        for obj in object_list_lock_dam_stage:
            print str(obj.value1) + " - " + str(obj.value2) + " - " + str(obj.value3) + " - " + str(obj.value4) + " - " + str(obj.value5) + " - " + str(obj.value6) + " - " + str(obj.value7)
            
    finally :
        print "getLockDamStage Query End"
        stmt.close()
        rs.close()
    return LockDamStage


def getLockDamNetmissForecast(conn):
    try :
        print "getLockDamNetmissForecast Query Start"
        LockDamNetmissForecast = None
        stmt = conn.prepareStatement('''
                                select upper(cwms_util.split_text(cwms_ts_id, 1, '.')) as location_id
                                    ,date_time
                                    ,value
                                    ,quality_code
                                    ,'CLKM7' as damlock
                                from cwms_v_tsv_dqu
                                where cwms_ts_id ='LD 24 Pool-Mississippi.Elev.Inst.~1Day.0.netmiss-compv2' and unit_id = 'ft'
                                and date_time > to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '0' DAY
                                and date_time < to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '5' DAY
                                union all
                                select upper(cwms_util.split_text(cwms_ts_id, 1, '.')) as location_id
                                    ,date_time
                                    ,value
                                    ,quality_code
                                    ,'CAGM7' as damlock
                                from cwms_v_tsv_dqu
                                where cwms_ts_id ='LD 25 Pool-Mississippi.Elev.Inst.~1Day.0.netmiss-compv2' and unit_id = 'ft'
                                and date_time > to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '0' DAY
                                and date_time < to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '5' DAY
                                union all
                                select upper(cwms_util.split_text(cwms_ts_id, 1, '.')) as location_id
                                    ,date_time
                                    ,value
                                    ,quality_code
                                    ,'ALNI2' as damlock
                                from cwms_v_tsv_dqu
                                where cwms_ts_id ='Mel Price Pool-Mississippi.Elev.Inst.~1Day.0.netmiss-compv2' and unit_id = 'ft'
                                and date_time > to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '0' DAY
                                and date_time < to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '5' DAY
                                    ''')
        rs = stmt.executeQuery()
        
        # create object list to store the data (3 cols by 6 rows)
        object_list_2 = []
        while rs.next() : 
            # exit if you have incomplete forecast data
            # TODO: check to have 15 rows, five for each. ld24, ld25, and mp
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(3) == None or rs.getString(4) == None or rs.getString(5) == None:
                print "No data for LockDamNetmissForecast."
                MessageBox.showInformation('No data for Current LockDamNetmissForecast', 'Alert')
                sys.exit()
            else:
                # loop and append which data col to object list
                object_list_2.append(Object_LD(rs.getString(1),rs.getString(2),rs.getString(3),rs.getString(4),rs.getString(5),None,None))
                      
        lock_dam_dict["LockDamNetmissForecast"] = object_list_2
        print lock_dam_dict
            
        for obj in object_list_2:
            print obj.value1

    finally :
        print "getLockDamNetmissForecast Query End"
        stmt.close()
        rs.close()
    return LockDamNetmissForecast


def getHingePoint(conn):
    try :
        print "getHingePoint Query Start"
        HingePoint = None
        stmt = conn.prepareStatement('''
                                    select location_level_id, level_unit, constant_level, specified_level_id
                                    from CWMS_20.AV_LOCATION_LEVEL 
                                    where specified_level_id in ('Hinge Max','Hinge Min') 
                                    and unit_system = 'EN' 
                                    and location_id in ('Louisiana-Mississippi','Grafton-Mississippi','Mosier Ldg-Mississippi')
                                    ''')
        rs = stmt.executeQuery()
        
        # create object list to store the data (4 columns)
        object_list_hinge_point = []
        while rs.next() : 
            # exit if you have incomplete forecast data
            # TODO: check to have 3 rows
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(3) == None or rs.getString(4) == None:
                print "No data for HingePoint."
                MessageBox.showInformation('No data for HingePoint', 'Alert')
                sys.exit()
            else:
                # loop and append data to object_list
                object_list_hinge_point.append(Object_LD(rs.getString(1),rs.getString(2),rs.getString(3),rs.getString(4),None,None,None))
                     
        lock_dam_dict["HingePoint"] = object_list_hinge_point
        print lock_dam_dict
            
        for obj in object_list_hinge_point:
            print str(obj.value1) + " - " + str(obj.value2) + " - " + str(obj.value3) + " - " + str(obj.value4)
    finally :
        print "getHingePoint Query End"
        stmt.close()
        rs.close()
    return HingePoint


def getCarlyle(conn):
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

        # create object list to store the data (4 columns)
        object_list = []
        while rs.next() :
            # exit if you have incomplete forecast data
            # TODO: check to have 6 rows
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(8) == None or rs.getString(9) == None:
                print "No data for Carlyle"
                MessageBox.showInformation('No data for Carlyle, System Exit', 'Alert')
                sys.exit()
            else:
                # loop and append data to object list. select the correct column number
                object_list.append(Object(rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9)))
                print "Carlyle: append data to object_list"
           
        # add object list to dictionary
        lake_dict["Carlyle"] = object_list
        print lake_dict
        
        print object_list
        
        list_index = len(object_list)
        
        for x in range(0, list_index):
            # create object for each row
            day0 = object_list [x]
            print "day{} = ".format(x) + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
       
    finally :
        stmt.close()
        rs.close()
    return Carlyle


def getWappapello(conn):
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

        # create object list to store the data (4 columns)
        object_list = []
        while rs.next() :
            # exit if you have incomplete forecast data
            # TODO: check to have 6 rows
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(8) == None or rs.getString(9) == None:
                print "No data for Wappappello"
                MessageBox.showInformation('No data for Wappappello, System Exit', 'Alert')
                sys.exit()
            else:
                # loop and append data to object list. select the correct column number
                object_list.append(Object(rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9)))
                print "Wappappello: append data to object_list"
           
        lake_dict["Wappapello"] = object_list
        print lake_dict
        print object_list
        
        list_index = len(object_list)
        
        for x in range(0, list_index):
            # create object for each row
            day0 = object_list [x]
            print "day{} = ".format(x) + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
    
    finally :
        stmt.close()
        rs.close()
    return Wappapello


def getRend(conn):
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

        # create object list to store the data (4 columns)
        object_list = []
        while rs.next() :
            # exit if you have incomplete forecast data
            # TODO: check to have 6 rows
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(8) == None or rs.getString(9) == None:
                print "No data for Rend"
                MessageBox.showInformation('No data for Rend, System Exit', 'Alert')
                sys.exit()
            else:
                # loop and append data to object list. select the correct column number
                object_list.append(Object(rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9)))
                print "Rend: append data to object_list"
           
        lake_dict["Rend"] = object_list
        print lake_dict
        print object_list

        list_index = len(object_list)
        
        for x in range(0, list_index):
            # create object for each row
            day0 = object_list [x]
            print "day{} = ".format(x) + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
            
    finally :
        stmt.close()
        rs.close()
    return Rend


def getShelbyville(conn):
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

        # create object list to store the data (4 columns)
        object_list = []
        while rs.next() :
            # exit if you have incomplete forecast data
            # TODO: check to have 6 rows
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(8) == None or rs.getString(9) == None:
                print "No data for Shelbyville"
                MessageBox.showInformation('No data for Shelbyville, System Exit', 'Alert') 
                sys.exit()
            else:
                # loop and append data to object list. select the correct column number
                object_list.append(Object(rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9)))
                print "Shelbyville: append data to object_list"
           
        lake_dict["Shelbyville"] = object_list
        print lake_dict
        print object_list
        
        list_index = len(object_list)
        
        for x in range(0, list_index):
            # create object for each row
            day0 = object_list [x]
            print "day{} = ".format(x) + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
            
    finally :
        stmt.close()
        rs.close()
    return Shelbyville


def getMarkTwain(conn):
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
                                        and cwms_util.change_timezone(date_time, 'UTC', 'US/Central') >= to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'US/Central'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
                                    order by date_time asc
                                    fetch next 7 row only
                                    ''')
        rs = stmt.executeQuery()

        # create object list to store the data (4 columns)
        object_list = []
        while rs.next() :
            # exit if you have incomplete forecast data
            # TODO: check to have 6 rows
            if rs.getString(1) == None or rs.getString(2) == None or rs.getString(8) == None or rs.getString(9) == None:
                print "No data for MarkTwain"
                MessageBox.showInformation('No data for MarkTwain, System Exit', 'Alert') 
                sys.exit()
            else:
                # loop and append data to object list. select the correct column number
                object_list.append(Object(rs.getString(1),rs.getString(2),rs.getString(8),rs.getString(9)))
                print "MarkTwain: append data to object_list" 
             
        lake_dict["MarkTwain"] = object_list
        print lake_dict
        print object_list

        list_index = len(object_list)
        
        for x in range(0, list_index):
            # create object for each row
            day0 = object_list [x]
            print "day{} = ".format(x) + str(day0.lake) + " - " + str(day0.date_time) + " - " + str(day0.outflow) + " - " + str(day0.station)
            
    finally :
        stmt.close()
        rs.close()
    return MarkTwain


def getMarkTwainYesterday(conn):
    try :
        MarkTwainYesterday = None
        stmt = conn.prepareStatement('''
                                    select 'Mark Twain Lk-Salt' as location_id
                                        , cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time
                                        , value
                                        , unit_id
                                        , 'CDAM7' as station
                                    from cwms_v_tsv_dqu  tsv
                                    where 
                                         tsv.cwms_ts_id = 'Mark Twain Lk-Salt.Flow-Turb.Ave.~1Day.1Day.lakerep-rev' 
                                         and date_time  >= to_date( to_char(sysdate-2, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss') 
                                         and date_time  <= to_date( to_char(sysdate-1, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
                                         and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
                                         and tsv.office_id = 'MVS' 
                                         and tsv.aliased_item is null
                                    ''')
        rs = stmt.executeQuery()

        # create object list to store the data (4 columns)
        while rs.next() :
            # exit if you have incomplete forecast data
            # TODO: check to have 1 rows
            if rs.getString(3) == None or rs.getString(5) == None:
                print "No data for MarkTwainYesterday."
                MessageBox.showInformation('No data for MarkTwainYesterday, System Exit', 'Alert') 
                sys.exit()
            else:
                # loop and append data to object list. select the correct column number
                markTwainYesterday_list.append(Object(None, None,rs.getString(3),rs.getString(5)))
                print "test"  
             
        print markTwainYesterday_list
        
        list_index = len(markTwainYesterday_list)
        
        for x in range(0, list_index):
            # create object for each row
            day0 = markTwainYesterday_list [x]
            print "day{} = ".format(x) + str(day0.station) + " - " + str(day0.outflow)        

    finally :
        stmt.close()
        rs.close()
    return MarkTwainYesterday


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
    
    # create a java.sql.Connection
    conn = CwmsDb.getConnection()

    # get LockDamStage data
    LockDamStage = getLockDamStage(conn)
    print "LockDamStage = " +  str(LockDamStage)
    
    print "==========================================================="

    # get LockDamNetmissForecast data
    LockDamNetmissForecast = getLockDamNetmissForecast(conn)
    print "LockDamNetmissForecast = " +  str(LockDamNetmissForecast)
    
    print "==========================================================="
    
    # get HingePoint data
    Hinge = getHingePoint(conn)
    print "Hinge = " +  str(Hinge)
    
    print "==========================================================="    
    
    # get Carlyle data
    Carlyle = getCarlyle(conn)
    print "Carlyle = " +  str(Carlyle)
    
    print "==========================================================="

    # get Wappapello data
    Wappapello = getWappapello(conn)
    print "Wappapello = " +  str(Wappapello)
    
    print "==========================================================="
    
    # get Rend data
    Rend = getRend(conn)
    print "Rend = " +  str(Rend)
    
    print "==========================================================="

    # get Shelbyville data
    Shelbyville = getShelbyville(conn)
    print "Shelbyville = " +  str(Shelbyville)
    
    print "==========================================================="
    
    # get MarkTwain data
    MarkTwain = getMarkTwain(conn)
    print "MarkTwain = " +  str(MarkTwain)
    
    print "==========================================================="
    
    # get MarkTwainYesterday data
    MarkTwainYesterday = getMarkTwainYesterday(conn)
    print "MarkTwainYesterday = " +  str(MarkTwainYesterday)
    
    print "==========================================================="
    
    #=======================================================================================================================
    #=======================================================================================================================
    # NOTE WINDOW FOR FIVE LAKES
    #=======================================================================================================================
    #=======================================================================================================================

    noteCarlyle = JOptionPane.showInputDialog(None, 'Carlyle Lake Note', 'CEMVS Reservoir Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteCarlyle = " + str(noteCarlyle)
    
    noteShelbyville = JOptionPane.showInputDialog(None, 'Shelbyville Lake Note', 'CEMVS Reservoir Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteShelbyville = " + str(noteShelbyville)
    
    noteMarkTwain = JOptionPane.showInputDialog(None, 'MarkTwain Lake Note', 'CEMVS Reservoir Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteMarkTwain = " + str(noteMarkTwain)
    
    noteRend = JOptionPane.showInputDialog(None, 'Rend Lake Note', 'CEMVS Reservoir Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteRend = " + str(noteRend)
    
    noteWappapello = JOptionPane.showInputDialog(None, 'Wappapello Lake Note', 'CEMVS Reservoir Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteWappapello = " + str(noteWappapello)
    
    
    
    noteLD24 = JOptionPane.showInputDialog(None, 'LD 24 Note', 'CEMVS LD Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteLD24 = " + str(noteLD24)
    
    noteLD25 = JOptionPane.showInputDialog(None, 'LD 25 Note', 'CEMVS LD Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteLD25 = " + str(noteLD25)
    
    noteLDMelPrice = JOptionPane.showInputDialog(None, 'LD Mel Price Note', 'CEMVS LD Notes', JOptionPane.PLAIN_MESSAGE, None, None, 'Nothing to report')
    print "noteLDMelPrice = " + str(noteLDMelPrice)
    
    
    #=======================================================================================================================
    # CREATE TEXT FILE
    #=======================================================================================================================
     
    # Variable to hold any changes for the text file
    holdText = ""
    
    # Create text for the txt file
    text = TextFileLake(today_date).text+"\n"
    data_text = ""
    for key, value in lake_dict.items():
        data_text += TextFileButton(value).text+"\n"
    end_text = ".END"
    text += data_text
    text += end_text
    text += "\n\n"
    
    # mark twain current shef data block
    mark_twain_text = TextFileMarkTwainYesterday(markTwainYesterday_list, today_date).mark_twain_text
    mark_twain_text += "\n\n"
    
    # lock and dam current and forecast shef data block
    lock_dam_text =  TextFileLockDam(lock_dam_dict, today_date).line1+"\n"
    lock_dam_text += TextFileLockDam(lock_dam_dict, today_date).line2+"\n"
    lock_dam_text += TextFileLockDam(lock_dam_dict, today_date).body
    lock_dam_text += "\n\n"
    
    # Lake Comments
    lakes_comments = Lake_comments(str(noteCarlyle), str(noteShelbyville), str(noteMarkTwain), str(noteRend), str(noteWappapello)).text
    lakes_comments += "\n\n"
    
    
    # LD Comments
    ld_comments = LD_comments(str(noteLD24), str(noteLD25),str(noteLDMelPrice)).text
    ld_comments += "\n\n"
    
    # The complete text for the shef file
    final_text = text+mark_twain_text+lakes_comments+lock_dam_text+ld_comments
    
    
    # Window to show and modify the text file
    class MyWindowListener(WindowAdapter):
        
        def windowClosing(self, event):
            global holdText
            holdText = textArea.getText()
            
            dialogButton = JOptionPane.showConfirmDialog(None, "Do you want to send it?")
            
            if dialogButton == 2:
                print "Decision: 'Cancel'\nClosing window"
            elif dialogButton == 1:
                print "Decision: 'No'\nClosing window"
            else:
                print "Decision: 'Yes'\nClosing window"
                
                #===================================================================================
                # SEND, UPLOAD, AND PUBLISH
                #==================================================================================
                print '='
                print '='
                print '='
                print '=================================================================================='
                print '============================== SEND, UPLOAD, AND PUBLISH'
                print '================================================================================== '
                print '='
                print '='
                print '='
                
                # Check if is in Server or Local 
                print '=== Determine if OS is Windows or Unix ==='
                OsName = System.getProperty("os.name").lower()
        
                print 'OS is Windows or Unix = ', OsName
                
                # If OS is PC, else UNIX Server
                if OsName[ : 7] == 'windows' :
                    
                    txt_date = datetime.datetime.now().strftime('%Y%m%d')
                    
                    '''
                    # Save Window For C Drive
                    # Default Directory
                    c_directory = "C:/scripts/cwms/morning_shef"
                    
                    pop_name = "Save in C Drive"
                    first_save_path = save_window(c_directory, txt_file_name, txt_date, pop_name)
                    
                    with open(first_save_path + ".shef", "w") as f:
                        f.write(holdText)
                    '''
                    
                    # Create Text File, directory setup
                    z_directory = "Z:\\DailyOps\\morning_shef"
                    file_name = txt_file_name + ".shef"
                    file_name_with_date = txt_file_name + "_" + txt_date + ".shef"
                    
                    # save file to z drive
                    with open(z_directory + "\\" + file_name, "w") as f:
                        f.write(holdText)
                    
                    with open(z_directory + "\\" + file_name_with_date, "w") as f:
                        f.write(holdText)
                        
                    # Send Email function will give error when run in Eclipse. Comment out send_email when run 
                    send_email(holdText)
    
                    # push shef to public site
                    cmd = "pscp -i C:\\wc\\ssh\\id_rsa.ppk Z:/DailyOps/morning_shef/" + file_name + " " + "d1wm1a95@199.124.16.152:/I:/web/mvs-wc/inetpub/wwwroot/" + file_name
                    print(cmd)
                    check_call(cmd, shell=True)
                    
                    cmd2 = "pscp -i C:\\wc\\ssh\\id_rsa.ppk Z:/DailyOps/morning_shef/" + file_name + " " + "d1wm1a95@199.124.16.152:/I:/web/mvs-wc/inetpub/wwwroot/" + file_name + ".txt"
                    print(cmd2)
                    check_call(cmd2, shell=True)
                    
                    MessageBox.showInformation('Text File Created and Email Was Sent', 'Alert') 
                    
                    print '='
                    print '='
                    print '='
                    print '=================================================================================='
                    print '============================== SCRIPT END'
                    print '================================================================================== '
                    print '='
                    print '='
                    print '='
    
                else:
                    MessageBox.showInformation('Error, Run the script in CWMS-VUE', 'Alert')
    
    # Window
    frame = JFrame("GUI", size = (1080, 650))
    
    textArea = JTextArea(final_text)
    frame.add(textArea)
    
    window_listener = MyWindowListener()
    
    frame.addWindowListener(window_listener)
    
    frame.visible = True
    
    # close the database
    CwmsDb.close()
    
    print "===================================================="    
    
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
