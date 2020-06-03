import datetime
import glob
import os
import sqlite3
from pathlib import Path
from tkinter import (END, Button, Entry, Frame, Label, LabelFrame, PhotoImage,
                     Tk, filedialog, messagebox, ttk)

import messages
import scorecalc
import utils
from logman import exitlogman, logger

# Global static variables
PROJECT_ROOT = os.getcwd()
SERVER = "Storage"
CONFIG = "ConfigFiles"
EXPORTS = "Exports"
BACKUPS = "Backups"
ATHLETE_ICON_FILE = "athlete.png"
SCHEMA_FILE = "schema.properties"
SETTINGS_FILE = "settings.properties"
FIELDMAP_FILE = "fieldmap.properties"

# Root Window
window = Tk()

# Title remains static against all frames. No changing
titlelabel = Label(window, text="Middle School Student Sports Data Organizer", font=(
    "Roboto", 18, "bold"), fg="#590004", bg="#969A97")
titlelabel.pack()

# Global variables
currdb = None
currtable = None
dbconn = None
loadfilename = None
exportfolder = EXPORTS
recordDict = {}







################################## ENTRY VALIDATORS ##############################################################
def validateDBName(inp):
    if(inp == ""):
        return True
    elif(inp[-1].isalpha() or inp[-1].isdigit()):
        return True
    else:
        return False
    
def validateRoll(inp):
	if(inp.isdigit()):
		return True
	elif(inp == ""):
		return True
	else:
		return False

def validateName(inp):
	if(inp.isalpha()):
		return True
	elif(inp == ""):
		return True
	else:
		return False

def validateValues(inp):
	if(inp.isdigit()):
		return True
	elif((inp.replace('.', '', 1)).isdigit()):
		return True
	elif(inp == ""):
		return True
	else:
		return False

def validateExcelFileName(inp):
    if(inp == ""):
        return True
    elif(inp[-1].isalpha() or inp[-1].isdigit() or inp[-1] == "-"):
        return True
    else:
        return False







################################# DATABASE & TABLE CREATION/SELECTION ###################################################
# When setting up for the first time, this handles Database creation & persists the dbconn variable
def createDB(dataLabel, dbname):
    # create a new db and pop an info/error message with the Path
    global currtable
    global dbconn
    global currdb
    
    if dbconn != None:
        logger.info(messages.DB_DETAILS_CLEAN.format(currdb,currtable))
        dbconn.close()
        currdb = None
        currtable = None
    
    if(dbname != "" and dbname != None):
        serverdir = PROJECT_ROOT + os.path.sep + SERVER

        if not (dbname.endswith(".db")):
            dbname = dbname + ".db"
            
        logger.info(messages.USER_GIVEN_DBNAME.format(dbname))
        
        dbpath = Path(serverdir + os.path.sep + dbname)
        dbconn = utils.connectwithDB(dbpath)
        if dbconn:
            currdb = dbname
            logger.info(messages.CURRDB_VALUE.format(currdb))
            dataLabel.configure(text="Successfully connected to " + currdb + " database")
    else:
        dataLabel.configure(text="Currently not connected to any Database")
        logger.warning(messages.INVALID_DB_NAME_ENTERED.format(dbname))
        messagebox.showinfo(title='INVALID DB NAME', message=messages.INVALID_DB_NAME)

# Opens a dbconn with the given DB name and persists the connection else throws an error.
def selectDB(dataLabel):
    # open the DB. and open an connection. Store it as a global variable. Show error message
    global currtable
    global dbconn
    global currdb

    if dbconn != None:
        logger.info(messages.DB_DETAILS_CLEAN.format(currdb,currtable))
        dbconn.close()
        currdb = None
        currtable = None
        
    serverdir = PROJECT_ROOT + os.path.sep + SERVER
    filepattern = serverdir + os.path.sep + "*.db"
    
    if not (glob.glob(filepattern)):
        logger.warning(messages.NO_DB_EXISTS)
        messagebox.showerror(title="No DATABASE PRESENT", message=messages.NO_DB_EXISTS)
        return
    else:
        dbpath =  filedialog.askopenfilename(initialdir=Path(SERVER), title="Select an Database file", filetypes=(("SQLite3 Databases", "*.db"),))
        if dbpath == '':
            logger.warn(messages.INVALID_DB_SELECTION)
            messagebox.showinfo(title="INVALID_DB_SELECTION", message = messages.INVALID_DB_SELECTION)
            dataLabel.configure(text="Currently not connected to any Database")
            return
        else:
            dbname = os.path.basename(Path(dbpath))
            dbconn = utils.connectwithDB(dbpath)
        if dbconn:
            currdb = dbname
            logger.info(messages.CURRDB_VALUE.format(currdb))
            dataLabel.configure(text="Successfully connected to " + currdb + " database")

