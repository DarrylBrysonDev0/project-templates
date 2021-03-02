//------------------------------------------------------------------------------
//MIT License

//Copyright(c) 2017 Microsoft Corporation. All rights reserved.

//Permission is hereby granted, free of charge, to any person obtaining a copy
//of this software and associated documentation files (the "Software"), to deal
//in the Software without restriction, including without limitation the rights
//to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//copies of the Software, and to permit persons to whom the Software is
//furnished to do so, subject to the following conditions:

//The above copyright notice and this permission notice shall be included in all
//copies or substantial portions of the Software.

//THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//SOFTWARE.
//------------------------------------------------------------------------------


namespace FIDAT.XTR.FileBroker
{
    //using Microsoft.WindowsAzure.Storage;
    //using Microsoft.WindowsAzure.Storage.Queue;
    using System;
    using System.Threading.Tasks;
    using Microsoft.Rest;
    //using Microsoft.Rest.Azure.Authentication;
    //using Microsoft.Azure.DataLake.Store;
    //using Azure.Storage.Files.DataLake;
   // using System.Collections.Generic;

    class Program
    {
        //private static AdlsClient client;
        //private static DataLakeDirectoryClient dlClient;
        private static string _flag_WriteMode;
        static void Main(string[] args)
        {
            // Pull ENV_VAR
            // Set Creds
            var _env_Client_Id = Environment.GetEnvironmentVariable("CLIENT_ID");
            var _env_SP_Key = Environment.GetEnvironmentVariable("CLIENT_KEY");
            // string _env_fId = Environment.GetEnvironmentVariable("FOLDER_ID");
            string _env_adlsRawPath = Environment.GetEnvironmentVariable("ADLS_DIR_PATH");
            string _env_AzureTenantId = Environment.GetEnvironmentVariable("AZ_TENANT_ID");
            string _env_adlsAccountName = Environment.GetEnvironmentVariable("ADLS_ACCNT_NAME");
            string _env_queueName = Environment.GetEnvironmentVariable("AZURE_QUEUE_NAME");
            string _env_storageConnectionString = Environment.GetEnvironmentVariable("storageconnectionstring");
            string _env_WriteMode = Environment.GetEnvironmentVariable("WRITE_MODE");
            ///////////////////////\\\\\\\\\\\\\\\\\\\\\\\\\\
            ///////// _____ Dev Variables _____ \\\\\\\\\\\\\\
            ///
            if (_env_Client_Id == null) { _env_Client_Id = "38ecf826-79a0-498d-855f-1405ad5e2644"; }
            if (_env_SP_Key == null) { _env_SP_Key = "ySPY4XCZQ~l~RQ-i--h9B3lhJF_l8KAi9~"; }

            if (_env_adlsRawPath == null) { _env_adlsRawPath = "/xtr/raw/collection/2020-10-XX/"; }
            if (_env_AzureTenantId == null) { _env_AzureTenantId = "7b0efc1a-8aeb-45bb-b1cb-38569cab1fb3"; }
            if (_env_adlsAccountName == null) { _env_adlsAccountName = "fidatddecadls.azuredatalakestore.net"; }
            if (_env_queueName == null) { _env_queueName = "ddec-file-raw-queue"; }
            if (_env_storageConnectionString == null) { _env_storageConnectionString = "DefaultEndpointsProtocol=https;AccountName=fidatddecstore;AccountKey=G0WEQZQgyFY6s8yexwZaBQPP9xGNZ8xcJLatVHoJnX6eh/Hy/w6dupVgq1tB74YkD9McbZJeitN4x7g5cN7xlg==;EndpointSuffix=core.windows.net"; }
            if (_env_WriteMode == null) { _env_WriteMode = "reset"; }

            // ADLS Gen 2 TestVar
            //string _env_storageConnectionString_g2 = "DefaultEndpointsProtocol=https;AccountName=ddecstoregen2;AccountKey=g8X1/01we8YN/sYGlHAFfIekx6JDYQB7hD5CWxdx5LttUxfwyC5bT2eL8AupI/HXPBTbnT78h6UQzH7E6hlzEQ==;EndpointSuffix=core.windows.net";
            //string _env_adlsRawPath_g2 = "/xtr/raw/2020-10-05/"; 
            ///////////////////////\\\\\\\\\\\\\\\\\\\\\\\\\\
            _flag_WriteMode = _env_WriteMode;

            //// Login to ADLS
            ConfigureADLSClient(_env_AzureTenantId, _env_Client_Id, _env_SP_Key, _env_adlsAccountName);

            Console.WriteLine("** DDEC File Broker: {0} **", Environment.MachineName);
            Console.WriteLine();
            Console.WriteLine("Starting Broker {0} UTC +0:00", DateTime.UtcNow);

            Console.WriteLine();

            //ConfigureDataLakeClient(_env_AzureTenantId, _env_Client_Id, _env_SP_Key, _env_adlsAccountName);

            ProcessAsync(_env_adlsRawPath, _env_storageConnectionString, _env_queueName).GetAwaiter().GetResult();

            Console.WriteLine("Queue update complete, exiting DDEC File Broker.");
            //Console.WriteLine("Press any key to exit DDEC File Broker application.");
            //Console.ReadLine();
        }

