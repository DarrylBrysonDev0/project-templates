import os
import pysftp
import traceback
import time
import pika
import pathlib
import uuid

##### Class #####
class sftp_CONN:
    def __init__(self):
        self.ResultAr = []
        return
    def from_env(self) -> None: #setAllParams(self):
        self.remote_host = self.set_env_param('SFTP_HOST',r'localhost')
        self.port = int(self.set_env_param('SFTP_PORT',r'22'))
        self.usr = self.set_env_param('SFTP_USR',r'admin')
        self.pwd = self.set_env_param('SFTP_PWD',r'pwd')
        self.src = self.set_env_param('SOURCE_PATH',r'/src')
        self.destPath = self.set_env_param('DEST_PATH',r'/trgt')
        c = pysftp.CnOpts()
        c.hostkeys = None
        self.cnopts = c
    def to_list(self):
        self.ResultAr.append(self.remote_host)
        self.ResultAr.append(self.port)
        self.ResultAr.append(self.usr)
        self.ResultAr.append(self.pwd)
        self.ResultAr.append(self.src)
        self.ResultAr.append(self.destPath)
        return self.ResultAr
    def set_env_param(self, paramName,defaultStr):
        param = os.getenv(paramName)
        res = defaultStr if not param else param
        return res
    def get_dir_list(self, scon, srcPath):
        # Set callback functions
        wtcb = pysftp.WTCallbacks()
        # Recursively map files
        scon.walktree(srcPath, fcallback=wtcb.file_cb, dcallback=wtcb.dir_cb, ucallback=wtcb.unk_cb)
        lAr = wtcb.flist
        return lAr
    def get_conn(self) -> pysftp.Connection:
        """
        Returns an SFTP connection object
        """
        if self.conn is None:
            cnopts = self.cnopts

            conn_params = {
                'host': self.remote_host,
                'port': self.port,
                'username': self.usr,
                'cnopts': cnopts
            }
            if self.pwd and self.pwd.strip():
                conn_params['password'] = self.pwd
            self.conn = pysftp.Connection(**conn_params)
        return self.conn
    def close_conn(self) -> None:
        """
        Closes the connection
        """
        if self.conn is not None:
            self.conn.close()
            self.conn = None
    def path_exists(self, path: str) -> bool:
        """
        Returns True if a remote entity exists

        :param path: full path to the remote file or directory
        :type path: str
        """
        conn = self.get_conn()
        return conn.exists(path)
    def create_directory(self, remote_directory: str) -> bool:
        """Change to this directory, recursively making new folders if needed.
        Returns True if any folders were created."""
        if self.conn is None:
            self.get_conn()
        sftp = self.conn

        if remote_directory == '/':
            # absolute path so change directory to root
            sftp.chdir('/')
            return
        if remote_directory == '':
            # top-level relative directory must exist
            return
        try:
            sftp.chdir(remote_directory) # sub-directory exists
        except IOError:
            dirname, basename = os.path.split(remote_directory.rstrip('/'))
            self.create_directory(dirname) # make parent directories
            sftp.mkdir(basename) # sub-directory missing, so created it
            sftp.chdir(basename)
            return True
    def download_file(self, locDir: str, remotePath: str) -> str:
        res = None
        if self.conn is None:
            self.get_conn()
        sftp = self.conn

        try:
            # Set local file paths
            rp = str(remotePath)
            p = pathlib.Path(rp.replace("b'", "").replace("'", ""))
            b = pathlib.Path(str(locDir))
            locPath = b.joinpath(p.name)
            # Copy files locally
            sftp.get(str(p), str(locPath))
            res = locPath
        except Exception as err:
            print()
            print("An error occurred while downloading file from SFTP server.")
            print(str(err))
            traceback.print_tb(err.__traceback__)
        return res
    def upload_file(self, locPath, remotePath) -> str:
        res = None
        if self.conn is None:
            self.get_conn()
        sftp = self.conn
        try:
            # Set local file paths
            rp = str(remotePath)
            locPath = str(locPath)
            rDir = pathlib.Path(rp).parent
            self.create_directory(rDir)
            # Copy files remotely
            sftp.put(locPath,rp)
            res = rp
        except Exception as err:
            print("An error occurred while uploading file to SFTP server.")
            print(str(err))
            traceback.print_tb(err.__traceback__)
            raise
        return res
    def delete_file(self, remotePath: str):
        if self.conn is None:
            self.get_conn()
        sftp = self.conn
        try:
            sftp.remove(remotePath)
        except Exception as err:
            print("An error occurred while deleting file from SFTP server.")
            print(str(err))
            traceback.print_tb(err.__traceback__)
    def append_file(self, remotePath_a, remotePath_b):
        if self.conn is None:
            self.get_conn()
        sftp = self.conn
        res = None
        try:
            # with sftp_conn.open(remotePath_a,'a') as f_a:
            with sftp.open(remotePath_b,'rb') as f_b:
                appStr = f_b.read().decode('utf-8') + '\n'
                remotePath_a.writelines(appStr)
            rp = str(remotePath_a)
            res = rp
        except Exception as err:
            print("An error occurred while appending text to file on SFTP server.")
            print(str(err))
            traceback.print_tb(err.__traceback__)
        return res