# Creates a table if not exists with the class/term/year details as the name    
def processtabledetails(klass, term, year, dataLabel):

    if(dbconn == None or currdb == None):
        logger.warning(messages.SELECT_DB_FIRST)
        messagebox.showinfo(title="SELECT A DATABASE FIRST", message=messages.SELECT_DB_FIRST)
        return

    global currtable
    if currtable != None:
        logger.info(messages.TABLE_DETAILS_CLEAN.format(currtable))
        currtable = None
    
    tablename = "class_" + klass + "_term_" + term + "_year_" + year
    
    schemaFile = Path(PROJECT_ROOT + os.path.sep + CONFIG + os.path.sep + SCHEMA_FILE)
    result = utils.createtable(dbconn, tablename, schemaFile)
    
    if(result == True):
        currtable = tablename
        logger.info(messages.CURRTABLE_VALUE.format(currtable))
        dataLabel.configure(text="Connected to the Table " + currtable + " \npresent in the Database " + currdb)
    else:
        messagebox.showerror(title="TABLE_SELECTION_ERROR",message=messages.TABLE_SELECTION_ERROR)
        currtable = None








#################################### LOAD DATA WIDGETS ############################################################# 
# Choose the Excel workbook from which the data is to be imported
def chooseFile(filedisplay):
    global loadfilename
    
    if loadfilename != None:
        logger.info(messages.LOADFILE_CLEAR.format(loadfilename))
        loadfilename = None

    chosenfile =  filedialog.askopenfilename(initialdir=Path(PROJECT_ROOT), title="Select an Excel file", filetypes=(("Excel workbook", "*.xlsx"),))

    if chosenfile == None or chosenfile == "":
        logger.warning(messages.NO_EXCEL_FILE_SELECTED)
        messagebox.showinfo(title="NO_EXCEL_FILE_SELECTED",message=messages.NO_EXCEL_FILE_SELECTED)
        loadfilename = None
    else:
        loadfilename = chosenfile
        logger.info(messages.LOADFILE_VALUE.format(loadfilename))
        filedisplay.configure(text="The Student data will be imported from \n " + loadfilename)

# Load data will prompt you to choose XLSX file and upload it to the current table
def loadData(filedisplay):

    global loadfilename
    if(loadfilename == None or loadfilename == ""):
        messagebox.showinfo(title="NO_EXCEL_FILE_SELECTED",message=messages.NO_EXCEL_FILE_SELECTED)
        logger.warning(messages.NO_EXCEL_FILE_SELECTED)
        return

    fieldmapfile = Path(PROJECT_ROOT + os.path.sep + CONFIG + os.path.sep + FIELDMAP_FILE)
    insertedrows, rowstoload = utils.exceltosql(dbconn, currtable, loadfilename, fieldmapfile)

    result = (insertedrows == rowstoload)

    if(result == True):
        logger.info(messages.DATA_LOAD_PASS.format(insertedrows, currtable, loadfilename))
        filedisplay.configure(text= str(insertedrows) + " records have been successfully uploaded to \n" + currtable)
    else:
        logger.info(messages.DATA_LOAD_FAIL.format(insertedrows, currtable, loadfilename))
        messagebox.showerror(title="DATA_UPLOAD_ERROR",message=messages.DATA_UPLOAD_ERROR.format(insertedrows,rowstoload))

