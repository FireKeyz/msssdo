# What is MSSSDO?

MSSSDO is the *Middle School Student Sports Data Organizer* that is used to manage the Sports Data for middle school students for 5 different sports events.

## What features does MSSSDO offer?

There are 4 main features :

* **Select or Create Database & Tables**
  * The user can create a SQLite Database at the start or select one. The Table name will be constructed from the Class, Term & Year details and will be creaed if it does not exist.
* **Load the Student Data**
  * You can load the basic student data from an Excel workbook (Load an *.xlsx* file with one worksheet) into the selected Database & table.
* **Update Student Data**
  * First, you use the *Search Utility* to get the student by providing the Roll Number.
  * Then, you can edit the different sport-scores for the chosen student and *Submit* which will update the record
* **Export Student Data**
  * In the Export option, you can configure the Export file & folder names.
  * The data from the chosen table in the Database will be exported to an Excel workbook (Into an *.xlsx* file's one worksheet)
* **Backup Database**
  * After every time you quit the Application, there is a backup of all the databases you have created inside a folder with it's name as the *current date*

## The different folders created in MSSSDO & their usage?

* **Backups** : This folder stores the backup of the databases in a Dated folders
* **Exports** : This folder is the default location for exported workbooks
* **Storage** : This folder is used to hold the Databases created by the users from the Application
* **Icons** : This folder holds the 2 icons for the Tkinter window and the Executable
* **ConfigFiles** : This folder holds the property files for *Table creation* & *Excel to SQL field map*
* **Logs** : This folder contains the Logs generated from each run of the application. *Extensive logging - Ideal for debugging*

## How to build & Use MSSSDO locally?

* Should have installed version of Python > 3.6
* All dependencies will be managed by Pip. So, have Pip installed and run the command - `pip install -r requirements.txt`
* Post making changes to generate the executable, run below command :

```python
`pyinstaller.exe --onefile  --add-data "Icons/athlete.png;." --icon=Icons/athlete-big.ico homepage.py`
```

* Checkout the **dist** folder generated where the binary `msssdo.exe` will be present
* Copy the 2 property files from **ConfigFiles** folder into the folder of same name that gets created the first time you start the executable.

## Homepage Screenshot

![Screenshot](Homepage.jpg)