'''
    - ini
    - create queues
    - set_input_function
    - read_input
    - write to output
    - write status
'''
class queue_CONN:
    def __init__(self):
        self.ResultAr = []
        return
    def set_input_function(self, input_func) -> None:
        self._input_func = input_func
        return
    def open_Connection(self):
        connection =  (pika.BlockingConnection(
                            parameters=pika.ConnectionParameters(self.rbt_srv)))
        return connection
    def open_channel(self, connObj):
        ch = connObj.channel()
        ch.basic_qos(prefetch_count=1)
        return ch
    def create_namespace_queues(self, chObj, nsStr: str) -> None:
        self.success_queue = 'pass_' + nsStr
        self.fail_queue = 'fail_' + nsStr
        self.progress_queue = 'status_' + nsStr
        chObj.queue_declare(queue=self.success_queue, durable=True)
        chObj.queue_declare(queue=self.fail_queue, durable=True)
        chObj.queue_declare(queue=self.progress_queue, durable=True)
        return

    def create_Queue(self) -> None:
        # Create connections
        self.in_conn = self.open_Connection()
        self.out_conn = self.open_Connection()
        # Create channels
        self.in_channel = self.open_channel(self.in_conn)
        self.out_channel = self.open_channel(self.out_conn)
        self.ns_channel = self.open_channel(self.out_conn)
        # Create queues
        self.in_channel.queue_declare(queue=self.src_queue, durable=True)
        self.out_channel.queue_declare(queue=self.dest_queue, durable=True)
        ## Create namespace based queues
        create_namespace_queues(self.ns_channel)
        return
    def from_env(self) -> None: #setAllParams(self):
        default_ns = str(uuid.uuid4().hex)
        self.rbt_srv = self.set_env_param('RABBIT_SRV',r'rabbit-queue')
        self.queue_namespace = self.set_env_param('NAMESPACE',default_ns)
        self.src_queue = self.set_env_param('INPUT_QUEUE',r'new_files')
        self.dest_queue = self.set_env_param('OUTPUT_QUEUE',r'processed_files')
        return
    def to_list(self):
        self.ResultAr.append(self.rbt_srv)
        self.ResultAr.append(self.queue_namespace)
        self.ResultAr.append(self.src_queue)
        self.ResultAr.append(self.dest_queue)
        return self.ResultAr
    def set_env_param(self, paramName: str,defaultStr: str) -> str:
        param = os.getenv(paramName)
        res = defaultStr if not param else param
        return res
    # Read From Input
    def start_input_stream(self) -> None:
        if (self.in_channel is not None) and (self._input_func is not None):
            self.ip_consuming_tag = self.in_channel.basic_consume(
                                        self.src_queue, self._input_func)
        return
    def stop_input_stream(self) -> None:
        if (self.in_channel is not None) and (self.ip_consuming_tag is not None):
            stop_consuming(self.in_channel, self.ip_consuming_tag)
        return
    def stop_consuming(self, ch, ch_tag) -> None:
        ch.basic_cancel(ch_tag)
        return
    # Write to Output
    def write_output(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.out_channel is not None) and (self.dest_queue is not None):
            publish_message(self.out_channel, self.dest_queue,op_msg)
        return

    # Communicate status
    ## Write Success
    def write_success(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.out_channel is not None) and (self.success_queue is not None):
            publish_message(self.out_channel, self.success_queue,op_msg)
        return
    ## Write Fault
    def write_fault(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.out_channel is not None) and (self.fail_queue is not None):
            publish_message(self.out_channel, self.fail_queue,op_msg)
        return
    ## Write Status
    def write_status(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.out_channel is not None) and (self.progress_queue is not None):
            publish_message(self.out_channel, self.progress_queue, op_msg)
        return

    # Publish message to queue
    def publish_message(self, channel, queueName: str, op_msg: str) -> None:
        # Build in publish limiter
        channel.basic_publish(exchange='',
                        routing_key=queueName,
                        body=op_msg)
        return
    def close_all_connections(self) -> None:
        if self.in_conn is not None:
            close_connection(self.in_conn)
        if self.out_conn is not None:
            close_connection(self.out_conn)
        return

    def close_connection(self, conn) -> None:
        # self._consuming = False
        if not conn.is_closing and not conn.is_closed:
            conn.close()
        return





def setParam(paramName,defaultStr):
    param = os.getenv(paramName)
    res = defaultStr if not param else param
    return res

def main():
    # Set sftp wrapper
    sfCon = sftp_CONN()
    sfCon.from_env()
    pAr = sfCon.to_list

    rbt_con = queue_CONN()
    rbt_con.from_env
    try:
        # Get sftp connections
        ## Scope connection to self maintain
        with sfCon.get_conn() as sftp:
            with sftp.open(mst_path,'a') as f_a:
                # Connect to RabbitMQ server
                print(' [-] Connecting to RabbitMQ server',rbt_srv)
                with pika.BlockingConnection(pika.ConnectionParameters(rbt_srv)) as connection:
                    channel = connection.channel()
                    channel_trgt = connection.channel()
                    # Add target queue
                    # Add Source queue

                    print(' [+] Connected to RabbitMQ')
                    # Declare source queue
                    channel.queue_declare(queue=src_queue, durable=True)

                    def callback(ch, method, properties, filePath):
                        try:
                            print()
                            print(" [*] Appending {0}".format(filePath))
                            
                            append_sftp(sftp,f_a,filePath)

                            # # Remove source file
                            # delete_sftp(sftp,filePath)

                            # # Report completion
                            # reportStatus(channel_trgt,trgt_queue,str(resRemotePath))

                            # Ack message proc completion
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                        except Exception as err:
                            print(' [!] Error appending file {0} to master {1}'.format(str(filePath),mst_file))

                    channel.basic_qos(prefetch_count=1)
                    channel.basic_consume(queue=src_queue, on_message_callback=callback, auto_ack=False)

                    print(' [*] Waiting for messages. To exit press CTRL+C')
                    channel.start_consuming()
                    print('queue is empty...')

                    connection.close()
        time.sleep(frq)
    
    except Exception as err:
        print()
        print("An error occured wwhile retriving the file.")
        print(str(err))
        traceback.print_tb(err.__traceback__)
    return

if __name__ == '__main__':
    main()