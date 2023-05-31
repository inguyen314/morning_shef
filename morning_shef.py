'''
Author: IVAN H. NGUYEN USACE-MVS
Last Updated: 05-22-2023
Version: 2.1
Description: The purpose of this script is to import data from CWMS and other schema then convert them to SHEF file format.
'''
from ast                                        import IsNot
from decimal                                    import Decimal
from hec.data.cwmsRating                        import RatingSet
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


#================================================================================
# Step 1: Get data from cwms_db
#================================================================================


#================================================================================
# Step 2: Get data from lake schema
#================================================================================


#================================================================================
# Step 3: Combine data
#================================================================================


#================================================================================
# Step 4: Convert data to SHEF format
#================================================================================


# Set the command line arguments for the script
CwmsHome = os.environ['CWMS_HOME']

print 'CwmsHome = ' + str(CwmsHome)

print 'CwmsHome = ' + str(CwmsHome)



#CwmsHomeParts = CwmsHome.split('\\')
#CwmsHome = '\\'.join(CwmsHomeParts[ : -1])
#ExportShefDirectory = os.path.join(CwmsHome, 'common\\exe\\exportSHEF.py')
#outputDebug(debug, lineNo(), 'CwmsHome = ', CwmsHome, '\nExportShefDirectory = ', ExportShefDirectory)

# NWO Share
#try : 
    #sys.argv = [
                #ExportShefDirectory,
                #'in=%s' % RCC_Programs_Directories['GRFT Files']['GRFT_SHEF_Input.txt']['NWO'],
                #'out=%s' % RCC_Programs_Directories['GRFT Files']['GRFT_SHEF.txt']['NWO']
                #]
    
    # Read the text of the script to run
    #with open(sys.argv[0]) as f : script_text = f.read()

    # Replace any exit() or System.exit(...) calls with a "pass" statement to keep from exiting JVM
    #exit_pattern = re.compile("(:|\\s*)((?:sys\\.)?exit\\(.*?\\)|System\\.exit\\(.+?\\))")
    #script_text = exit_pattern.sub("\\1pass", script_text)
    #script_text += '\noutfile.close()'

    # Execute the modified script with the specified command line
    #exec(script_text)
    #outputDebug(True, lineNo(), 'SHEF file written to NWO Public')
#except :
    #outputDebug(True, lineNo(), 'SHEF file did not write to NWO Public')
    #exc_type, exc_value, exc_traceback = sys.exc_info()
    #traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)











#================================================================================
# QUERY FUNCTIONS TO GET DATA TO BE CONVERT TO SHEF FORMAT
#================================================================================

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
        while rs.next() : 
            Carlyle = rs.getString(1)
            break 
    finally :
        stmt.close()
        rs.close()
    return Carlyle


def retrieveShelbyville(conn):
    try :
        Shelbyville = None
        stmt = conn.prepareStatement('''
                                    select lake, to_char(date_time, 'mm-dd-yyyy') as date_time, outflow
                                    from wm_mvs_lake.qlev_fcst where lake = 'SHELBYVILLE' and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
                                    order by date_time asc
                                    fetch next 6 row only
                                    ''')
        rs = stmt.executeQuery()
        while rs.next() : 
            Shelbyville = rs.getString(1)
            break 
    finally :
        stmt.close()
        rs.close()
    return Shelbyville


def retrieveRend(conn):
    try :
        Rend = None
        stmt = conn.prepareStatement('''
                                    select lake, to_char(date_time, 'mm-dd-yyyy') as date_time, outflow
                                    from wm_mvs_lake.qlev_fcst where lake = 'REND' and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
                                    order by date_time asc
                                    fetch next 6 row only
                                    ''')
        rs = stmt.executeQuery()
        while rs.next() : 
            Rend = rs.getString(1)
            break 
    finally :
        stmt.close()
        rs.close()
    return Rend


def retrieveWappapello(conn):
    try :
        Wappapello = None
        stmt = conn.prepareStatement('''
                                    select lake, to_char(date_time, 'mm-dd-yyyy') as date_time, outflow
                                    from wm_mvs_lake.qlev_fcst where lake = 'WAPPAPELLO' and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
                                    order by date_time asc
                                    fetch next 6 row only
                                    ''')
        rs = stmt.executeQuery()
        while rs.next() : 
            Wappapello = rs.getString(1)
            break 
    finally :
        stmt.close()
        rs.close()
    return Wappapello


def retrieveMarkTwain(conn):
    try :
        MarkTwain = None
        stmt = conn.prepareStatement('''
                                    select 'MARK TWAIN' as lake, to_char(date_time, 'mm-dd-yyyy') as date_time, outflow
                                    from wm_mvs_lake.qlev_fcst where lake = 'MT' and cwms_util.change_timezone(fcst_date, 'UTC', 'US/Central') = to_date(to_char(cwms_util.change_timezone(sysdate, 'UTC', 'CST6CDT'),'mm-dd-yyyy') || '00:00:00','mm-dd-yyyy hh24:mi:ss')
                                    order by date_time asc
                                    fetch next 7 row only
                                    ''')
        rs = stmt.executeQuery()
        while rs.next() : 
            MarkTwain = rs.getString(1)
            break 
    finally :
        stmt.close()
        rs.close()
    return MarkTwain


