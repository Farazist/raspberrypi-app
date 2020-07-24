import os.path
import datetime


class ErrorLog(): 
    @staticmethod
    def writeToFile(log):
        time = datetime.datetime.now()
        f = open('error_log.txt', 'a', encoding='utf8')
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + log + '\n')
        f.close()


#test = LogFile.checkExistsFile()
#LogFile.writeToFile('test1')
