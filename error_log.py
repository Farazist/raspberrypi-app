import os.path
import datetime


class ErrorLog():
    @staticmethod
    def checkExistsFile():
        #file = pathlib.Path()
        if os.path.isfile('log-file.txt'):
            print ("File exist")
        else:
            f = open('log-file.txt', 'x', encoding='utf8')
            print('Create File')
    
    @staticmethod
    def writeToFile(log):
        time = datetime.datetime.now()
        f = open('log-file.txt', 'a', encoding='utf8')
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + log + '\n')
        f.close()


#test = LogFile.checkExistsFile()
#LogFile.writeToFile('test1')