def retrieveLDPool(conn):
    try :
        LDPool = None
        stmt = conn.prepareStatement('''
                                    with cte_pool as 
                                        (select 'LD 24 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code
                                        from cwms_v_tsv_dqu  tsv
                                        where 
                                             tsv.cwms_ts_id = 'LD 24 Pool-Mississippi.Stage.Inst.30Minutes.0.29' 
                                             and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss') 
                                             and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
                                             and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
                                             and tsv.office_id = 'MVS' 
                                             and tsv.aliased_item is null
                                        union all
                                        select 'LD 25 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code
                                        from cwms_v_tsv_dqu  tsv
                                        where 
                                             tsv.cwms_ts_id = 'LD 25 Pool-Mississippi.Stage.Inst.30Minutes.0.29' 
                                             and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
                                             and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
                                             and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
                                             and tsv.office_id = 'MVS' 
                                             and tsv.aliased_item is null   
                                        union all
                                        select 'Mel Price Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code
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
                                        (select 'LD 24 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code
                                        from cwms_v_tsv_dqu  tsv
                                        where 
                                             tsv.cwms_ts_id = 'LD 24 Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
                                             and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss') 
                                             and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
                                             and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
                                             and tsv.office_id = 'MVS' 
                                             and tsv.aliased_item is null
                                        union all
                                        select 'LD 25 Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code
                                        from cwms_v_tsv_dqu  tsv
                                        where 
                                             tsv.cwms_ts_id = 'LD 25 Pool-Mississippi.Opening.Inst.~2Hours.0.lpmsShef-raw-Taint' 
                                             and date_time  >= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
                                             and date_time  <= to_date( to_char(sysdate, 'mm-dd-yyyy') || '12:00:00' ,'mm-dd-yyyy hh24:mi:ss')
                                             and (tsv.unit_id = 'ppm' or tsv.unit_id = 'F' or tsv.unit_id = 'ft' or tsv.unit_id = 'cfs' or tsv.unit_id = 'umho/cm' or tsv.unit_id = 'volt')
                                             and tsv.office_id = 'MVS' 
                                             and tsv.aliased_item is null   
                                        union all
                                        select 'Mel Price Pool-Mississippi' as location_id, cwms_util.change_timezone(tsv.date_time, 'UTC', 'CST6CDT') date_time, value, unit_id, quality_code
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
                                        from cte_pool
                                        left join tainter on cte_pool.location_id = tainter.location_id
                                    ''')
        rs = stmt.executeQuery()
        while rs.next() : 
            LDPool = rs.getString(1)
            break 
    finally :
        stmt.close()
        rs.close()
    return LDPool


def retrieveLDPoolForecast(conn):
    try :
        LDPoolForecast = None
        stmt = conn.prepareStatement('''
                                    select 'LD 24 Pool-Mississippi' as location_id, date_time, value, quality_code 
                                    from table(rdl.timeseries.getReportDataByType ('TIME_SERIES', 'LD 24 Pool-Mississippi.Elev.Inst.~1Day.0.netmiss-compv2', 
                                        to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') - interval '0' DAY,
                                        to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '5' DAY, 
                                        null, 
                                        null,--TOD time 
                                        null, 
                                        null, 
                                        'ft',--unit 
                                        'MVS',--office_id 
                                        'CST6CDT')--timezone
                                        )
                                        
                                    union all
                                    
                                    select 'LD 25 Pool-Mississippi' as location_id, date_time, value, quality_code 
                                    from table(rdl.timeseries.getReportDataByType ('TIME_SERIES', 'LD 25 Pool-Mississippi.Elev.Inst.~1Day.0.netmiss-compv2', 
                                        to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') - interval '0' DAY,
                                        to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '5' DAY, 
                                        null, 
                                        null,--TOD time 
                                        null, 
                                        null, 
                                        'ft',--unit 
                                        'MVS',--office_id 
                                        'CST6CDT')--timezone
                                        )
                                        
                                    union all
                                    
                                    select 'Mel Price Pool-Mississippi' as location_id, date_time, value, quality_code 
                                    from table(rdl.timeseries.getReportDataByType ('TIME_SERIES', 'Mel Price Pool-Mississippi.Elev.Inst.~1Day.0.netmiss-compv2', 
                                        to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') - interval '0' DAY,
                                        to_date( to_char(sysdate, 'mm-dd-yyyy hh24:mm:ss') ,'mm-dd-yyyy hh24:mi:ss') + interval '5' DAY, 
                                        null, 
                                        null,--TOD time 
                                        null, 
                                        null, 
                                        'ft',--unit 
                                        'MVS',--office_id 
                                        'CST6CDT')--timezone
                                        )
                                    ''')
        rs = stmt.executeQuery()
        while rs.next() : 
            LDPoolForecast = rs.getString(1)
            break 
    finally :
        stmt.close()
        rs.close()
    return LDPoolForecast








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
    
    # hard coded the start and end time window
    mysdate = '01Jan2015 0000'
    myedate = '31Dec2016 2400'

    print 'mysdate = ' + mysdate
    print 'myedate = ' + myedate
  
    # setup time window with start and end date
    CwmsDb.setTimeWindow(mysdate,myedate)
    
    # get Carlyle data
    Carlyle = retrieveCarlyle(conn)
    print "Carlyle" +  str(Carlyle)

    
    
finally :
    try : CwmsDb.done()
    except : pass

    try : CwmsDb.done()
    except : pass