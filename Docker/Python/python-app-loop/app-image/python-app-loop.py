import os
import pysftp
import traceback
import time
from datetime import datetime
import pika
import pathlib
import uuid
import sys

##### Class #####
class sftp_CONN:
    # Ini
    def __init__(self):
        self.ResultAr = []

        self.remote_host = None
        self.port = None
        self.usr = None
        self.pwd = None
        self.src = None
        self.destPath = None

        self.conn = None

        return
    def __enter__(self):
        res = self.setup()
        pAr = self.to_list()
        return res
    def __exit__(self, type, value, traceback):
        self.close_conn()
        return
    def setup(self) -> None :
        self.from_env()
        conn = self.get_conn()
        return conn
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

class queue_CONN:
    # Ini
    def __init__(self):
        # ini class attributes
        self.ResultAr = []

        self.rbt_srv = None
        self.queue_namespace = None
        self.src_queue = None
        self.dest_queue = None
        self.enable_namespace = None
        self.pub_limit = None

        self.in_conn = None
        self.out_conn = None
        # Create channels
        self.in_channel = None
        self.out_channel = None
        self.ns_channel = None
        return
    def __enter__(self):
        self.setup()
        pAr = self.to_list()
        return pAr
    def __exit__(self, type, value, traceback):
        self.close_all_connections()
        return
    def setup(self) -> None :
        self.from_env()
        self.create_named_channel_queues()
        return
    def _isAttribSet(self, attr) -> bool:
        res = False
        try: res =  hasattr(self,attr)
        except Exception as err: res = False
        return res
    def from_env(self) -> None: #setAllParams(self):
        '''
            Set class parameters from environment variables or set development defaults
        '''
        default_ns = str(uuid.uuid4().hex)
        self.rbt_srv = self.set_env_param('RABBIT_SRV',r'rabbit-queue')
        self.queue_namespace = self.set_env_param('NAMESPACE',default_ns)
        self.src_queue = self.set_env_param('INPUT_QUEUE',r'new_files')
        self.dest_queue = self.set_env_param('OUTPUT_QUEUE',r'processed_files')
        self.enable_namespace = bool(int(self.set_env_param('ENABLE_NAMESPACE_QUEUE',r'0')))
        self.pub_limit = int(self.set_env_param('PUBLISHING_LIMIT','20'))
        return
    def to_list(self):
        '''
            Return class parameters as a list
        '''
        self.ResultAr.append(self.rbt_srv)
        self.ResultAr.append(self.queue_namespace)
        self.ResultAr.append(self.src_queue)
        self.ResultAr.append(self.dest_queue)
        return self.ResultAr
    def set_env_param(self, paramName: str,defaultStr: str) -> str:
        param = os.getenv(paramName)
        res = defaultStr if not param else param
        return res
    def set_input_function(self, input_func) -> None:
        self._input_func = input_func
        return

    # Channel Managment
    ## Named channels
    ### Create channels
    def create_namespace_queues(self, chObj, nsStr: str) -> None:
        self.success_queue = 'pass_' + nsStr
        self.fail_queue = 'fail_' + nsStr
        self.progress_queue = 'status_' + nsStr
        chObj.queue_declare(queue=self.success_queue, durable=True)
        chObj.queue_declare(queue=self.fail_queue, durable=True)
        chObj.queue_declare(queue=self.progress_queue, durable=True)
        return
    def create_named_channel_queues(self) -> None:
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

        if self.enable_namespace:
            ## Create namespace based queues
            self.create_namespace_queues(self.ns_channel, self.queue_namespace)
        return
    ### Start/Stop Input channel
    def start_input_stream(self) -> None:
        print(' [*] Starting input stream')
        if (self.in_channel is not None) and (self._input_func is not None):
        # if self._isAttribSet(self.in_channel) and self._isAttribSet(self._input_func):
            self.ip_consuming_tag = self.start_consuming(self.in_channel, self.src_queue, self._input_func)
            print(' [+] Input stream started with consumer_tag {0}'.format(str(self.ip_consuming_tag)))
        return
    def stop_input_stream(self) -> None:
        if (self.in_channel is not None) and (self.ip_consuming_tag is not None):
        # if self._isAttribSet('in_channel') and self._isAttribSet('ip_consuming_tag'):
            self.stop_consuming(self.in_channel, self.ip_consuming_tag)
        return
    ### Write to Output channel
    def write_output(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.out_channel is not None) and (self.dest_queue is not None):
            self.publish_message(self.out_channel, self.dest_queue,op_msg)
        return
    ## General channels
    ### Publish message to queue
    def publish_message(self, channel, queueName: str, op_msg: str) -> None:
        # Build in publish limiter
        channel.basic_publish(exchange='',
                        routing_key=queueName,
                        body=op_msg)
        return
    ### Start/Stop consumer
    def start_consuming(self, channel, queueName, func):
        if (channel is not None) and (queueName is not None) and (func is not None):
            ctag = self.in_channel.basic_consume(self.src_queue, self._input_func)
            channel.start_consuming()
        return ctag
    def stop_consuming(self, ch, ch_tag) -> None:
        ch.basic_cancel(ch_tag)
        return
    # Connection State
    def open_Connection(self):
        connection =  (pika.BlockingConnection(
                            parameters=pika.ConnectionParameters(self.rbt_srv)))
        return connection
    def open_channel(self, connObj):
        ch = connObj.channel()
        ch.basic_qos(prefetch_count=1)
        return ch
    def close_all_connections(self) -> None:
        self.close_connection(self.in_conn)
        self.close_connection(self.out_conn)
        return
    def close_connection(self, conn) -> None:
        if conn is not None:
            if conn.is_open:
                conn.close()
        return
    # Communicate status
    ## Write Success
    def write_success(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.enable_namespace) and (self.out_channel is not None) and (self.success_queue is not None):
            self.publish_message(self.out_channel, self.success_queue,op_msg)
        return
    ## Write Fault
    def write_fault(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.enable_namespace) and (self.out_channel is not None) and (self.fail_queue is not None):
            self.publish_message(self.out_channel, self.fail_queue,op_msg)
        return
    ## Write Status
    def write_status(self, op_msg: str) -> None:
        # Build in publish limiter
        if (self.enable_namespace) and (self.out_channel is not None) and (self.progress_queue is not None):
            self.publish_message(self.out_channel, self.progress_queue, op_msg)
        return