        private static async Task ProcessAsync(string sourcePath, string storageConnectionString, string queueName)
        {
            CloudStorageAccount storageAccount = null;
            CloudQueue queue = null;

            // Check whether the connection string can be parsed.
            if (CloudStorageAccount.TryParse(storageConnectionString, out storageAccount))
            {
                try
                {
                    // Create the CloudQueueClient that represents the queue endpoint for the storage account.
                    CloudQueueClient cloudQueueClient = storageAccount.CreateCloudQueueClient();

                    // Create a queue called 'quickstartqueues' and append a GUID value so that the queue name 
                    // is unique in your storage account. 
                    queue = cloudQueueClient.GetQueueReference(queueName);
                    await queue.CreateIfNotExistsAsync();
                    Console.WriteLine("Connected to queue '{0}'", queue.Name);
                    Console.WriteLine();

                    // Recursively publish file names of an adls directory
                    await PublishFolder(sourcePath, queue);

                    //// Get list of files 
                    //// Check ADLS directory access rights
                    //bool adlsAccess = client.CheckAccess(sourcePath, "r-x");
                    //// Console.WriteLine(adlsAccess.ToString()); 
                    //if(adlsAccess)
                    //{
                    //    // Reset queue
                    //    if (_flag_WriteMode == "reset"){await queue.ClearAsync();}
                    //    var stream = client.EnumerateDirectory(sourcePath);
                    //    string currentFullFileName = string.Empty;
                    //    int _BUFFER_LIMIT = 1000;
                    //    int msgCnt = 0;
                    //    int buffCnt = 0;

                    //    Console.WriteLine("Starting queue insert {0} UTC +0:00", DateTime.UtcNow);

                    //    foreach (var item in stream)
                    //    {
                    //        if (item.Type == DirectoryEntryType.FILE && !item.FullName.ToLower().Contains(".txt"))
                    //        {
                    //            currentFullFileName = item.FullName;
                    //            // Broadcast each path as a message

                    //            // Create a message and add it to the queue. Set expiration time to 7 days.
                    //            CloudQueueMessage message = new CloudQueueMessage(currentFullFileName);
                    //            await queue.AddMessageAsync(message, new TimeSpan(7,0,0,0), null, null, null);
                    //            //Console.WriteLine("Added message '{0}' to queue '{1}'", message.Id, queue.Name);
                    //            //Console.WriteLine("Message insertion time: {0}", message.InsertionTime.ToString());
                    //            //Console.WriteLine("Message expiration time: {0}", message.ExpirationTime.ToString());
                    //            //Console.WriteLine();
                    //            msgCnt++;
                    //            buffCnt++;
                    //            if (buffCnt%_BUFFER_LIMIT == 0)
                    //            {
                    //                buffCnt = 0;
                    //                Console.WriteLine("Added {0} messages to queue '{1}' @ {2}", msgCnt, queue.Name, DateTime.UtcNow);
                    //            }
                    //        } else if (item.Type == DirectoryEntryType.DIRECTORY)
                    //        {

                    //        }
                    //    }
                    //    Console.WriteLine("Queue filled at {0} UTC +0:00", DateTime.UtcNow);
                    //    Console.WriteLine("{0} messages inserted", msgCnt);
                    //}
                }
                catch (StorageException ex)
                {
                    Console.WriteLine("Error returned from Azure Storage: {0}", ex.Message);
                }
                finally
                {
                }
            }
            else
            {
                Console.WriteLine(
                    "A connection string has not been defined in the system environment variables. " +
                    "Add a environment variable named 'storageconnectionstring' with your storage " +
                    "connection string as a value.");
            }
        }
        private static async Task PublishFolder(string sourcePath, CloudQueue queue)
        {
            //Console.WriteLine("Starting queue insert {0} UTC +0:00", DateTime.UtcNow);
            Console.WriteLine("Publishing directory {0}", sourcePath);

            // Get list of files 
            // Check ADLS directory access rights
            bool adlsAccess = client.CheckAccess(sourcePath, "r-x");
            // Console.WriteLine(adlsAccess.ToString()); 
            if (adlsAccess)
            {
                // Reset queue
                if (_flag_WriteMode == "reset") { await queue.ClearAsync(); }
                var stream = client.EnumerateDirectory(sourcePath);
                string currentFullFileName;
                int _BUFFER_LIMIT = 1000;
                int msgCnt = 0;
                int buffCnt = 0;

                //Console.WriteLine("Starting queue insert {0} UTC +0:00", DateTime.UtcNow);

                foreach (var item in stream)
                {
                    if (item.Type == DirectoryEntryType.FILE && !item.FullName.ToLower().Contains(".txt"))
                    {
                        currentFullFileName = item.FullName;
                        // Broadcast each path as a message

                        // Create a message and add it to the queue. Set expiration time to 7 days.
                        CloudQueueMessage message = new CloudQueueMessage(currentFullFileName);
                        await queue.AddMessageAsync(message, new TimeSpan(7, 0, 0, 0), null, null, null);

                        msgCnt++;
                        buffCnt++;
                        if (buffCnt % _BUFFER_LIMIT == 0)
                        {
                            buffCnt = 0;
                            Console.WriteLine("{0} file paths published to queue '{1}' @ {2}", msgCnt, queue.Name, DateTime.UtcNow);
                        }
                    }
                    else if (item.Type == DirectoryEntryType.DIRECTORY)
                    {
                        await PublishFolder(item.FullName, queue);
                    }
                }
                Console.WriteLine("Directory {0} Published at {1} UTC +0:00", sourcePath, DateTime.UtcNow);
                Console.WriteLine("{0} Total file paths published", msgCnt);
            }

        }
        private static void ConfigureADLSClient(string azureTenantId, string clientId, string spKey, string adlsAccountName)
        {
            try
            {
                System.Uri ARM_TOKEN_AUDIENCE = new System.Uri(@"https://management.core.windows.net/");
                //
                System.Uri ADL_TOKEN_AUDIENCE = new System.Uri(@"https://datalake.azure.net/");
                //
                var armCreds = GetCreds_SPI_SecretKey(azureTenantId, ARM_TOKEN_AUDIENCE, clientId, spKey);
                //
                var adlCreds = GetCreds_SPI_SecretKey(azureTenantId, ADL_TOKEN_AUDIENCE, clientId, spKey);
                //
                client = AdlsClient.CreateClient(adlsAccountName, adlCreds);
            }
            catch (Exception ex)
            {
                //
                WriteExceptionToConsole(ex);
                //
                //telemetryClient.TrackException(ex);
                ////
                //telemetryClient.TrackEvent("ConfigureADLSClient() Failed" + " : Process Id = " + _folderId);
            }
            finally
            {
                //
                //telemetryClient.Flush();
            }
        }
        private static void ConfigureDataLakeClient(string azureTenantId, string clientId, string spKey, string adlsAccountName)
        {
            try
            {
                //System.Uri ARM_TOKEN_AUDIENCE = new System.Uri(@"https://management.core.windows.net/");
                ////
                //System.Uri ADL_TOKEN_AUDIENCE = new System.Uri(@"https://datalake.azure.net/");
                ////
                //var armCreds = GetCreds_SPI_SecretKey(azureTenantId, ARM_TOKEN_AUDIENCE, clientId, spKey);
                ////
                //var adlCreds = GetCreds_SPI_SecretKey(azureTenantId, ADL_TOKEN_AUDIENCE, clientId, spKey);
                ////
                //client = AdlsClient.CreateClient(adlsAccountName, adlCreds);
                System.Uri STORAGE_AUDIENCE = new System.Uri(@"https://storage.azure.com");
                var storage_Uri = GetCreds_SPI_SecretKey(azureTenantId, STORAGE_AUDIENCE, clientId, spKey);

                System.Uri ADL_Uri = new System.Uri(@"https://ddecstoregen2.blob.core.windows.net/xtr");
                var t_dlClient = new DataLakeDirectoryClient(ADL_Uri);
                Console.WriteLine(t_dlClient.Name);
                Console.WriteLine(t_dlClient.Path);
            }
            catch (Exception ex)
            {
                //
                WriteExceptionToConsole(ex);
                //
                //telemetryClient.TrackException(ex);
                ////
                //telemetryClient.TrackEvent("ConfigureADLSClient() Failed" + " : Process Id = " + _folderId);
            }
            finally
            {
                //
                //telemetryClient.Flush();
            }
        }
        private static ServiceClientCredentials GetCreds_SPI_SecretKey(string tenant, Uri tokenAudience, string clientId, string secretKey)
        {
            //
            System.Threading.SynchronizationContext.SetSynchronizationContext(new System.Threading.SynchronizationContext());
            //
            var serviceSettings = ActiveDirectoryServiceSettings.Azure;
            //
            serviceSettings.TokenAudience = tokenAudience;
            //
            var creds = ApplicationTokenProvider.LoginSilentAsync(
             tenant,
             clientId,
             secretKey,
             serviceSettings).GetAwaiter().GetResult();
            return creds;
        }

        private static void WriteExceptionToConsole(Exception ex)
        {
            //
            string errorMessage = ex.Message;
            //
            if (ex.InnerException != null && ex.InnerException.Message != null)
                errorMessage = errorMessage + " INNER: " + ex.InnerException.Message;
            //
            Console.WriteLine(errorMessage);
        }

    }
}
