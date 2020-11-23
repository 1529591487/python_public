# -*- coding: utf-8 -*-
import configparser
import logging
import os
import threading
import shutil

from PyQt5.QtWidgets import QFileDialog

logger = logging.getLogger('SunLog')


def openFile(path):
    if os.path.exists(os.path.abspath(path)):
        os.startfile(os.path.abspath(path))
    else:
        logger.warning('[{path}]不存在'.format(path=os.path.abspath(path)))


def checkPath(path):
    if len(path) > 0:
        if path[-1] != '/' and path[-1] != '\\':
            path = path + '/'
    if False is os.path.exists(path):
        os.makedirs(path)
    return path


class ConfigOpError:
    FileNotFound = "文件不存在"
    IllegalCharacters = "配置存在非法字样"
    RepeatingNode = "配置存在重复节点"
    NoSection = "没有此节点:"
    NoOption = "没有此选项:"


# 返回值不小写
class myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None, allow_no_value=True)

    def optionxform(self, optionstr):
        return optionstr


class Public_ConfigOp:
    NoSection = True
    NoOption = True
    fileExist = False
    configFilePath = ""
    FileContent = []
    newName = ''

    def __init__(self, configFilePath="Config/Config.ini", encoding='utf-8'):
        self.encoding = encoding
        self.configFilePath = configFilePath
        self.config = myconf()
        self.FileContent = self.readAll()

    def __creatError(self, ErrorMsg='未知错误', errorMessage=''):
        rt = [False, ErrorMsg, errorMessage]
        return rt

    def getConfig(self):
        return self.config

    def getAllContent(self):
        return self.FileContent

    # 获取所有子节点名称
    def getSections(self):
        return self.config.sections()

    def readAll(self):
        rt = self.__readAllWithEncoding(self.encoding)
        if False is rt[0]:
            if 'UnicodeDecodeError' == rt[1]:
                self.encoding = 'gbk'
                rt = self.__readAllWithEncoding(self.encoding)
            elif rt[2].startswith('File contains no section headers.'):
                self.encoding = 'utf-8-sig'
                rt = self.__readAllWithEncoding(self.encoding)
        return rt

    def __readAllWithEncoding(self, ecoding):
        rt = self.__creatError()
        try:
            rt = self.config.read(self.configFilePath, ecoding)
            if len(rt) == 0:
                self.fileExist = False
                rt = self.__creatError(self.configFilePath + ConfigOpError.FileNotFound)
            else:
                self.fileExist = True
                rt = [True, "读取成功"]
        except configparser.ParsingError as e:  # 存在非法字样
            rt = self.__creatError(ConfigOpError.IllegalCharacters, e.message)
        except configparser.DuplicateOptionError as e:  # 存在重复节点
            rt = self.__creatError(ConfigOpError.RepeatingNode, e.message)
            self.RemoveSection(e.section)
        except UnicodeDecodeError as e:
            rt = self.__creatError("UnicodeDecodeError")
        except Exception as e:
            rt = self.__creatError(str(e))
        return rt

    def getSections(self):
        return self.config.sections()

    def ReadAllBySection(self, Section):
        rt = self.FileContent
        if True is rt[0]:
            try:
                subNodes = self.config.items(Section)
                rt.clear()
                rt.append(True)
                rt.append(subNodes)
            except configparser.NoSectionError as e:
                rt = self.__creatError(ConfigOpError.NoSection + e.message)
            except Exception as e:
                rt = self.__creatError(e.message)
        return rt

    def ReadConfig(self, section, subNode, Type='str', defaultValue='',comment=''):
        rt = self.FileContent
        NoSection = True
        NoOption = True
        if True is rt[0]:
            try:
                rtContent = self.config.get(section, subNode)
                if 'int' == Type:
                    try:
                        rtContent = int(rtContent)
                    except Exception as e:
                        rt = self.__creatError(
                            '文件:[{path}]中{section}->{sub}转换为{type}类型失败\n'.format(path=self.configFilePath,
                                                                                 section=section, sub=subNode,
                                                                                 type=type) + e.message)
                        return rt
                elif 'hex' == Type:
                    try:
                        rtContent = int(rtContent, 16)
                    except Exception as e:
                        rt = self.__creatError(
                            '文件:[{path}]中{section}->{sub}转换为{type}类型失败\n'.format(path=self.configFilePath,
                                                                                 section=section, sub=subNode,
                                                                                 type=type) + e.message)
                elif 'float' == Type:
                    try:
                        rtContent = float(rtContent)
                    except Exception as e:
                        rt = self.__creatError(
                            '文件:[{path}]中{section}->{sub}转换为{type}类型失败\n'.format(path=self.configFilePath,
                                                                                 section=section, sub=subNode,
                                                                                 type=type) + e.message)
                        return rt
                elif 'bool' == Type:
                    try:
                        if 'true' == rtContent.lower():
                            rtContent = True
                        else:
                            rtContent = False
                    except Exception as e:
                        rt = self.__creatError(
                            '文件:[{path}]中{section}->{sub}转换为{type}类型失败\n'.format(path=self.configFilePath,
                                                                                 section=section, sub=subNode,
                                                                                 type=type) + e.message)
                        return rt
                rt = [True, rtContent]
                NoSection = False
                NoOption = False
            except configparser.NoSectionError as e:
                NoSection = True
                rt = self.__creatError(ConfigOpError.NoSection + e.message)
            except configparser.NoOptionError as e:
                NoOption = True
                rt = self.__creatError(ConfigOpError.NoOption + e.message)
            except AttributeError as e:
                rt = self.__creatError(str(e))
            except Exception as e:
                rt = self.__creatError(e.message)

        if (True is NoSection) or (True is NoOption):
            if '' != comment:
                self.SaveConfig(section, comment)

            # 设置默认值
            if '' != defaultValue:
                self.SaveConfig(section, subNode, defaultValue)
                logger.info('文件:[{path}]中[{section}][{sub}]已设置为默认值[{value}]'.format(path=self.configFilePath,
                                                                                    section=section, sub=subNode,
                                                                                    value=defaultValue))
        rt.append(NoSection)
        rt.append(NoOption)
        return rt

    def SetConfig(self, Section, Option, OptContent=None):
        if None is not OptContent:
            OptContent = str(OptContent)
        if False is os.path.exists(os.path.dirname(self.configFilePath)):
            os.makedirs(os.path.dirname(self.configFilePath))
        try:
            if False is self.config.has_section(Section):
                self.config.add_section(Section)
                self.config.set(Section, Option, OptContent)
            else:
                self.config.set(Section, Option, OptContent)
        except configparser.DuplicateSectionError as e:
            self.config.set(Section, Option, OptContent)
        except Exception as e:
            logger.error(str(e))

    def RemoveOption(self,Section,Option,ifSave=True):
        if True is self.config.has_option(Section,Option):
            self.config.remove_option(Section,Option)
        if True is ifSave:
            self.config.write(open(self.configFilePath, "w+"), space_around_delimiters=False)

    def SaveConfig(self, Section, Option, OptContent=None):
        if None is not OptContent:
            OptContent = str(OptContent)
        if False is os.path.exists(os.path.dirname(self.configFilePath)):
            dirName = os.path.dirname(self.configFilePath)
            if '' != dirName:
                os.makedirs(dirName)
        try:
            if False is self.config.has_section(Section):
                self.config.add_section(Section)
                self.config.set(Section, Option, OptContent)
                self.config.write(open(self.configFilePath, "w"), space_around_delimiters=False)
            else:
                self.config.set(Section, Option, OptContent)
                self.config.write(open(self.configFilePath, "w+"), space_around_delimiters=False)

        except configparser.DuplicateSectionError as e:
            self.config.set(Section, Option, OptContent)
            self.config.write(open(self.configFilePath, "w+"), space_around_delimiters=False)
        except Exception as e:
            logger.error(str(e))

    def SaveSection(self, Section, itemInSection, ifSave=True):
        if False is os.path.exists(os.path.dirname(self.configFilePath)):
            os.makedirs(os.path.dirname(self.configFilePath))
        try:
            if False is self.config.has_section(Section):
                self.config.add_section(Section)
            for item in itemInSection:
                self.config.set(Section, item[0], item[1])
                if True is ifSave:
                    self.config.write(open(self.configFilePath, "w+"), space_around_delimiters=False)
        except Exception as e:
            print("error", str(e))

    def RemoveSection(self, Section, ifSave=False):
        self.config.remove_section(Section)
        if True is ifSave:
            self.SaveAll()

    def SaveAll(self):
        if False is os.path.exists(os.path.dirname(self.configFilePath)):
            os.makedirs(os.path.dirname(self.configFilePath))
        self.config.write(open(self.configFilePath, "w+"), space_around_delimiters=False)

    def SaveByPath(self, newPath):
        if False is os.path.exists(os.path.dirname(newPath)):
            os.makedirs(os.path.dirname(newPath))
        self.config.write(open(newPath, "w+"), space_around_delimiters=False)

    def setFilter(self, Type):
        Filter = "All Files (*)"
        if 'exe' == Type:
            Filter = "Program (*.exe);;All Files (*)"
        elif 'config' == Type:
            Filter = "Config (*.TAB);;All Files (*)"
        elif 'txt' == Type:
            Filter = "txt (*.txt);;All Files (*)"
        elif 'docx' == Type:
            Filter = "docx (*.docx);;All Files (*)"
        elif '' != Type:
            Filter = "{type} (*.{type});;All Files (*)".format(type=Type)
        return Filter

    # 打开旧文件路径并保存新路径
    def OldPathReadAndNewPathSave(self, Section, Sub, ifDir=False, ifSave=False, Type=""):
        FilePath = ""
        DefaultFilePath = ""

        # 获取默认路径
        rt = self.ReadConfig(Section, Sub)
        if rt[0] is True:
            DefaultFilePath = rt[1]

        # 根据默认路径打开文件夹
        Filter = self.setFilter(Type)
        if True is ifDir:
            FilePath = QFileDialog.getExistingDirectory(None,
                                                        "选取文件夹",
                                                        DefaultFilePath)
        else:
            if ifSave is True:
                FilePath = QFileDialog.getSaveFileName(None, caption='文件名',
                                                       directory=DefaultFilePath,
                                                       filter=Filter)[0]
            else:
                FilePath, filetype = QFileDialog.getOpenFileName(None,
                                                                 "选取文件",
                                                                 DefaultFilePath,
                                                                 Filter)  # 设置文件扩展名过滤,注意用双分号间隔

        # 保存文件路径
        if "" != FilePath:
            self.SaveConfig(Section, Sub, FilePath)

        return FilePath


