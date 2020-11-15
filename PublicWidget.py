import time
import sys
import os

from PyQt5.QtWidgets import QWidget, QTabWidget, QMessageBox, QLineEdit, QCompleter, QTextBrowser, QMenu, QAction, \
    QTextEdit, QPushButton, QFrame, QLabel, QHBoxLayout
from PyQt5.QtCore import QObject, QStringListModel, Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QTextCursor

from Public import logger, checkPath
import Public
import logging


# print输出重定向
class Stream(QObject):
    """printRedirects console output to text widget."""
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))


# 用于显示logger日志
class LogTab(QTabWidget):
    def __init__(self, parent, maxLogLine=500, configPath='./config', ifRedirect=True, logDir='',
                 ifClearLogAtStart=False,  ifAddTime=False,logLevel=logging.INFO):
        super(LogTab, self).__init__(parent)
        self.title = type(parent).__name__
        self.configPath = '{0}\\{1}.ini'.format(configPath,type(self).__name__)
        self.ifSaveLog = False
        self.logDir = logDir
        self.maxLogLine = maxLogLine
        self.ifRedirect = ifRedirect
        self.ifAddTime = ifAddTime
        self.ifClearLogAtStart = ifClearLogAtStart
        self.colorInfo = '#FFFFFF'
        self.colorWarning = '#9999FF'
        self.colorError = '#FF0000'
        self.logLevel = logLevel

        self.__loadConfig()

        if self.ifRedirect:
            self.printRedirect()

        self.__widgetInit()

        if '' != self.logDir:
            self.ifSaveLog = True
            if False is os.path.exists(logDir):
                os.makedirs(logDir)
            self.debugSavePath = self.logDir + '/debug.log'
            self.infoSavePath = self.logDir + '/info.log'
            self.warningSavePath = self.logDir + '/warning.log'
            self.errorSavePath = self.logDir + '/error.log'
            if self.ifClearLogAtStart:
                self.clearAll(True, True, True, True)

    def setLogLevel(self,loglevel):
        self.logLevel = loglevel
        self.__changeLogFormat()

    def __loadConfig(self):
        op = Public.Public_ConfigOp(self.configPath)
        rt = op.ReadConfig(self.title, 'maxLogLine', Type='int', defaultValue=self.maxLogLine)
        if True is rt[0]:
            self.maxLogLine = rt[1]

        rt = op.ReadConfig(self.title, 'ifRedirect', Type='bool', defaultValue=self.ifRedirect)
        if True is rt[0]:
            self.ifRedirect = rt[1]

        rt = op.ReadConfig(self.title, 'ifClearLogAtStart', Type='bool', defaultValue=self.ifClearLogAtStart)
        if True is rt[0]:
            self.ifClearLogAtStart = rt[1]

        rt = op.ReadConfig(self.title, 'logLevel', Type='int', defaultValue=self.logLevel)
        if True is rt[0]:
            self.logLevel = rt[1]

        rt = op.ReadConfig(self.title, 'ifAddTime', Type='bool', defaultValue=self.ifAddTime)
        if True is rt[0]:
            self.ifAddTime = rt[1]

        rt = op.ReadConfig(self.title, 'logDir', defaultValue=self.logDir)
        if True is rt[0]:
            self.logDir = rt[1]

        rt = op.ReadConfig(self.title, 'colorInfo', defaultValue=self.colorInfo)
        if True is rt[0]:
            self.colorInfo = rt[1]

        rt = op.ReadConfig(self.title, 'colorWarning', defaultValue=self.colorWarning)
        if True is rt[0]:
            self.colorWarning = rt[1]

        rt = op.ReadConfig(self.title, 'colorError', defaultValue=self.colorError)
        if True is rt[0]:
            self.colorError = rt[1]

    def __widgetInit(self):
        self.debugTextBrow = QTextEditCanClear(self, self.maxLogLine)
        self.infoTextBrow = QTextEditCanClear(self, self.maxLogLine)
        self.warningTextBrow = QTextEditCanClear(self, self.maxLogLine)
        self.errorTextBrow = QTextEditCanClear(self, self.maxLogLine)
        self.addNewTab(self.infoTextBrow, 'INFO')
        self.addNewTab(self.warningTextBrow, 'WARNING')
        self.addNewTab(self.errorTextBrow, 'ERROR')
        self.addNewTab(self.debugTextBrow, 'DEBUG')

    def exit(self):
        self.recoverPrintRedirect()

    def clearAll(self, info=False, debug=False, warning=False, error=False):
        self.clearInfo(info)
        self.clearDebug(debug)
        self.clearWarning(warning)
        self.clearError(error)

    def clearInfo(self, ifClearLog=False):
        self.infoTextBrow.clear()
        if ifClearLog:
            path = self.infoSavePath
            if os.path.exists(path):
                os.remove(path)

    def clearDebug(self, ifClearLog=False):
        self.debugTextBrow.clear()
        if ifClearLog:
            path = self.debugSavePath
            if os.path.exists(path):
                os.remove(path)

    def clearError(self, ifClearLog=False):
        self.errorTextBrow.clear()
        if ifClearLog:
            path = self.errorSavePath
            if os.path.exists(path):
                os.remove(path)

    def clearWarning(self, ifClearLog=False):
        self.warningTextBrow.clear()
        if ifClearLog:
            path = self.warningSavePath
            if os.path.exists(path):
                os.remove(path)

    def Info(self, msg, color=''):
        if self.logLevel > logging.INFO:
            return
        msg = str(msg)
        if True is self.ifAddTime:
            msg = "[{time}] {msg}".format(time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg=msg)
        if True is self.ifSaveLog:
            with open(self.infoSavePath, 'a+') as f:
                f.write(msg + '\r')
        if '' != color:
            msg = "<font color=\"{color}\">{message}</font> ".format(message=msg, color=color)
        self.infoTextBrow.append(msg)

    def Debug(self, msg):
        if self.logLevel > logging.DEBUG:
            return
        msg = str(msg)
        if True is self.ifAddTime:
            msg = "[{time}] {msg}".format(time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg=msg)
        if True is self.ifSaveLog:
            with open(self.debugSavePath, 'a+') as f:
                f.write(msg + '\r')
        self.debugTextBrow.append(msg)
        # self.log(msg)

    def Error(self, msg):
        if self.logLevel > logging.ERROR:
            return
        msg = str(msg)
        if True is self.ifAddTime:
            msg = "[{time}] {msg}".format(time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg=msg)
        if True is self.ifSaveLog:
            with open(self.errorSavePath, 'a+') as f:
                f.write(msg + '\r')
        self.errorTextBrow.append(msg)

    def Warning(self, msg):
        if self.logLevel > logging.WARNING:
            return
        msg = str(msg)
        if True is self.ifAddTime:
            msg = "[{time}] {msg}".format(time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg=msg)
        if True is self.ifSaveLog:
            with open(self.warningSavePath, 'a+') as f:
                f.write(msg + '\r')

        self.warningTextBrow.append(msg)

    def addNewTab(self, widget, Name):
        self.addTab(widget, Name)

    def onUpdateText(self, message):
        """Write console output to text widget."""
        if len(message.strip()) > 0:
            if False is message.startswith('['):
                self.Debug(message)
                return
            pos = message.find(']')
            level = message[1:pos]
            if 'DEBUG' == level:
                self.Debug(message)
            else:
                color = '#FFFFFF'
                if 'WARNING' == level:
                    color = '#9999FF'
                    self.Warning(message)
                elif 'ERROR' == level:
                    color = '#FF0000'
                    self.Error(message)
                self.Info(message, color)

    def __changeLogFormat(self):
        logging.basicConfig(level=self.logLevel,
                            # format="[%(name)s][%(levelname)s][%(asctime)s] %(message)s",
                            format="[%(levelname)s][%(asctime)s] %(message)s",
                            datefmt='%Y-%m-%d %H:%M:%S'  # 注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                            )

    # print重定向
    def printRedirect(self):
        if True is self.ifRedirect:
            sys.stdout = Stream(newText=self.onUpdateText)
            sys.stderr = Stream(newText=self.onUpdateText)
            self.__changeLogFormat()

    def recoverPrintRedirect(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stdout__


def ShowWarning(self, Msg):
    QMessageBox.warning(self,
                        'Warning',
                        Msg,
                        QMessageBox.Yes)


# LineEdit添加历史记录功能，按下回车添加至历史中
class LineEditWithHistory(QLineEdit):
    elementSelected = pyqtSignal(str)
    nowTime = 0
    oldTime = 0

    def __init__(self, parent, title='历史记录', configPath='',
                 qssFilePath="./Resources/stylesheet/style.qss"):
        super(LineEditWithHistory, self).__init__(parent)
        self.qssFilePath = qssFilePath
        if "" == configPath:
            self.configPath = "./config/{parentName}/LineEditWithHistory.ini".format(parentName=type(parent).__name__)
        else:
            if 0 <= os.path.basename(configPath).find("."):
                self.configPath = configPath
            else:
                self.configPath = "{basePath}/LineEditWithHistory.ini".format(basePath=configPath)
        self.title = title
        self.sectionName = '{title}'.format(title=self.title)
        self.HistoryListChanged = False
        self.commandHasSent = False
        # 用于存放历史记录的List
        self.inputList = []

        self.__loadHistory()
        self.__widgetInit()

    def Exit(self):
        self.__saveHistory()

    def __widgetInit(self):
        # LineEdit设置QCompleter，用于显示历史记录
        self.completer = QCompleter(self)
        self.listModel = QStringListModel(self.inputList, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setModel(self.listModel)
        self.completer.activated.connect(self.Slot_completer_activated, type=Qt.QueuedConnection)

        try:
            with open(self.qssFilePath, "r") as fh:
                self.completer.popup().setStyleSheet(fh.read())
        except Exception as e:
            logger.info('读取QSS文件失败' + str(e))

        self.setCompleter(self.completer)
        # 输入完成按下回车后去重添加到历史记录中
        self.returnPressed.connect(self.Slot_updateHistoryModule)

    def __loadHistory(self):
        historyList = self.inputList
        historyOp = Public.Public_ConfigOp(self.configPath)
        rt = historyOp.ReadAllBySection(self.sectionName)
        if True is rt[0]:
            for item in rt[1]:
                if (item[1] not in historyList) and ("" != item[1]):
                    historyList.append(item[1])
        else:
            logger.info(rt[1])

    def __saveHistory(self):
        ipOp = Public.Public_ConfigOp(self.configPath)
        if True is self.HistoryListChanged:
            ipOp.RemoveSection(self.sectionName)
            ipOp.SaveAll()
            for index, item in enumerate(self.inputList):
                ipOp.SaveConfig(self.sectionName, str(index), item)

    def updateHistory(self):
        content = self.text()
        if content != "":
            if content not in self.inputList:
                self.inputList.append(content)
                self.listModel.setStringList(self.inputList)
                self.completer.setCompletionMode(QCompleter.PopupCompletion)
                self.HistoryListChanged = True
        self.__sendElement()

    def Slot_updateHistoryModule(self):
        self.updateHistory()

    # 按下回车或单击后恢复显示模式  https://doc.qt.io/qt-5/qcompleter.html#activated
    def Slot_completer_activated(self, text):
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.__sendElement()

    def __sendElement(self):
        self.elementSelected.emit(self.text())

    def deleteEle(self, ele):
        if ele in self.inputList:
            self.inputList.remove(ele)
            self.listModel.setStringList(self.inputList)
            self.completer.setCompletionMode(QCompleter.PopupCompletion)
            self.HistoryListChanged = True

    def event(self, event):
        # 按下Tab键时弹出所有记录
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                # 设置不过滤显示  https://doc.qt.io/qt-5/qcompleter.html#completionMode-prop
                if self.completer.completionCount() > 0:
                    self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
                    self.listModel.setStringList(self.inputList)
                    self.completer.complete()
                    self.completer.popup().show()
                return True
            elif event.key() == Qt.Key_Delete:
                self.deleteEle(self.text())

        return super().event(event)


# LineEdit自动补全
class LineEditWithComplete(QLineEdit):
    def __init__(self, parent, inputList, configPath='./config/LineEditWithHistory.ini',
                 qssFilePath="./Resources/stylesheet/style.qss"):
        super(LineEditWithComplete, self).__init__(parent)
        self.qssFilePath = qssFilePath
        self.configPath = configPath
        # 用于存放历史记录的List
        self.inputList = inputList

        self.__widgetInit()

    def Exit(self):
        pass

    def __widgetInit(self):
        # LineEdit设置QCompleter，用于显示历史记录
        self.completer = QCompleter(self)
        self.listModel = QStringListModel(self.inputList, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setModel(self.listModel)
        self.completer.activated.connect(self.Slot_completer_activated, type=Qt.QueuedConnection)

        # try:
        #     with open(self.qssFilePath, "r") as fh:
        #         self.completer.popup().setStyleSheet(fh.read())
        # except Exception as e:
        #     logger.info('读取QSS文件失败' + str(e))

        self.setCompleter(self.completer)

    # 按下回车或单击后恢复显示模式  https://doc.qt.io/qt-5/qcompleter.html#activated
    def Slot_completer_activated(self, text):
        self.completer.setCompletionMode(QCompleter.PopupCompletion)

    def event(self, event):
        # 按下Tab键时弹出所有记录
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab:
                # 设置不过滤显示  https://doc.qt.io/qt-5/qcompleter.html#completionMode-prop
                if self.completer.completionCount() > 0:
                    self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
                    self.listModel.setStringList(self.inputList)
                    self.completer.complete()
                    self.completer.popup().show()
                return True
            elif event.key() == Qt.Key_Delete:
                self.deleteEle(self.text())

        return super().event(event)


class QTextBrowserCanClear(QTextBrowser):
    KeyPressSignal = pyqtSignal(int)
    MousePressSignal = pyqtSignal(object)
    wheelEventSignal = pyqtSignal(object)

    def __init__(self, parent, maxTextLine=100):
        super(QTextBrowser, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popMenu)
        self.__paraInit()

        self.maxTextLine = maxTextLine

    def __paraInit(self):
        self.currentLineNum = 0  # 当前打印行数
        self.maxTextLine = 100  # 最大打印行数

    def popMenu(self, pos):
        self.RightClickedMenu = QMenu(None, self)
        self.RightClickedMenu.move(QWidget.mapToGlobal(self, pos))
        self.Aciton_delete = QAction("清屏", self)
        self.Aciton_delete.triggered.connect(self.Slot_Aciton_delete_ClearScreen)
        self.RightClickedMenu.addAction(self.Aciton_delete)
        self.RightClickedMenu.show()

    def Slot_Aciton_delete_ClearScreen(self):
        self.clear()

    # 根据行数上限可以删除旧打印
    def newAppend(self, p_str):
        self.append(p_str)
        self.currentLineNum = self.getCurrentLineNum()
        excessNum = self.currentLineNum - self.maxTextLine
        if excessNum >= 0:
            txtCur = self.textCursor()
            # 选中第一行
            txtCur.setPosition(0)
            txtCur.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            # 向下拉动
            for i in range(0, excessNum + 1):
                txtCur.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor)
            # 移动到行首，防止第一行空白
            txtCur.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
            # selectStr = txtCur.selectedText()
            txtCur.removeSelectedText()

    # 获取光标所在行数
    def getCurrentLineNum(self):
        tc = self.textCursor()
        nCurpos = tc.position() - tc.block().position()
        nTextline = tc.block().layout().lineForTextPosition(nCurpos).lineNumber() + tc.block().firstLineNumber()
        return nTextline


class QTextEditCanClear(QTextBrowser):
    KeyPressSignal = pyqtSignal(int)
    MousePressSignal = pyqtSignal(object)
    wheelEventSignal = pyqtSignal(object)

    def __init__(self, parent, maxLogLine=100):
        super(QTextBrowser, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popMenu)
        self.document().setMaximumBlockCount(maxLogLine)

    def popMenu(self, pos):
        RightClickedMenu = QMenu(None, self)
        RightClickedMenu.move(QWidget.mapToGlobal(self, pos))
        Aciton_delete = QAction("清屏", self)
        Aciton_delete.triggered.connect(self.Slot_Aciton_delete_ClearScreen)
        Aciton_openSelectedPath = QAction('打开选中路径', self)
        Aciton_openSelectedPath.triggered.connect(self.Slot_Aciton_openSelectedPath)
        RightClickedMenu.addAction(Aciton_delete)
        RightClickedMenu.addAction(Aciton_openSelectedPath)
        RightClickedMenu.show()

    def Slot_Aciton_delete_ClearScreen(self):
        self.clear()

    def Slot_Aciton_openSelectedPath(self):
        selectedContent = self.textCursor().selectedText()
        Public.openFile(selectedContent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.KeyPressSignal.emit(event.key())
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, mouseEvent):
        self.MousePressSignal.emit(mouseEvent)
        super().mousePressEvent(mouseEvent)


class QTextEdit_SetMaxLine_Clear_Log(QTextEdit):
    KeyPressSignal = pyqtSignal(int)
    MousePressSignal = pyqtSignal(object)
    wheelEventSignal = pyqtSignal(object)

    def __init__(self, parent, maxTextLine=100, ifLog=True, savedLogPath='./Log/', logSaveFileName='',
                 logMaxSize=1048576):
        super(QTextEdit, self).__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popMenu)
        self.__paraInit()

        self.maxTextLine = maxTextLine
        self.currentlineNum = 0
        self.ifLog = ifLog
        self.savedLogPath = checkPath(savedLogPath)
        self.logSaveFileName = logSaveFileName
        if 0 < logMaxSize:
            self.logMaxSize = logMaxSize

        self.__configInit()
        self.__widgetInit()

    def __paraInit(self):
        self.currentlineNum = 0  # 当前打印行数
        self.maxTextLine = 100  # 最大打印行数
        self.ifSaveLog = True
        self.logSaveFileName = ''
        self.savedLogPath = ''
        self.logFileNum = 0
        self.logMaxSize = 1024 * 1024
        self.logSize = 0

    def __configInit(self):
        if '' == self.logSaveFileName:
            nowtime = time.localtime(time.time())
            self.logSaveFileName = "%04d_%02d_%02d" % (int(nowtime.tm_year), int(nowtime.tm_mon), int(
                nowtime.tm_mday))  # +'_'+ int(nowtime.tm_hour) + int(nowtime.tm_min) + int(nowtime.tm_sec)
        if False is os.path.exists(self.savedLogPath):
            os.makedirs(self.savedLogPath)

        self.logSaveFileName = self.savedLogPath + self.logSaveFileName + '.log'

    def __widgetInit(self):
        self.Aciton_ifLog = QAction("取消保存日志", self)
        self.Aciton_ifLog.triggered.connect(self.Slot_Aciton_ifLog)
        self.Aciton_ClearScreen = QAction("清屏", self)
        self.Aciton_ClearScreen.triggered.connect(self.Slot_Aciton_ClearScreen)

        self.document().setMaximumBlockCount(self.maxTextLine)

    def popMenu(self, pos):
        self.RightClickedMenu = QMenu(None, self)
        self.RightClickedMenu.move(QWidget.mapToGlobal(self, pos))
        self.RightClickedMenu.addAction(self.Aciton_ClearScreen)
        self.RightClickedMenu.addAction(self.Aciton_ifLog)
        self.RightClickedMenu.show()

    def Slot_Aciton_ifLog(self):
        if True is self.ifSaveLog:
            self.ifSaveLog = False
            self.Aciton_ifLog.setText("保存日志")
        else:
            self.ifSaveLog = True
            self.Aciton_ifLog.setText("取消保存日志")

    def Slot_Aciton_ClearScreen(self):
        self.clear()

    # 根据行数上限可以删除旧打印
    def newAppend(self, p_str):
        if True is self.ifSaveLog:
            with open(self.logSaveFileName, 'a+') as fw:
                fw.write(p_str + '\r')
        self.append(p_str)

    # 获取光标所在行数
    def getCurrentLineNum(self):
        tc = self.textCursor()
        nCurpos = tc.position() - tc.block().position()
        nTextline = tc.block().layout().lineForTextPosition(nCurpos).lineNumber() + tc.block().firstLineNumber()
        return nTextline

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.KeyPressSignal.emit(event.key())
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, mouseEvent):
        self.MousePressSignal.emit(mouseEvent)
        super().mousePressEvent(mouseEvent)


class QLineEdit_Can_Drop(QLineEdit):
    def __init__(self, parent, title, configPath):
        super(QLineEdit, self).__init__(parent)
        self.configPath = configPath
        self.title = title
        self.setAcceptDrops(True)
        self.editingFinished.connect(self.savePath)
        self.ifAutoLoad = True
        self.__loadConfig()

    def __loadConfig(self):
        op = Public.Public_ConfigOp(self.configPath)
        rt = op.ReadConfig('Global', 'ifAutoLoad',Type='bool')
        if True is rt[0]:
            self.ifAutoLoad = rt[1]
        else:
            op.SaveConfig('Global', 'ifAutoLoad','True')

        if False is self.ifAutoLoad:
            return
        rt = op.ReadConfig(self.title, 'path')
        if True is rt[0]:
            self.setText(rt[1])
        else:
            logger.warn('读取路径失败:{path}'.format(path=self.title))

    def savePath(self):
        op = Public.Public_ConfigOp(self.configPath)
        op.SaveConfig(self.title, 'path', self.text())

    def dragEnterEvent(self, e):
        e.accept()

    def dragLeaveEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        fileNameList = []
        fileList = e.mimeData().urls()
        for file in fileList:
            fileName = file.toString()
            if fileName.startswith('file:///'):
                fileNameList.append(fileName[len('file:///'):])
        if 1 == len(fileNameList):
            self.setText(fileNameList[0])
            op = Public.Public_ConfigOp(self.configPath)
            op.SaveConfig(self.title, 'path', fileNameList[0])


class QPushButton_Can_Return_Path(QPushButton):
    returnPath = pyqtSignal(str)

    def __init__(self, parent, title, ifDir, configPath):
        super(QPushButton, self).__init__(parent)
        self.configPath = configPath
        self.title = title
        self.ifDir = ifDir
        self.setText(title)
        self.clicked.connect(self.__getPath)

    def __getPath(self):
        op = Public.Public_ConfigOp(self.configPath)
        filePath = op.OldPathReadAndNewPathSave(self.title, "path", ifDir=self.ifDir)
        if "" != filePath:
            self.returnPath.emit(filePath)


class QDirLoadFrame(QFrame):
    def __init__(self, parent, title, buttonSize, configPath,ifDir=False):
        super(QFrame, self).__init__(parent)
        self.title = title
        self.configPath = '{0}\\{1}.ini'.format(configPath,type(self).__name__)
        self.ifDir = ifDir
        self.buttonSize = buttonSize
        self.__widgetInit()

    def __widgetInit(self):
        self.hBoxLayout = QHBoxLayout(self)
        self.lineEdit = QLineEdit_Can_Drop(self, self.title, self.configPath)
        self.pubutton = QPushButton_Can_Return_Path(self, title=self.title, ifDir=self.ifDir,
                                                    configPath=self.configPath)
        if 0 < self.buttonSize:
            self.pubutton.setFixedWidth(self.buttonSize)
        self.pubutton.returnPath.connect(self.Slot_pubutton_returnPath)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.addWidget(self.lineEdit)
        self.hBoxLayout.addWidget(self.pubutton)

    def Slot_pubutton_returnPath(self, path):
        self.lineEdit.setText(path)


class QLineEditFrame(QFrame):
    def __init__(self, parent, title, configPath):
        super(QFrame, self).__init__(parent)
        self.title = title
        self.configPath = '{0}\\{1}.ini'.format(configPath,type(self).__name__)
        self.__widgetInit()
        self.__loadConfig()

        self.destroyed.connect(self.Exit)

    def Exit(self):
        for widget in self.widgetList:
            try:
                widget.Exit()
            except Exception as e:
                pass

    def __widgetInit(self):
        self.widgetList = []
        self.label_name = QLabel(self.title)
        self.widgetList.append(self.label_name)
        self.lineEdit = LineEditWithHistory(self, self.title)
        self.lineEdit.editingFinished.connect(self.saveConfig)
        self.widgetList.append(self.lineEdit)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label_name)
        self.hBoxLayout.addWidget(self.lineEdit)

    def __loadConfig(self):
        op = Public.Public_ConfigOp(self.configPath)
        rt = op.ReadConfig(self.title, 'name')
        if True is rt[0]:
            self.lineEdit.setText(rt[1])
        else:
            logger.warn('读取路径失败:{path}'.format(path=self.title))

    def saveConfig(self):
        op = Public.Public_ConfigOp(self.configPath)
        op.SaveConfig(self.title, 'name', self.lineEdit.text())