# Loader Page - Offers file selection via Windows explorer and Record loading option
def loader():
    global loadfilename
    
    if loadfilename != None:
        logger.info(messages.LOADFILE_CLEAR.format(loadfilename))
        loadfilename = None

    # topframe which provides the student file upload utility
    topframe = Frame(window, bg="#80c1ff")
    topframe.place(rely=0.06, relx=0.015, relwidth=0.97, relheight=0.22)

    searchButton = Button(topframe, text="Choose Data File", font=("Roboto", 14, "bold"), fg="Brown", bg="#54EE4A", bd=5, relief="raised", command=lambda: chooseFile(filedisplay))
    searchButton.place(relx=0.25, rely=0.32, relwidth=0.50, relheight=0.30)

    middleframe = LabelFrame(window, bg="#acdcdc", text="File Path", font=("Roboto", 13, "bold"))
    middleframe.place(rely=0.30, relx=0.015, relwidth=0.97, relheight=0.16)

    filedisplay = Label(middleframe, bg="#acdcdc", text="No Chosen File", font=("Comic Sans MS", 14))
    filedisplay.pack()

    bottomframe = Frame(window, bg="#BC04BF")
    bottomframe.place(rely=0.48, relx=0.015, relwidth=0.97, relheight=0.51)

    loadDataButton = Button(bottomframe, text="Upload data to DB", font=("Roboto", 14, "bold"), fg="Brown", bg="#54EE4A", bd=5, relief="raised", command=lambda: loadData(filedisplay))
    loadDataButton.place(rely=0.25, relx=0.25, relheight=0.15, relwidth=0.50)

    backButton =  Button(bottomframe, text="Back to Homepage", font=("Roboto", 14, "bold"), fg="Brown", bg="#54EE4A", bd=5, relief="raised", command=lambda:callHomescreen(allframes))
    backButton.place(rely=0.50, relx=0.25, relheight=0.15, relwidth=0.50)

    allframes = []
    allframes.append(middleframe)
    allframes.append(topframe)
    allframes.append(bottomframe)







####################################### UPDATE RECORD WIDGETS  ######################################################

def updateStudentDisplay(dataLabel, schemaList, studentRecord):
    
    global recordDict
    
    if len(recordDict) > 0:
        recordDict.clear()
        logger.info(messages.RECORD_DICT_CLEAR)
    
    displayData = ""
    
    if ((len(schemaList) < 7) or (len(studentRecord) < 7)):
        logger.critical(messages.INSUFFICIENT_FIELDS_FOR_UPDATE.format(str(len(schemaList)), str(len(studentRecord))))
        return
         
    for i in range(0,4):
        displayData = displayData + schemaList[i] + " : " + str(studentRecord[i]) + " | "
    displayData = displayData + "\n"
    for i in range(4,7):
        displayData = displayData + schemaList[i] + " : " + str(studentRecord[i]) + " | "
        
    dataLabel.configure(text=displayData)
    tempDict = {schemaList[i]: studentRecord[i] for i in range(len(studentRecord))}
    
    recordDict.update(tempDict)
    del tempDict

#Gets roll number and/or name, and searches for student
def searchStudent(rollEntry, nameEntry, dataLabel):
    
    studentRoll = rollEntry.get()
    studentName = nameEntry.get()
    nameEntry.delete(0, END)
    rollEntry.delete(0, END)

    if(studentRoll == ""):
        logger.warn(messages.INVALID_ENTRY)
        messagebox.showerror(title="INVALID_ENTRY", message=messages.INVALID_ENTRY)
        return

    studentRecord = utils.getStudentRecord(dbconn, currtable, studentRoll, studentName)
    schema = utils.getSchemaFromTable(dbconn, currtable)
    
    if studentRecord == None:
        logger.warn(messages.STUDENT_RECORD_EMPTY)
        return
    if not schema:  
        logger.warn(messages.SCHEMA_EMPTY)
        return

    updateStudentDisplay(dataLabel, schema, studentRecord)

# Used to collect sports data and updated corresponding student record
def updateStudentData(heightEntry, speedEntry, enduranceEntry, strengthEntry, explosiveEntry, agilityEntry, dataLabel):

    global recordDict

    height = heightEntry.get()
    fiftytime = speedEntry.get()
    eighthundredtime = enduranceEntry.get()
    shotputdist = strengthEntry.get()
    longjumpdist = explosiveEntry.get()
    agilitytime = agilityEntry.get()
    
    logger.info(messages.UPDATE_VALUES.format(height, fiftytime, eighthundredtime, shotputdist, longjumpdist, agilitytime))

    if(height == "" and fiftytime == "" and eighthundredtime == "" and shotputdist == "" and longjumpdist == "" and agilitytime == ""):
        messagebox.showerror(title="EMPTY_VALUES", message=messages.EMPTY_VALUES)
        return
    
    if not recordDict:
        messagebox.showerror(title="NO_STUDENT_CHOSEN", message=messages.NO_STUDENT_CHOSEN)
        return

    updateQueries, recordDict = utils.getUpdateQueries(height, fiftytime, eighthundredtime, shotputdist, longjumpdist, agilitytime, recordDict)
    logger.info(messages.UPDATE_QUERY_NUM.format(len(updateQueries)))
    
    finalupdatequery = utils.formUpdateQuery(currtable, updateQueries, recordDict)
    logger.info(messages.UPDATE_QUERY.format(finalupdatequery))
    
    result = utils.updateTable(dbconn, finalupdatequery)
    
    if result:
        logger.info(messages.UPDATE_RECORD_PASS.format(finalupdatequery))
        dataLabel.config(text="Student Record was updated Successfully")
        return
    else:
        messagebox.showerror(title="UPDATE_FAILED", message=messages.UPDATE_FAILED)
        return
    
