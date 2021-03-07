$imageFile = $PSScriptRoot + "\app-image\Dockerfile.python-app-loop"
$imageVersion = ":v0.1"
$imageName = "python-app-loop" + $imageVersion
$loginSrv = "192.168.86.33:5000" #"ghost-server-brysonlabs:5000" # adjust for use of private registry
$imageTag = "$loginSrv/$imageName"

docker build --rm --no-cache -f $imageFile -t $imageName $PSScriptRoot\app-image
#docker build --rm -f ./app-image/Dockerfile.python-app-loop -t $imageName ./app-image


docker tag $imageName $imageTag
docker push $imageTag 