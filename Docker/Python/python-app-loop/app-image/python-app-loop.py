import os
import pysftp
import traceback
import time
import pika
import pathlib
import uuid

##### Class #####
class queue_CONN:
    def __init__(self):
        self.ResultAr = []
        return
    def from_env(self) -> None: #setAllParams(self):
        default_ns = str(uuid.uuid4().hex)
        self.rbt_srv = self.set_env_param('RABBIT_SRV',r'rabbit-queue')
        self.queue_namespace = self.set_env_param('NAMESPACE',default_ns)
        self.src_queue = self.set_env_param('INPUT_QUEUE',r'new_files')
        self.dest_queue = self.set_env_param('OUTPUT_QUEUE',r'processed_files')
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
    def write_output(self, op_msg) -> None:
        # Build in publish limiter
        return
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
    # def Connect(self):
    #     scon = pysftp.Connection(host=self.remote_host, username=self.usr, password=self.pwd, port=self.port, cnopts=self.cnopts)
    #     return scon
    def get_dir_list(self, scon, srcPath):
        # Set callback functions
        wtcb = pysftp.WTCallbacks()
        # Recursivly map files
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

    ####################################################

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
            create_directory(dirname) # make parent directories
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
    def upload_sftp(self, locPath, remotePath) -> str:
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
    def delete_sftp(self, remotePath: str):
        if self.conn is None:
            self.get_conn()
        sftp = self.conn
        try:
            sftp.remove(remotePath)
        except Exception as err:
            print("An error occurred while deleting file from SFTP server.")
            print(str(err))
            traceback.print_tb(err.__traceback__)
    def append_sftp(self, remotePath_a, remotePath_b):
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

        
def setParam(paramName,defaultStr):
    param = os.getenv(paramName)
    res = defaultStr if not param else param
    return res
# Class for Fault Extract
def main ():
    sfCon = sftp_CONN()
    sfCon.setAllParams()
    pAr = sfCon.getParams()

    rbt_srv = setParam('RABBIT_SRV','rabbit-queue')
    frq = int(setParam('FREQUENCY_SEC','30'))
    pub_limit = int(setParam('PUBLISHING_LIMIT','20'))
    trgt_queue = setParam('TARGET_QUEUE','new_files')

    try:
        print('Setting start up delay')
        print()
        time.sleep(10)

        print(' [*] Connecting to SFTP server...')
        print(' [-] Retriving file list...')
        # cnopts.hostkeys = None
        with sfCon.Connect() as sftp:
            # list directory 
            fAr = sfCon.getDirList(sftp, sfCon.src)

        print('Connecting to rabbit ',rbt_srv)
        with pika.BlockingConnection(pika.ConnectionParameters(rbt_srv)) as connection:
            channel = connection.channel()

            print('Connected')
            channel.queue_declare(queue=trgt_queue, durable=True)
            # channel.queue_declare(queue=trgt_queue)
            channel.queue_purge(queue=trgt_queue) 

            i=0
            for f in fAr:
                fh = os.path.join(sfCon.src,f)
                channel.basic_publish(exchange='',
                                    routing_key=trgt_queue,
                                    body=str(fh))
                i+=1
                if i == pub_limit:
                    break
            print(" [x] Sent", i,"files to the queue")

            connection.close()
        time.sleep(frq)
    
    except Exception as err:
        print("An error occurred while retriving the file.")
        print(str(err))
        traceback.print_tb(err.__traceback__)

if __name__ == '__main__':
    main()