# Updater Page element - Offers search and update functionality
def updater():

    # Upper portion which provides the Student search utility
    topframe = Frame(window, bg="#80c1ff")
    topframe.place(rely=0.05, relx=0.015, relwidth=0.97, relheight=0.23)

    rollLabel = Label(topframe, text="Enter Student's Roll number : ", bg="#80c1ff", font=("Roboto", 13, "bold"), anchor='w')
    rollLabel.place(relx=0.10, rely=0.12, relwidth=0.40, relheight=0.15)
    rollEntry = Entry(topframe, font=("Calibri 15"))
    rollEntry.place(relx=0.47, rely=0.12, relwidth=0.35, relheight=0.15)

    rollreg = topframe.register(validateRoll)
    rollEntry.config(validate="key",validatecommand=(rollreg,'%P'))

    nameLabel = Label(topframe, text="Enter Student's name : ", bg="#80c1ff", font=("Roboto", 13, "bold"), anchor='w')
    nameLabel.place(relx=0.10, rely=0.40, relwidth=0.30, relheight=0.15)
    nameEntry = Entry(topframe, font=("Calibri 15"))
    nameEntry.place(relx=0.47, rely=0.40, relwidth=0.35, relheight=0.15)

    namereg = topframe.register(validateName)
    nameEntry.config(validate="key",validatecommand=(namereg,'%P'))

    searchButton = Button(topframe, text="Search", font=("Roboto", 13, "bold"), fg="White", bg="#49306B", bd=5, relief="ridge", command=lambda: searchStudent(rollEntry, nameEntry, dataLabel))
    searchButton.place(relx=0.35, rely=0.72, relwidth=0.3, relheight=0.20)

    # Middle frame which displays student record data
    middleframe = LabelFrame(window, bg="#acdcdc", text="Student Data", font=("Roboto", 12, "bold"))
    middleframe.place(rely=0.29, relx=0.015, relwidth=0.97, relheight=0.12)

    dataLabel = Label(middleframe, text="No Student data to display currently", bg="#acdcdc", font=("Comic Sans MS", 13))
    dataLabel.pack()

    # Lower portion which enables the user to upload the scores
    bottomframe = Frame(window, bg="#c4d763")
    bottomframe.place(relx=0.015, rely=0.42, relwidth=0.97, relheight=0.57)

    valreg = bottomframe.register(validateValues)

    heightLabel = Label(bottomframe, text="Enter Height :", bg="#c4d763", font=("Roboto", 13, "bold"), anchor='w')
    heightLabel.place(relx=0.10, rely=0.1, relwidth=0.35, relheight=0.07)
    heightEntry = Entry(bottomframe, font=("Calibri 15"))
    heightEntry.place(relx=0.47, rely=0.1, relwidth=0.35, relheight=0.07)
    heightUnits = Label(bottomframe, text="metres", bg="#c4d763", font=("Roboto", 11), anchor='w')
    heightUnits.place(relx=0.83, rely=0.11, relwidth=0.1, relheight=0.07)

    heightEntry.config(validate="key",validatecommand=(valreg, '%P'))

    speedLabel = Label(bottomframe, text="Time taken for 50m race :", bg="#c4d763", font=("Roboto", 13, "bold"), anchor='w')
    speedLabel.place(relx=0.10, rely=0.2, relwidth=0.35, relheight=0.07)
    speedEntry = Entry(bottomframe, font=("Calibri 15"))
    speedEntry.place(relx=0.47, rely=0.2, relwidth=0.35, relheight=0.07)
    speedUnits = Label(bottomframe, text="seconds", bg="#c4d763", font=("Roboto", 11), anchor='w')
    speedUnits.place(relx=0.83, rely=0.21, relwidth=0.1, relheight=0.07)

    speedEntry.config(validate="key",validatecommand=(valreg, '%P'))

    enduranceLabel = Label(bottomframe, text="Time taken for 800m race :", bg="#c4d763", font=("Roboto", 13, "bold"), anchor='w')
    enduranceLabel.place(relx=0.10, rely=0.3, relwidth=0.35, relheight=0.07)
    enduranceEntry = Entry(bottomframe, font=("Calibri 15"))
    enduranceEntry.place(relx=0.47, rely=0.3, relwidth=0.35, relheight=0.07)
    enduranceUnits = Label(bottomframe, text="minutes", bg="#c4d763", font=("Roboto", 11), anchor='w')
    enduranceUnits.place(relx=0.83, rely=0.31, relwidth=0.1, relheight=0.07)

    enduranceEntry.config(validate="key",validatecommand=(valreg, '%P'))

    strengthLabel = Label(bottomframe, text="Shotput Distance Thrown :", bg="#c4d763", font=("Roboto", 13, "bold"), anchor='w')
    strengthLabel.place(relx=0.10, rely=0.4, relwidth=0.35, relheight=0.07)
    strengthEntry = Entry(bottomframe, font=("Calibri 15"))
    strengthEntry.place(relx=0.47, rely=0.4, relwidth=0.35, relheight=0.07)
    strengthUnits = Label(bottomframe, text="metres", bg="#c4d763", font=("Roboto", 11), anchor='w')
    strengthUnits.place(relx=0.83, rely=0.41, relwidth=0.1, relheight=0.07)

    strengthEntry.config(validate="key",validatecommand=(valreg, '%P'))

    explosiveLabel = Label(bottomframe, text="LongJump Distance Jumped :", bg="#c4d763", font=("Roboto", 13, "bold"), anchor='w')
    explosiveLabel.place(relx=0.10, rely=0.5, relwidth=0.35, relheight=0.07)
    explosiveEntry = Entry(bottomframe, font=("Calibri 15"))
    explosiveEntry.place(relx=0.47, rely=0.5, relwidth=0.35, relheight=0.07)
    explosiveUnits = Label(bottomframe, text="metres", bg="#c4d763", font=("Roboto", 11), anchor='w')
    explosiveUnits.place(relx=0.83, rely=0.51, relwidth=0.1, relheight=0.07)

    explosiveEntry.config(validate="key",validatecommand=(valreg, '%P'))

    agilityLabel = Label(bottomframe, text="Time taken for 6x10m race :", bg="#c4d763", font=("Roboto", 13, "bold"), anchor='w')
    agilityLabel.place(relx=0.10, rely=0.6, relwidth=0.35, relheight=0.07)
    agilityEntry = Entry(bottomframe, font=("Calibri 15"))
    agilityEntry.place(relx=0.47, rely=0.6, relwidth=0.35, relheight=0.07)
    agilityUnits = Label(bottomframe, text="seconds", bg="#c4d763", font=("Roboto", 11), anchor='w')
    agilityUnits.place(relx=0.83, rely=0.61, relwidth=0.1, relheight=0.07)

    agilityEntry.config(validate="key",validatecommand=(valreg, '%P'))

    submitButton = Button(bottomframe, text="Submit", font=("Roboto", 13, "bold"), fg="White", bg="#49306B", bd=5, relief="ridge", command=lambda : updateStudentData(heightEntry, speedEntry, enduranceEntry, strengthEntry, explosiveEntry, agilityEntry, dataLabel))
    submitButton.place(relx=0.1, rely=0.82, relwidth=0.45, relheight=0.10)

    backButton = Button(bottomframe, text="Back to Homepage", font=("Roboto", 13, "bold"), fg="White", bg="#49306B", bd=5, relief="ridge", command=lambda: callHomescreen(allframes))
    backButton.place(relx=0.65, rely=0.82, relwidth=0.25, relheight=0.10)

    allframes = []
    allframes.append(middleframe)
    allframes.append(topframe)
    allframes.append(bottomframe)







