import os
import sys
import traceback
import time
import pandas as pd
from microsrv_interface.comm_interface import db_CONN, set_env_param #,sftp_CONN, queue_CONN

def main():
    # Set Database interface
    db_interface = db_CONN()

    # Get frequency of app container
    frq = int(set_env_param('FREQUENCY_SEC','30'))
    # Get Application name
    app_name = set_env_param('APP_NAME',str(os.uname()[1]))

    try:
        # Connect to Database
        print(' [*] Connecting to database')
        with db_interface as db_conn:
            print(' [+] Connected to database')

            col = ['ID','val']
            qStr = 'SELECT [ID],[val] FROM [telemDataStore].[dbo].[test_tbl]'
            df = db_interface.select_query(qStr,col)

            print(df)
        time.sleep(frq)
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