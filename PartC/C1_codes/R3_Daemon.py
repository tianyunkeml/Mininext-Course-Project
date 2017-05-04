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
		

class myDaemon_R3(DaemonClass):
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
		R3_IP = '131.4.1.1'
		R1_IP = '131.3.1.1'
		R4_IP = '131.4.1.2/16'
		R4_GW = '131.4.1.2'
		R4_NET = '131.4.0.0'
		R4_MASK = '255.255.0.0'
		R3_R4 = 10000
		s_recv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s_recv.bind((R3_IP,RECV_PORT))
		s_recv.listen(5)
		while True:
			s_send = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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
					if 'R3-R4' in line:
						temp = line[line.find('=') + 1:len(line)]
						rTable.append({'dest': R4_NET,'mask': R4_MASK,'gateway': R4_GW,'dist': int(temp.replace(' ','')),'itf': 'R3-eth1'})
						R3_R4 = int(temp.replace(' ',''))
			myfile.close()
			time.sleep(period / 2)
			
			#send its routing table to neighbors	
			send_pack = [w_version] + rTable
			byte_stream = pickle.dumps(send_pack)
			s_send.connect((R1_IP,RECV_PORT))
			s_send.send(byte_stream)
			s_send.close()
		
			time.sleep(period / 2)

			#receive neighbors' routing table info and update own routing table
			conn,addr = s_recv.accept()
			data_recv = conn.recv(BUFFER_SIZE)
			conn.close()
			msg_recv = pickle.loads(data_recv)
			w_version_recv = msg_recv[0]	
			rt_recv = msg_recv[1:]
			if w_version == w_version_recv:
				rTable = rt_update(rt_recv,R4_GW,rTable,'R3-eth1',R3_R4)
			logFile = open(currentPath + '/logR3.txt','a')
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
	setting = {'APP':'R3_Daemon','PIDFILE':'/home/mininet/myfolder/copy/quagga-ixp/part_c/logs/R3_Daemon.pid','LOG':'/home/mininet/myfolder/copy/quagga-ixp/part_c/logs/R3_Daemon.log'}
	myApp = myDaemon_R3(setting)
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
