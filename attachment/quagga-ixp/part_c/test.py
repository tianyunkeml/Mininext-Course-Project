from daemon import DaemonClass
import time
import sys

class MyApp(DaemonClass):
	def __init__(self,setting = None):
		DaemonClass.__init__(self,setting)

	def run(self):
		alive = True
		while alive:
			f = open('/home/mininet/myfolder/quagga-ixp/part_c/out.txt','a')
			f.write('fff\n')
			f.close()
			time.sleep(1)
		self.on_exit(f)
		self.cleanup()

	def before_start(self):
		sys.stdout.write('Config tasks could go here')

	def on_exit(self,fn):
		fn.close()
		sys.stdout.write('Cleanup tasks go here')

if __name__ == '__main__':
	setting = {'APP':'test','PIDFILE':'/home/mininet/myfolder/quagga-ixp/part_c/test.pid','LOG':'/home/mininet/myfolder/quagga-ixp/part_c/test.log'}
	print('start up...')
	mine = MyApp(setting)
	if sys.argv[1] == 'start':
		mine.start()
	if sys.argv[1] == 'stop':
		mine.stop()
	if sys.argv[1] == 'restart':
		mine.restart()
	if sys.argv[1] == 'status':
		mine.status()
	print('Done')
