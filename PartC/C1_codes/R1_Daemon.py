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
		

class myDaemon_R1(DaemonClass):
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
		R1_IP_1 = '131.1.1.1'
		R1_IP_2 = '131.3.1.1'
		H1_IP = '130.2.70.8'
		R2_IP = '131.1.1.2/16'
		R2_GW = '131.1.1.2'
		R2_NET = '131.1.0.0'
		R2_MASK = '255.255.0.0'
		R3_IP = '131.3.1.2/16'
		R3_GW = '131.3.1.2'
		R3_NET = '131.3.0.0'
		R3_MASK = '255.255.0.0'
		R1_R2 = 10000
		R1_R3 = 10000
		s_recv1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s_recv2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s_recv1.bind((R1_IP_1,RECV_PORT))
		s_recv2.bind((R1_IP_2,RECV_PORT))
		s_recv1.listen(5)
		s_recv2.listen(5)
		while True:
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
					if 'R1-R2' in line:
						temp = line[line.find('=') + 1:len(line)]
						rTable.append({'dest': R2_NET,'mask': R2_MASK,'gateway': R2_GW,'dist': int(temp.replace(' ','')),'itf': 'R1-eth1'})
						R1_R2 = int(temp.replace(' ',''))
					if 'R1-R3' in line:
						temp = line[line.find('=') + 1:len(line)]
						rTable.append({'dest': R3_NET,'mask': R3_MASK,'gateway': R3_GW,'dist': int(temp.replace(' ','')),'itf': 'R1-eth2'})
						R1_R3 = int(temp.replace(' ',''))
			myfile.close()		
			time.sleep(period / 2)
			
			#send its routing table to neighbors	
			send_pack = [w_version] + rTable
			byte_stream = pickle.dumps(send_pack)
			s_send = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s_send.connect((H1_IP,RECV_PORT))
			s_send.send(byte_stream)
			s_send.close()
		
			time.sleep(period / 2)

			#receive neighbors' routing table info and update own routing table
			conn,addr = s_recv1.accept()
			data_recv = conn.recv(BUFFER_SIZE)
			conn.close()
			msg_recv = pickle.loads(data_recv)
			w_version_recv = msg_recv[0]	
			rt_recv = msg_recv[1:]
			if w_version == w_version_recv:
				rTable = rt_update(rt_recv,R2_GW,rTable,'R1-eth1',R1_R2)

			conn,addr = s_recv2.accept()
			data_recv = conn.recv(BUFFER_SIZE)
			conn.close()
			msg_recv = pickle.loads(data_recv)
			w_version_recv = msg_recv[0]	
			rt_recv = msg_recv[1:]
			if w_version == w_version_recv:
				rTable = rt_update(rt_recv,R3_GW,rTable,'R1-eth2',R1_R3)
			logFile = open(currentPath + '/logR1.txt','a')
			logFile.write('*************' + time.strftime('%H:%M:%S') + '*************\n')
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
	setting = {'APP':'R1_Daemon','PIDFILE':'/home/mininet/myfolder/copy/quagga-ixp/part_c/logs/R1_Daemon.pid','LOG':'/home/mininet/myfolder/copy/quagga-ixp/part_c/logs/R1_Daemon.log'}
	myApp = myDaemon_R1(setting)
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
