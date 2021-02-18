# Current Production
## Deploy Notes: DDEC File Broker Service - Reset
0. Set variables
    ```powershell
    $imageFile = "Dockerfile.DDECFileBrokerReset"
    $imageVersion = ":reset-recursive"
    $imageName = "ddec-file-broker" + $imageVersion
    $loginSrv = "fidatdevacr.azurecr.io"
    $imageTag = "$loginSrv/$imageName"
    $RawPath = "/xtr/raw/collection/2020-10-XX/"
    ```
1. Build image locally
    ```powershell
    docker build --rm -f $imageFile -t $imageName . 
    ```
2. Test run locally
    ```powershell
    docker container run -it --name ddec-file-broker-reset $imageName
    ```
3. Push image to Azure Container Registry
    ```powershell
    docker tag $imageName $imageTag
    docker push $imageTag 
## Deploy Notes: Deploy Service to ACI
1. Start cli container
    ```powershell
    docker container start -ia azure-cli 
    ```
2. Ser variables
    ```bash
    resourceGroup='ddec-container-rg' \
    acrName='fidatdevacr.azurecr.io' \
    aciName='ddec-file-queue-service' \
    imageName=$acrName'/ddec-file-broker:reset-recursive' \
    osType='Windows' \
    usr='fidatdevacr' \
    paswd='U79qiWRFWXni/CMZ1vaTorS+REre0UrX'
    ```
3. Login
    ```bash
    az login
    ```
4. Deploy container group
    ```bash
    az container create \
        -g $resourceGroup \
        --registry-login-server $acrName \
        --registry-username $usr \
        --registry-password $paswd \
        --name $aciName \
        --image $imageName \
        --os-type $osType \
        --cpu 1 --memory 1 --restart-policy Never --location eastus2
    ```

## Deploy Notes: DDEC File Broker Service - Append
0. Set variables
    ```powershell
    $imageFile = "Dockerfile.DDECFileBrokerAppend"
    $imageVersion = ":Append-v0.1"
    $imageName = "ddec-file-broker" + $imageVersion
    $loginSrv = "fidatdevacr.azurecr.io"
    $imageTag = "$loginSrv/$imageName"
    ```
1. Build image locally
    ```powershell
    docker build --rm -f $imageFile -t $imageName . 
    ```
2. Test run locally
    ```powershell
    docker container run -it --name ddec-file-broker-append $imageName
    ```
3. Push image to Azure Container Registry
    ```powershell
    docker tag $imageName $imageTag
    docker push $imageTag 
    ```