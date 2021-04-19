from appJar import gui
import webbrowser

from tools.music_to_web import *
from tools.common import *
import platform

app = gui()
if platform.system() == 'Linux':
    if os.path.isfile("images/balfolkdb.png"):
        app.setIcon("images/balfolkdb.png")
    elif os.path.isfile("../images/balfolkdb.png"):
        app.setIcon("../images/balfolkdb.png")
elif platform.system() == 'Windows':
    if os.path.isfile("images/balfolkdb.ico"):
        app.setIcon("images/balfolkdb.ico")
    elif os.path.isfile("../images/balfolkdb.ico"):
        app.setIcon("../images/balfolkdb.ico")

global language
global method
global tagged, strict_tags
language = None
method = None
tagged = False
strict_tags = False
sendBtn = "Send my library and tagged dances to the server (Only meta data and short samples will be send)"
dontUpdateBtn = "Don't update my library"
addBtn = "Add dance tags in my library (Old genre tags are kept)"
replaceBtn = "Replace genre tags of known dances in my library (Unknown tracks will not be touched)"
clearBtn = "Clear all tags in my library before updating (Unknown tracks will have an empty genre tag)"
replaceFirstBtn = "Replace tags of known dances in my library first and send unknown (If sending is not selected, it will only update my library)"
libraryPath = ""

def loginScreen():
    app.removeAllWidgets()
    app.startFrame("Frame", row=0, column=0)
    app.addImage("login", "../images/login.png")
    app.addLabel("title", "Enter credentials to synchronize database")
    app.addLabelEntry("Username")
    app.addLabelSecretEntry("Password")
    app.addButtons(["Continue", "Create account", "Cancel"], pressLogin)
    app.stopFrame()

def uploadScreen1():
    app.removeAllWidgets()
    app.startFrame("Frame", row=0, column=0)
    app.addImage("upload", "../images/local_to_remote.png")
    app.addLabel("question", "Do you want to add your library to the online database?\nYour tracks can have tagged dances but don't need to.\nOnly meta information and some random samples will be uploaded.\n(About 1.5MB/unknown track)")
    app.addButtons(["Yes", "No"], pressUpload1)
    app.stopFrame()

def uploadScreen2():
    app.removeAllWidgets()
    app.startFrame("Frame", row=0, column=0)
    app.addImage("local_dances", "../images/dances_local.png")
    app.addLabel("question", "Have your tracks tagged dances?")
    app.addButtons(["All", "Some", "None"], pressUpload2)
    app.stopFrame()

def languageScreen1():
    app.removeAllWidgets()
    app.addImage("language", "../images/language.png")
    app.addLabel("question", "What language are your tags of the dances in?")
    app.addRadioButton("language", "Dutch")
    app.addRadioButton("language", "French")
    app.addRadioButton("language", "English")
    app.addButton("Continue", pressLanguage1)

def languageScreen2():
    app.removeAllWidgets()
    app.addImage("language", "../images/language.png")
    app.addLabel("question", "What language do you pefer your tags in?")
    app.addRadioButton("language", "Dutch")
    app.addRadioButton("language", "French")
    app.addRadioButton("language", "English")
    app.addButton("Continue", pressLanguage2)

def downloadScreen1():
    app.removeAllWidgets()
    app.addImage("login", "../images/remote_to_local.png")
    app.addLabel("question", "Do you want to update your library with the dances of the online database?")
    app.addButtons(["Yes", "No"], pressDownload1)

def downloadScreen2():
    app.removeAllWidgets()
    app.addImage("remote_dances", "../images/dances_remote.png")
    app.addLabel("question", "How do you want your library updated?")
    app.addButton("Clear all genre tags and add the known dances (some might become empty)", pressDownload2)
    app.addButton("Only replace genre tags of tracks with known dances", pressDownload2)
    app.addButton("Add known dances to existing genre tags", pressDownload2)

def selectLibraryScreen():
    app.removeAllWidgets()
    app.addImage("library", "../images/library.png")
    app.addLabel("library_path", libraryPath)
    app.addButton("Select library", selectLibrary)
    app.addButtons(["Prepare Synchronization", "Cancel"], pressPrepare)


def selectLibrary(button):
    global libraryPath
    libraryPath = os.path.normpath(app.directoryBox(title="Music Library Path"))
    app.setLabel("library_path", "Library path: "+libraryPath)

def pressLogin(button):
    if button == "Continue":
        global usr, pwd
        usr = app.getEntry("Username")
        pwd = app.getEntry("Password")
        if checkAuth(usr, pwd):
            uploadScreen1()
        else:
            app.setLabel("title", "Wrong username or password")
    elif button == "Create account":
        a_website = "https://balfolk-db.eu/db/view/create_account.php"
        webbrowser.open_new(a_website)
    else:
        app.stop()

def pressUpload1(button):
    global upload
    if button == "Yes":
        upload = True
        uploadScreen2()
    else:
        upload = False
        downloadScreen1()