################################### EXPORT DATA WIDGETS ###########################################################
# Opens the file dialog to let the user choose a Folder
def chooseExportFolder(filedisplay):

    global exportfolder
    
    exportfolder = filedialog.askdirectory(initialdir=Path(EXPORTS), mustexist=True)
    
    if(exportfolder == None or exportfolder == ""):
        exportfolder = EXPORTS
        logger.info(messages.INVALID_EXPORT_DIR.format(exportfolder))
    else:   
        filedisplay.configure(text="Chosen Export Folder : " + exportfolder)
        logger.info(messages.VALID_EXPORT_DIR.format(exportfolder))
    
# Exports the data from the SQL table to the required Excel file along with the Schema
def exportData(filedisplay, exportfilename):

    global exportfolder

    if(exportfilename == None or exportfilename == ""):
        logger.info(messages.INVALID_EXPORT_FILENAME.format(exportfilename, currtable))
        exportfilename = currtable
    else:
        logger.info(messages.VALID_EXPORT_FILENAME.format(exportfilename))
        
    if not exportfilename.endswith(".xlsx"):
        exportfilename += ".xlsx"
    
    exportfilepath = Path(exportfolder + os.path.sep + exportfilename)

    filedisplay.configure(text="Chosen Export Folder : " + exportfolder + "\n Export Excel Filename : " + exportfilename)

    result, exportedrows = utils.sqltoexcel(dbconn, currtable, exportfilepath)

    if(result == True):
        logger.info(messages.EXPORT_SUCCESS.format(currtable, str(exportfilepath)))
        filedisplay.configure(text="The data has been successfully exported to \n" + exportfilepath._str)
    else:
        logger.info(messages.EXPORT_FAILURE.format(currtable, str(exportfilepath), exportedrows))
        messagebox.showerror(title="DATA_EXPORT_ERROR",message=messages.DATA_EXPORT_ERROR)