##### Function #####
def set_env_param(paramName,defaultStr):
    param = os.getenv(paramName)
    res = defaultStr if not param else param
    return res

def main():
    # Set sftp interface
    sftp_interface = sftp_CONN()
    # Set queue interface
    rbt_interface = queue_CONN()

    # Get frequency of app container
    frq = int(set_env_param('FREQUENCY_SEC','300'))
    # Get Application name
    app_name = set_env_param('APP_NAME',str(os.uname()[1]))

    msg_cnt = 0
    try:
        # Connect to SFTP server
        print(' [*] Connecting to SFTP server')
        with sftp_interface as sftp:
            print(' [+] Connected to SFTP server')
            # Connect to RabbitMQ server
            print(' [*] Connecting to RabbitMQ server')
            with rbt_interface as rbt_params:
                print(' [+] Connected to RabbitMQ')
                # Set input calback function
                def input_callback(ch, method, properties, msg):
                    print(" [+] Received %r" % msg)
                    try:
                        # Do something cool
                        print(msg)
                        '''
                            <! Something cool>
                        '''

                        # Ack message proc completion
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                        # Register progress
                        msg_cnt+=1
                        rbt_interface.write_status(str(msg_cnt))
                    except Exception as err:
                        print(' [!] Error executing input stream {0}.'.format(app_name))
                        # Report failure to fault channel
                        fault_msg = app_name + ' | Timestamp:' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        rbt_interface.write_fault(success_msg)
                # Register callback function and start input stream
                rbt_interface.set_input_function(input_callback)
                rbt_interface.start_input_stream()
                # Clean up connections
                # rbt_interface.close_all_connections()
        time.sleep(frq)
        # Report success
        success_msg = app_name + ' | Timestamp:' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        rbt_interface.write_success(success_msg)
    except Exception as err:
        print()
        print("An error occurred while executing main proc.")
        print(str(err))
        traceback.print_tb(err.__traceback__)
    return

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)