def pressUpload2(button):
    global tagged, strict_tags
    if button == "All":
        tagged = True
        strict_tags = False
    elif button == "Some":
        tagged = True
        strict_tags = True
    else:
        tagged = False
        strict_tags = True
    global language
    if language:
        selectLibraryScreen()
    elif not tagged:
        downloadScreen1()
    else:
        languageScreen1()

def pressLanguage1(button):
    global language
    language = app.getRadioButton("language")
    downloadScreen1()

def pressLanguage2(button):
    global language
    language = app.getRadioButton("language")
    selectLibraryScreen()

def pressDownload1(button):
    global download
    if button == "Yes":
        download = True
        downloadScreen2()
    else:
        download = False
        selectLibraryScreen()

def pressDownload2(button):
    global method
    if button == "Clear all genre tags and add the known dances (some might become empty)":
        method = "purge"
    elif button == "Only replace genre tags of tracks with known dances":
        method = "replace"
    else:
        method = "add"
    languageScreen2()

def pressPrepare(button):
    if button == "Prepare Synchronization":
        prepareSynchronization()
    else:
        app.stop()

def pressSynchronize(button):
    if button == "Synchronize Library":
        setupSync()
        app.thread(synchronize)
    else:
        app.stop()

def prepareSynchronization():
    app.removeAllWidgets()
    global libraryPath, fileList
    fileList = getFileList(libraryPath)
    app.addImage("sync", "../images/prepsync.png")
    app.addLabel("Found "+str(len(fileList))+" tracks in local library")
    if len(fileList) > 100:
        app.addLabel("This will take some time")
    elif len(fileList) > 10:
        app.addLabel("This might take some time")
    app.addButtons(["Synchronize Library", "Cancel"], pressSynchronize)

def setupSync():
    app.removeAllWidgets()
    global libraryPath, fileList, upload, download, method, totalCount, fileCount, totalProgress
    app.addImage("sync", "../images/sync.png")
    app.addLabel("Synchronizing")
    app.addLabel("task","Preparing")
    fileCount = len(fileList)
    totalCount = 0
    app.addLabel("Overall")
    app.addMeter("progress")
    app.setMeter("progress", 0)
    app.addLabel("Task")
    app.addMeter("task_progress")
    app.setMeter("task_progress", 0)
    totalProgress = 0
    if upload:
        totalCount += 5*fileCount
    if download:
        totalCount += fileCount

def synchronize():
    global libraryPath, fileList, upload, download, method, totalCount, fileCount, totalProgress, language
    if upload:
        if not tagged:
            if method == "purge":
                totalCount += fileCount
                clearTags(fileList)
        uploadTracks(fileList)

    if download:
        downloadTracks(fileList)

def clearTags(fileList):
    global totalCount, fileCount, totalProgress
    taskProgress = 0
    for file in fileList:
        clearFile(file)
        taskProgress += 1
        totalProgress += 1
        app.queueFunction(app.setLabel, "task", "Clearing tags")
        app.queueFunction(app.setMeter, "task_progress", 100.0 * taskProgress / fileCount)
        app.queueFunction(app.setMeter, "progress", 100.0 * totalProgress / totalCount)

def uploadTracks(fileList):
    global totalCount, fileCount, totalProgress, usr, pwd, language, download, strict_tags, tagged
    taskProgress = 0
    app.setLabel("task", "Uploading track data")
    dance_list = get_dance_list()
    for file in fileList:
        track = extract_info_from_file(file, dance_list, language)
        if track:
            if tagged and strict_tags:
                for i in range(len(track.dances)-1, -1, -1):
                    dance = track.dances[i]
                    if not dance.name.lower() in dance_list:
                        track.dances = track.dances[:i]+track.dances[i+1:]
            elif not tagged:
                track.dances = []
            track_json = track.json()
            message = send_json_to_web(track_json,usr, pwd, language)
            if message:
                app.setLabel("task", message)
                return None

        taskProgress += 1
        totalProgress += 5
        app.queueFunction(app.setMeter, "task_progress", 100.0 * taskProgress / fileCount)
        app.queueFunction(app.setMeter, "progress", 100.0 * totalProgress / totalCount)
    if not download:
        app.queueFunction(done)

def downloadTracks(fileList):
    global totalCount, fileCount, totalProgress, language, method, nbDancesFound
    nbDancesFound = 0
    purge = method == "purge"
    append = method == "add"
    app.setLabel("task", "Downloading track data")
    taskProgress = 0
    for file in fileList:
        track, found, dancesFound = update_file(file, language, purge, append)
        if dancesFound:
            nbDancesFound += 1
        taskProgress += 1
        totalProgress += 1
        app.queueFunction(app.setMeter, "task_progress", 100.0 * taskProgress / fileCount)
        app.queueFunction(app.setMeter, "progress", 100.0 * totalProgress / totalCount)
    app.queueFunction(done)

def done():
    global nbDancesFound
    app.removeAllWidgets()
    app.addLabel("Done")
    if download:
        app.addLabel("Found "+str(nbDancesFound)+" dances for your library")
    app.addButton("Synchronize another directory",pressSyncOther)
    app.addButton("Close",pressClose)

def pressClose(button):
    app.stop()

def pressSyncOther(button):
    uploadScreen1()

loginScreen()


app.go()