# Opens the Export UI page where users can configure Folder and filename of the destination file
def exporter():

    global currtable

    # topframe which provides the Export location folder defaulted to Exports folder
    topframe = Frame(window, bg="#E5B25D")
    topframe.place(rely=0.06, relx=0.015, relwidth=0.97, relheight=0.35)

    chooseFolder = Button(topframe, text="Choose Export Folder", font=("Roboto", 15, "bold"), fg="#16262E", bg="#E952DE", bd=5, relief="raised", command=lambda: chooseExportFolder(filedisplay))
    chooseFolder.place(relx=0.26, rely=0.15, relwidth=0.50, relheight=0.20)

    exportFileLabel = Label(topframe, text="Export filename      :", font=("Roboto", 15, "bold"), fg="#16262E", bg="#E5B25D")
    exportFileLabel.place(relx=0.10, rely=0.60, relwidth=0.35, relheight=0.18)

    exportFileEntry = Entry(topframe, font=("Roboto", 15), bd=1, relief="solid")
    exportFileEntry.insert(0,currtable)
    exportFileEntry.place(relx=0.50, rely=0.60, relwidth=0.40, relheight=0.18)

    exportreg = topframe.register(validateExcelFileName)
    exportFileEntry.config(validate="key",validatecommand=(exportreg,'%P'))

    middleframe = LabelFrame(window, fg="#F5F8DE", bg="#391463", text="Export Path", font=("Roboto", 15, "bold"))
    middleframe.place(rely=0.42, relx=0.015, relwidth=0.97, relheight=0.14)

    filedisplay = Label(middleframe, fg="#F5F8DE", bg="#391463", text="Export Folder defaulted to : " + EXPORTS + "\n Export Excel Filename is defaulted to : " + currtable , font=("Comic Sans MS", 14))
    filedisplay.pack(pady=10)

    bottomframe = Frame(window, bg="#545E56")
    bottomframe.place(rely=0.57, relx=0.015, relwidth=0.97, relheight=0.42)

    loadDataButton = Button(bottomframe, text="Export Data to CSV File", font=("Roboto", 15, "bold"), fg="#16262E", bg="#E952DE", bd=5, relief="raised", command=lambda: exportData(filedisplay, exportFileEntry.get()))
    loadDataButton.place(rely=0.20, relx=0.25, relheight=0.20, relwidth=0.50)

    backButton =  Button(bottomframe, text="Back to Homepage", font=("Roboto", 15, "bold"), fg="#16262E", bg="#E952DE", bd=5, relief="raised", command=lambda:callHomescreen(allframes))
    backButton.place(rely=0.55, relx=0.25, relheight=0.20, relwidth=0.50)

    allframes = []
    allframes.append(middleframe)
    allframes.append(topframe)
    allframes.append(bottomframe)