class Public_IPOp:
    @staticmethod
    def CheckIP(IP):
        num = IP.split('.')
        if len(num) == 4:
            for item in num:
                if item.isdigit():
                    if int(item) < 0 or int(item) > 255:
                        return False
                else:
                    return False
        else:
            return False
        return True

    @staticmethod
    def CheckIPAndReturnList(IP):
        ipList = IP.split('.')
        if len(ipList) == 4:
            for item in ipList:
                if item.isdigit():
                    if int(item) < 0 or int(item) > 255:
                        return False
                else:
                    return False
        else:
            return False

        return True, [int(x) for x in ipList]


class DirOp:
    @staticmethod
    def getSpecFileList(filePath, suffix, ifFullName=False, ifFullPath=False):
        fileList = []
        for root, dirs, files in os.walk(filePath):
            for file in files:
                # print file.decode('gbk')    #文件名中有中文字符时转码
                if os.path.splitext(file)[1] == '.' + suffix.strip('.'):
                    t = os.path.splitext(file)[0]
                    if True is ifFullName:
                        t = file
                    if True is ifFullPath:
                        t = "{basePath}/{name}".format(basePath=root, name=file)
                    fileList.append(t)  # 将所有的文件名添加到L列表中
        return fileList  # 返回L列表

    @staticmethod
    def getSpecFileListByKeyWord(filePath, keyWord, ifFullName=False, ifFullPath=False):
        fileList = []
        for root, dirs, files in os.walk(filePath):
            for file in files:
                # print file.decode('gbk')    #文件名中有中文字符时转码
                if 0 <= file.find(keyWord):
                    t = os.path.splitext(file)[0]
                    if True is ifFullName:
                        t = file
                    if True is ifFullPath:
                        t = "{basePath}/{name}".format(basePath=filePath, name=file)
                    fileList.append(t)  # 将所有的文件名添加到L列表中
        return fileList  # 返回L列表

    @staticmethod
    def getAllFiles(dir):
        files_ = []
        list_ = os.listdir(dir)
        for i in range(0, len(list_)):
            path = os.path.join(dir, list_[i])
            if os.path.isdir(path):
                files_.extend(DirOp.getAllFiles(path))
            if os.path.isfile(path):
                files_.append(path)
        return files_

    @staticmethod
    def getAllDirs(dir):
        dirs_ = []
        list_ = os.listdir(dir)
        for i in range(0, len(list_)):
            path = os.path.join(dir, list_[i])
            if os.path.isdir(path):
                dirs_.append(path)
                dirs_.extend(DirOp.getAllDirs(path))
        return dirs_

    @staticmethod
    def copyDir(srcDir, dstDir):
        files = os.listdir(srcDir)
        for item in files:
            fullPath = "{basePath}/{fileName}".format(srcDir, fileName=item)
            shutil.copy2(fullPath, dstDir)

    @staticmethod
    def copytree(srcDir, dstDir, symlinks=False, ignore=None):
        if not os.path.exists(dstDir):
            os.makedirs(dstDir)
        for item in os.listdir(srcDir):
            s = os.path.join(srcDir, item)
            d = os.path.join(dstDir, item)
            if os.path.isdir(s):
                DirOp.copytree(s, d, symlinks, ignore)
            else:
                if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                    shutil.copy2(s, d)

    @staticmethod
    def rmtree(dirName):
        # shutil.rmtree(dirName)
        for root, dirs, files in os.walk(dirName):
            for item in dirs:
                DirOp.rmtree("{0}/{1}".format(root, item))
            for item in files:
                os.remove("{0}/{1}".format(root, item))
            os.rmdir(root)


