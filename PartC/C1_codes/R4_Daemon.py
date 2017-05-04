import sys
from daemon import DaemonClass
import time
import pickle		#dump into bytes when send, load when receive
from daemon import DaemonClass
import socket

currentPath = '/home/mininet/myfolder/copy/quagga-ixp/part_c'
#routing table update using Bellman-Ford Alg
def rt_update(rt_recv,gw_recv,my_rt,interface,wt):
	for rec in rt_recv:
		rec['dist'] += wt
		rec['gateway'] = gw_recv
		rec['itf'] = interface
		sign = 0
		for myrec in my_rt:
			if myrec['dest'] == rec['dest']:
				sign = 1
				if myrec['gateway'] == gw_recv:
					myrec = rec
				else:
					if rec['dist'] < myrec['dist']:
						myrec = rec
		if sign == 0:
			my_rt.append(rec)
	return my_rt
		

class myDaemon_R4(DaemonClass):
	def __init__(self,setting):
		DaemonClass.__init__(self,setting)

	def run(self):
		self.before_start()
		rTable = []		#routing table
		w_version = 0		#indicate weights.conf file's change
		w_file_path = currentPath + '/weights.conf'
		period = 6
		BUFFER_SIZE = 1024
		RECV_PORT = 88
		w_file_content=''
		R2_IP = '131.2.1.1'
		R3_IP = '131.4.1.1'
		R4_IP = '145.8.70.1'
		H2_IP = '145.8.68.2/18'
		H2_GW = '145.8.68.2'
		H2_NET = '145.8.64.0'
		H2_MASK = '255.255.192.0'
		R4_H2 = 10000
		while True:
			s_send1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s_send2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			w_change = False		#indicate whether weights changed or not
			myfile = open(w_file_path,'r')
			content = myfile.read()
			if content != w_file_content:
				w_version += 1
				w_change = True
			w_file_content = content
			myfile.close()
			myfile = open(w_file_path,'r')
			if w_change == True:
				rTable = []
				for line in myfile:
					if 'R4-H2' in line:
						temp = line[line.find('=') + 1:len(line)]
						rTable.append({'dest': H2_NET,'mask': H2_MASK,'gateway': H2_GW,'dist': int(temp.replace(' ','')),'itf': 'R4-eth2'})
						R4_H2 = int(temp.replace(' ',''))
			myfile.close()		
			time.sleep(period / 2)
			
			#send its routing table to neighbors	
			send_pack = [w_version] + rTable
			byte_stream = pickle.dumps(send_pack)
			s_send1.connect((R2_IP,RECV_PORT))
			s_send1.send(byte_stream)
			s_send1.close()
			s_send2.connect((R3_IP,RECV_PORT))
			s_send2.send(byte_stream)
			s_send2.close()
	
			time.sleep(period / 2)

			#receive neighbors' routing table info and update own routing table
			logFile = open(currentPath + '/logR4.txt','a')
			logFile.write('*************' + time.strftime('%H:%M:%S') + '*************')
			for rec in rTable:
				logFile.write(str(rec) + '\n')
			logFile.write('\n\n')
			logFile.close()
		self.on_exit()
		self.cleanup()

	
	def before_start(self):
		sys.stdout.write('daemon process start...')

	def on_exit(self):
		sys.stdout.write('daemon closed!')

if __name__ == '__main__':
	setting = {'APP':'R4_Daemon','PIDFILE':'/home/mininet/myfolder/copy/quagga-ixp/part_c/logs/R4_Daemon.pid','LOG':'/home/mininet/myfolder/copy/quagga-ixp/part_c/logs/R4_Daemon.log'}
	myApp = myDaemon_R4(setting)
	if sys.argv[1] == 'start':
		sys.stdout.write('Starting the daemon...\n')
		myApp.start()
	if sys.argv[1] == 'stop':
		sys.stdout.write('Stopping the daemon...\n')
		myApp.stop()
	if sys.argv[1] == 'restart':
		sys.stdout.write('Restarting the daemon...\n')
		myApp.restart()
	if sys.argv[1] == 'status':
		myApp.status()
	print '...Done'