####################################### ALL CALLERS ##################################################################
# All Callers that destroy current referenced before going back
def callHomescreen(allframes):
    utils.destroyframes(allframes)

    # Commits all transactions done by updating or loading data into the DB
    global dbconn
    if dbconn:
        dbconn.commit()

    # Delete all global variables
    global loadfilename
    global recordDict
    global exportfolder
    
    exportfolder = EXPORTS
    recordDict.clear()
    loadfilename = None 

    logger.info(messages.CALL_HOME_SCREEN)
    homescreen()

#This handled the default DB & Table checks as part of Caller
def callValidator():
    global dbconn
    global currtable

    if(dbconn == None and currtable == None):
        messagebox.showinfo(title="DB_TABLE_INFO_MISSING", message=messages.DB_TABLE_INFO_MISSING)
        return False
    elif(dbconn == None or currdb == None):
        messagebox.showinfo(title="SELECT_DB_FIRST", message=messages.SELECT_DB_FIRST)
        return False
    elif(currtable == None):
        messagebox.showinfo(title="TABLE_NOT_SELECTED", message=messages.TABLE_NOT_SELECTED)
        return False
    else:
        return True

# Checks if user has selected/created a DB, and then proceeds to destroy homepage frames and bring up the Updater Page
def callUpdater(allframes):
    # Validate Details first
    if(callValidator()):
        utils.destroyframes(allframes)
        updater()

# Select all from the chosen table and export it to the Export folder to a newly created file
def callExporter(allframes):
    # Validate Details first
    if(callValidator()):
        utils.destroyframes(allframes)
        exporter()    

# Checks if user has selected/created a DB, and then proceeds to destroy homepage frames and bring up the Loader Page
def callLoader(allframes):
    # Validate Details first
    if(callValidator()):
        utils.destroyframes(allframes)
        loader()

# Destroy all containers on Quit option selection by user
def quitapplication():
    ok = messagebox.askokcancel("Quit", "Do you want to quit?")
    if ok:
        
        logger.info(messages.QUIT_START)
        
        #Clear put global variables
        global currtable
        global currdb
        global dbconn
        
        currtable = None
        currdb = None
        
        #Close the connection to the DB if open. No commit happens here though
        if dbconn != None:
            dbconn.close()
            print("Closed the DB connection, closing the App")
            dbconn = None
        
        #Backing up all the Databases present in Storage folder
        utils.backup(PROJECT_ROOT, SERVER, BACKUPS)
        
        #Shutdown the Logging instance
        logger.info(messages.LOGGER_SHUTDOWN)
        exitlogman(logger)
        
        window.destroy()
        window.quit()