class myLogQueue:
    def __init__(self, maxLogsize=5000):
        self.mutex = self.mutex = threading.Lock()
        self.maxLogsize = maxLogsize
        self.log = []
        self.tempLogFlag = False
        self.tempLog = []

    def getLatestLog(self):
        with self.mutex:
            if 0 < len(self.log):
                return self.log[-1]
            else:
                return ''

    def full(self):
        if len(self.log) >= self.maxLogsize:
            return True
        else:
            return False

    def putLog(self, msg):
        with self.mutex:
            if True is self.full():
                self.log.pop(0)
            self.log.append(msg)
            if True is self.tempLogFlag:
                self.tempLog.append(msg)

    def initTempLog(self):
        with self.mutex:
            self.tempLog.clear()
            self.tempLogFlag = True

    def getTempLog(self):
        with self.mutex:
            return self.tempLog
            self.tempLog.clear()
            self.tempLogFlag = False


class SentenceHandle(object):

    @staticmethod
    def is_Chinese(word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    @staticmethod
    def splitChineseAndEnglishSentence(brief):
        if None is not brief:
            tempList = brief.split('\t')
            for item in tempList:
                if '' == item.strip():
                    tempList.remove(item)
            if 2 != len(tempList):
                tempList = brief.split()

            chineseFirst = False
            ChineseBrief = ''
            EnglishBrief = ''
            if len(tempList) > 0:
                flag = SentenceHandle.is_Chinese(tempList[0])
                preBrief = tempList[0] + ' '
                sufBrief = ''
                if len(tempList) > 1:
                    for i in range(1, len(tempList)):
                        if flag == SentenceHandle.is_Chinese(tempList[i]):
                            preBrief += tempList[i] + ' '
                        else:
                            for j in range(i, len(tempList)):
                                sufBrief += tempList[j] + ' '
                            break

                if True is flag:
                    ChineseBrief = preBrief
                    EnglishBrief = sufBrief
                else:
                    ChineseBrief = sufBrief
                    EnglishBrief = preBrief

            return {'Chinese': ChineseBrief.strip(), 'English': EnglishBrief.strip()}
        else:
            return {'Chinese': '', 'English': ''}

    @staticmethod
    def addChineseEnd(ChineseBrief):
        if '' == ChineseBrief:
            return ''
        if True is ChineseBrief.endswith('.') or True is ChineseBrief.endswith(',') or True is ChineseBrief.endswith(
                '，'):
            ChineseBrief = ChineseBrief[:-1] + '。'
        elif False is ChineseBrief.endswith('。'):
            ChineseBrief = ChineseBrief + '。'
        return ChineseBrief

    @staticmethod
    def addEnglishEnd(EnglishBrief):
        if '' == EnglishBrief:
            return ''
        if True is EnglishBrief.endswith('。') or True is EnglishBrief.endswith(',') or True is EnglishBrief.endswith(
                '，'):
            EnglishBrief = EnglishBrief[:-1] + '.'
        elif False is EnglishBrief.endswith('.'):
            EnglishBrief = EnglishBrief + '.'
        return EnglishBrief

    @staticmethod
    def initialUpper(EnglishBrief):
        if '' == EnglishBrief:
            return ''
        EnglishBrief = EnglishBrief[0].upper() + EnglishBrief[1:]
        return EnglishBrief


def getFiles(dir, suffix, ifsubDir=True):  # 查找根目录，文件后缀
    res = []
    for root, directory, files in os.walk(dir):  # =>当前根,根下目录,目录下的文件
        for filename in files:
            name, suf = os.path.splitext(filename)  # =>文件名,文件后缀
            if suf == suffix:
                res.append(os.path.join(root, filename))  # =>吧一串字符串组合成路径
        if False is ifsubDir:
            break
    return res


class PreffixAndSuffix:

    def __init__(self):
        pass

    @staticmethod
    def add_preffix(file_path, preffix):  # 为file_path添加preffix前缀 并返回文件名绝对路径
        dir_name, filename, extension = PreffixAndSuffix.get_names(file_path)

        new_name = dir_name + preffix + filename + extension
        os.rename(file_path, new_name)
        return new_name

    @staticmethod
    def del_preffix(file_path, preffix):  # 为file_path删除preffix前缀 并返回文件名绝对路径
        dir_name, filename, extension = PreffixAndSuffix.get_names(file_path)

        if filename.startswith(preffix):  # 判断文件名是否以preffix开头
            filename = filename.partition(preffix)[2]  # ('', preffix, 去掉前缀文件名)[2]
            new_name = dir_name + filename + extension
            os.rename(file_path, new_name)
            return new_name
        else:
            return file_path

    @staticmethod
    def add_suffix(file_path, suffix):  # 为file_path添加preffix后缀 并返回文件名绝对路径
        dir_name, filename, extension = PreffixAndSuffix.get_names(file_path)

        new_name = dir_name + filename + suffix + extension
        os.rename(file_path, new_name)
        return new_name

    @staticmethod
    def del_suffix(file_path, suffix):  # 为file_path删除preffix后缀 并返回文件名绝对路径
        dir_name, filename, extension = PreffixAndSuffix.get_names(file_path)

        if filename.endswith(suffix):  # 判断文件名是否以preffix开头
            filename = filename.rpartition(suffix)[0]  # (文件名, suffix, 扩展名)[0]

            new_name = dir_name + filename + extension
            os.rename(file_path, new_name)
            return new_name
        else:
            return file_path

    @staticmethod
    def get_names(file_path):
        file_path = os.path.abspath(file_path)  # 获取这个文件/文件夹的绝对路径
        dir_name = os.path.dirname(file_path)  # 获取所在目录
        dir_name = dir_name + os.sep  # 为拼接做准备
        filename, extension = os.path.splitext(file_path)  #: 分离文件名与扩展名结果为（filename，扩展名） 如果参数为一个路径则返回（路径，''）
        name = filename.rpartition(os.sep)[2]  # (文件目录名 ,目录分隔符, 文件名/目录名)
        names = (dir_name, name, extension)  # (文件所在目录名, 文件名, 文件扩展名)
        # print(names)
        return names
