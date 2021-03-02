import os
import traceback
import time
from datetime import datetime
import uuid
import sys

from microsrv_interface.comm_interface import *

def main():
    # Set sftp interface
    sftp_interface = sftp_CONN()
    # Set queue interface
    rbt_interface = queue_CONN()

    # Get frequency of app container
    frq = int(set_env_param('FREQUENCY_SEC','300'))
    # Get Application name
    app_name = set_env_param('APP_NAME',str(os.uname()[1]))

    success_msg = ''
    fault_msg = ''
    # Main process thread error handling
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
                        # msg_cnt +=1
                        rbt_interface.write_status(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
                    except Exception as err:
                        print(' [!] Error executing input stream {0}.'.format(app_name))
                        # Report failure to fault channel
                        fault_msg = app_name + ' | Timestamp:' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        rbt_interface.write_fault(fault_msg)
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