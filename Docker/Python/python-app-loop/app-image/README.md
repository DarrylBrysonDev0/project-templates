# Deploy Notes
## Build:
0. Set variables
    ```powershell
    $imageFile = "Dockerfile.python-app-loop"
    $imageVersion = ":v0.1"
    $imageName = "python-app-loop" + $imageVersion
    $loginSrv = "ghost-server-brysonlabs:5000" # adjust for use of private registry
    $imageTag = "$loginSrv/$imageName"
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