####################################### HOMESCREEN & INITIAL SETUPS ###################################################
# Default Homescreen attributes and elements to be displayed
def homescreen():

    # upperframe - Conists of LabelFrame to display Connection details & Table selection option
    upperframe = Frame(window, bg="#5CB040")
    upperframe.place(rely=0.05, relx=0.015, relwidth=0.97, relheight=0.22)

    selectbutton = Button(upperframe, text="Select Database", bg="#decccc", font=("Verdana", 15), command=lambda : selectDB(dataLabel), bd=5, relief="ridge")
    selectbutton.place(rely=0.10, relx=0.25, relwidth=0.50, relheight=0.30)

    dbEntry = Entry(upperframe, font=("Helvetica 15 "), bd=5, relief="ridge")
    dbEntry.place(relx=0.10, rely=0.60, relwidth=0.40, relheight=0.25)

    dbreg = upperframe.register(validateDBName)
    dbEntry.config(validate="key",validatecommand=(dbreg,'%P'))

    createbutton = Button(upperframe, text="Create Database", bg="#decccc", font=("Verdana", 15), command=lambda : createDB(dataLabel, dbEntry.get()), bd=5, relief="ridge")
    createbutton.place(rely=0.60, relx=0.60, relwidth=0.32, relheight=0.25)

    #combo Frame - Accomodates, table selection and creation place
    comboframe = Frame(window, bg="#778472")
    comboframe.place(rely=0.28, relx=0.015, relwidth=0.97, relheight=0.22)
    
    classLabel = Label(comboframe, text="Class", font=("Arial", 12, "bold"), bg="#778472")
    classLabel.place(relx=0.13, rely=0.08, relwidth=0.14, relheight=0.15)
    
    termLabel = Label(comboframe, text="Term", font=("Arial", 12, "bold"), bg="#778472")
    termLabel.place(relx=0.43, rely=0.08, relwidth=0.14, relheight=0.15)

    yearLabel = Label(comboframe, text="Year", font=("Arial", 12, "bold"), bg="#778472")
    yearLabel.place(relx=0.73, rely=0.08, relwidth=0.14, relheight=0.15)
    
    #Populating ComboList Dropdown values using Class/Term/Year options
    classList = [6,7,8]
    termList = [1,2,3]
    currentyear = datetime.datetime.today().year
    yearList = [currentyear + i for i in range(10)]
    
    combofont = ("Courier", 15, "bold")
    classCombo = ttk.Combobox(comboframe, values=classList, font=combofont, state="readonly")
    classCombo.current(0)
    classCombo.place(relx=0.13, rely = 0.26, relwidth=0.14, relheight=0.20)
    
    termCombo = ttk.Combobox(comboframe, values=termList, font = combofont, state="readonly")
    termCombo.current(0)
    termCombo.place(relx=0.43, rely = 0.26, relwidth=0.14, relheight=0.20)
    
    yearCombo = ttk.Combobox(comboframe, values=yearList, font = combofont, state="readonly")
    yearCombo.current(0)
    yearCombo.place(relx=0.73, rely = 0.26, relwidth=0.14, relheight=0.20)
    
    tablebutton = Button(comboframe, text="Select Table", bg="#decccc", font=("Verdana", 15), bd=5, relief="ridge", command=lambda : processtabledetails(classCombo.get(), termCombo.get(), yearCombo.get(), dataLabel))
    tablebutton.place(rely=0.65, relx=0.25, relwidth=0.50, relheight=0.25)
    
    # Data frame which displays DB connection & Table details
    global dbconn
    global currdb
    global currtable
    
    dataframe = LabelFrame(window, bg="#acdcdc", text="DB & Table Details", font=("Roboto", 12, "bold"))
    dataframe.place(rely=0.51, relx=0.015, relwidth=0.97, relheight=0.11)

    dataLabel = Label(dataframe, text="Currently not connected to any Database", bg="#acdcdc", font=("Comic Sans MS", 13))
    dataLabel.pack()
    
    if dbconn:
        if(currdb != None and currdb != "" and currtable != None and currtable != ""):
            dataLabel.configure(text="Connected to the Table " + currtable + " \npresent in the Database " + currdb)

    # Lower frame - Consists buttons to either Load/Update records and also Quit the application
    lowerframe = Frame(window, bg="#4867EE")
    lowerframe.place(rely=0.63, relx=0.015, relwidth=0.97, relheight=0.36)

    loadbutton = Button(lowerframe, text="Load Student Data", bg="#decccc", font=("Verdana", 15), bd=5, relief="raised", command= lambda: callLoader(allframes))
    loadbutton.place(relx=0.07, rely=0.20, relwidth=0.40, relheight=0.2)

    updatebutton = Button(lowerframe, text="Update Student Records", bg="#decccc", font=("Verdana", 15), bd=5, relief="raised", command= lambda: callUpdater(allframes))
    updatebutton.place(relx=0.53, rely=0.20, relwidth=0.40, relheight=0.2)

    exportbutton = Button(lowerframe, text="Export Table to CSV", bg="#decccc", font=("Verdana", 15), bd=5, relief="raised",
    command= lambda: callExporter(allframes))
    exportbutton.place(relx=0.07, rely=0.60, relwidth=0.40, relheight=0.2)

    quitbutton = Button(lowerframe, text="Quit", bg="#decccc", font=("Verdana", 15), bd=5, relief="raised", command=quitapplication)
    quitbutton.place(relx=0.53, rely=0.60, relwidth=0.40, relheight=0.2)
    
    allframes = []
    allframes.append(upperframe)
    allframes.append(lowerframe)
    allframes.append(comboframe)
    allframes.append(dataframe)





######################################### INITIALIZERS #################################################################
logger.info(messages.APPLN_START)
utils.verifySetup(PROJECT_ROOT, SERVER, CONFIG, BACKUPS, EXPORTS)

# Entry point for the program, where homescreen is displayed first
homescreen()

# Basic Root Window Initializations
Logo = utils.resource_path(ATHLETE_ICON_FILE)
window.iconphoto(True, PhotoImage(file=Logo))
window.title('MSSSDO v1.0')
window.geometry("750x850")
window.protocol("WM_DELETE_WINDOW", quitapplication)
window.mainloop()
