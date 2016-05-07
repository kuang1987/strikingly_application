# strikingly_application

This Repo is for strikingly job application.

### How to update the configuration of haproxy or nginx with zero downtime? Explain the mechanism behind it.
1. For nginx, use 'kill -HUP <master pid>' or 'nginx -s reload'(it does the same thing as former command).
The nginx's elegant arch ensures zero downtime. when nginx's master process receives SIGHUP signal, it will fork new worker processes which will handle request immediatly after startup with new configuration. Then, 
the master will send signal to old worker processes to gracefully exit, it's to say, these processes will not acceptin new connection any more, and try to cleanly close existing connection. Once all connections are closed, processes exit.

2. For haproxy, the 'reload' command will reload configuration within a very tiny connection loss.
When starting to reload, the script will start a new haproxy process after checking new configuration. The new haproxy will bind connection to all listening ports using 'SO_REUSEPORT'. If binding successfully, new process
will send singal to old process to gracefully exit. 
When the old process is closing listening ports, the kernal may not always redistribute pending connections which was remainning in socket's backlog. It will leads SYN packet happend before socket is closed. And then, a RST will be sent back
to client. It's the 'tiny loss' mentioned above.  

### What does the command “kill” do? What is the difference, if any, between "kill -9” and “kill” command with other arguments?  
Simply speaking, command kill is used to send a signal to a certain process or a process group. If no signal is specified, the "SIGTERM" will be sent.  
In process, you can set listener for 'SIGTERM' to do some clearance or ensure some significant action done.
And "kill -9 <pid>" will send 'SIGKILL' signal which will enforce process exit.   
I will use two python code snippets to illustrate under kill folder:
> 1. eg1.py -- If we need only one process of some service running in system, usually, we use a lock file or pid file. when process being killed, we should delete lock/pid file.  
If we use 'kill -9' to kill this process, the pid file may not be deleted.
> 2. eg2.py -- If we need ensure something done before exiting. At this situation, if use 'kill -9', process will be exit immediately. 
In real case, may be the web app is still process http request, may be app is writing data into db and etc. 

### In a Unix-like system, how to find files that are older than a certain timestamp and larger than a certain size? You can assume the timestamp & size limit and answer with commands or code.

> find . -type f -exec stat -c '%n %s %Y' '{}' + | awk -vt=`date -d "2016-04-28 00:00:00" +%s` -vs=4000 'BEGIN{}{if($3 > t && $2 > s){print $0}}'

### Elaborate the concept of “everything is a file” in linux with at least 3 examples in different scenarios.
1. in xshell, open a terminal, type 'tty' command  

> [root@cloudapp1 ipc]# tty
> /dev/pts/6

open another terminal, then echo some string like operating file.
> [root@cloudapp1 dev]# echo 'hello' > /dev/pts/6  

in the former terminal,  
> [root@cloudapp1 ipc]# hello

2. proc virtual system to show kernel info
> [root@cloudapp1 dev]# cat /proc/cpuinfo

3. pipe
>[root@cloudapp1 dev]# echo 'hello' | cat
>hello

### What are possible ways two processes communicate with each other? Provide examples. (IPC folder)
1. to illustrate communication between two processes. One is shared memory(mmap), another is socket.
2. I design a virtual conversion which I will ask five questions here.
3. Three py files included:
   >1. xiangxiang.py stands for me 
   >2. strikingly.py stands for the great company. 
   >3. mymap.py is a encapsulation of mmap.

4. Note the former parts is based on mmap and the later is based on socket. 
5. You may need "pickle" module for runtime

### Elaborate the difference between Linux Containers(LXC) and virtualization as well as their pros and cons in different scenarios.
To be honest, I have not much experience in this field. I read some materials today, and try my best to give a simple answer.
The same part for two is to utilize machine hardware resource more efficiently.  
###### Difference:  
virtualization:
   1. lays between hardware and os.
   2. Even though in a same host, virtualization can supply virtual machines with different os by means of CPU instruction translation, file system support, memory management and so on.

LXC:
   1. Based on cgroup.
   2. Seperate resource and namespaceing for a pack of process of appliction.
   3. Share same hardware resource and os kernel which makes a little performance loss.
   4. Quick startup/shutdown give itself high flexibility.

###### pros and cons in some scenarios I can think of:  
1. As the situation in my current company, there are projects in both linux and windows. Virtualization may be the better choice.
2. In order to face the sudden increasing business traffic, LXC may be the better option due to its fast deployment.
3. Try to think the situation that a serious security vulnerability happened, such as open ssl heart bleeding, simply patching the host's kernel is OK for LXC while we need patch every image for virtual machine.

### In a typical 3-layer web application architecture (web server + app/api server + db server), the db server is running slow on both read and write. How would you diagnose the problem and narrow down the problem? What tools will you use and what metrics will you look into?
###### check db server hardware including cpu/memory/disk io/network bandwidth/TCP connections. Command 'top'/'iostat'/'free'/'iftop'/'netstat'... will be used.
1. is there any non-db process having high cpu/memory usage?
2. compare db process cpu/memory usage with past -- if abnormal, it may need look into db itself.
3. check whether disk io being abnormal. -- consider disk is almost full or disk hardward issue.
4. check TCP connections, whether it's from app/api or other origin.  -- consider hack or other mis-access to db
5. check connections number to port which db used.
5. check bandwidth. Use 'tcpdump' or 'pcap' to look into the traffic if nessasary.
....

###### check db process itself. I just have some experience on mysql.
1. 'show processlist' to check slow or hang sql.
2. 'show status like '%connection%'' to see db connection usage.
   1. whether exceed max connection.
   2. how many connections queued.
   3. how many connections error. -- mysql will restrict access from IP when too much error occurs
   4. how many connections timeout.
3. 'show status like '%lock%''. -- may be some sqls lock the row or table leading other transaction hanged
4. 'show open tables' -- to see how many tables is opening, and how many thread is operating on these table.
5. if innodb used, use 'show status like 'innodb'
   1. buffer pool pages used/blank pages/dirty pages/write request.
...

###### check the network enviroment from app/api server to db server.
1. use 'ping' from app/api server to see ttl time.
2. use 'traceroute' -- may be some network equipments down or high traffic. It may leads the long response time or route changed.
...

###### check applications on app/api server. 
1. whether app is using some cold sql.
2. whether the app cache service is running well
3. check app connection pool component. -- I once met a disgusting bug in java c3p0. 
... 

###### If db is in a cluster env, check other members. The LB may lead traffic to 'slow' db server when other members down.

### What tools/services have you used to monitor servers in your past experience? What are the most important metrics you were looking into? Why? 
zabbix
1. some basic metrics -- cpu, memory, disk usage, bandwidth
2. For tomcat application server -- jvm memory, reponse time, connection count, queued connections
3. For mysql server -- connection, slow_query, inno_db_pool_buffer_size, insert/select/delete/update/commit qos
4. For Nginx server -- connection write/wait/read, request count/fail

### Why do you want to join Strikingly? What can you bring to Strikingly? 
I want:  
1. work with brilliant guys with strong technical background, positive attitude.
2. international and startup enviroment.
3. anticipate in a world-wide and esay-to-use product. 

I hope I can bring more passion, more enquiry mind and more views.  

### Ask us 5 questions about Strikingly.
1. what's the strikingly like in your mind?
2. Can employees have chance to work abroad?
3. what's the revenune situation now?
4. what's the plan in next few years including team expansion, produce, IPO and etc?
5. Will the company try a different business field?
