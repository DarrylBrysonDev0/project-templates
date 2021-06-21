function Set-PsEnv {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Low')]
    param($localEnvFile = (Split-Path -Path $PSScriptRoot -Parent) + "\.env")

    #return if no env file
    if (!( Test-Path $localEnvFile)) {
        Throw "could not open $localEnvFile"
    }

    #read the local env file
    $content = Get-Content $localEnvFile -ErrorAction Stop
    Write-Verbose "Parsed .env file"

    #load the content to environment
    foreach ($line in $content) {
        if ($line.StartsWith("#")) { continue };
        if ($line.Trim()) {
            $line = $line.Replace("`"","")
            $kvp = $line -split "=",2
            if ($PSCmdlet.ShouldProcess("$($kvp[0])", "set value $($kvp[1])")) {
                [Environment]::SetEnvironmentVariable($kvp[0].Trim(), $kvp[1].Trim(), "Process") | Out-Null
            }
        }
    }
}

Set-PsEnv

$imageFile = $PSScriptRoot + "\app-image\Dockerfile.python-app-loop"
$imageVersion = ":" + [Environment]::GetEnvironmentVariable("APP_VERSION", "Process")
$imageName = [Environment]::GetEnvironmentVariable("APP_NAME", "Process") + $imageVersion
$loginSrv = [Environment]::GetEnvironmentVariable("LOCAL_IMAGE_REG", "Process") #"192.168.86.33:5000" #"ghost-server-brysonlabs:5000" # adjust for use of private registry
$imageTag = "$loginSrv/$imageName"

docker build --rm --no-cache -f $imageFile -t $imageName $PSScriptRoot\app-image

docker tag $imageName $imageTag
docker push $imageTag 

$imageVersion = ":latest"
$imageName_l = [Environment]::GetEnvironmentVariable("APP_NAME", "Process") + $imageVersion
$imageTag = "$loginSrv/$imageName_l"

docker tag $imageName $imageTag
docker push $imageTag 