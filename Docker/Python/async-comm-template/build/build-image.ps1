$parentDir = Split-Path -Path $PSScriptRoot

function Set-PsEnv {
    [CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Low')]
    param($localEnvFile = "$parentDir\.env")

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

Write-Output " [*] Setting env variables."
Set-PsEnv

# Set-Location -Path $parentDir

$imageFile = $parentDir + "\Dockerfile"
$imageVersion = ":" + [Environment]::GetEnvironmentVariable("APP_VERSION", "Process")
$imageName = [Environment]::GetEnvironmentVariable("APP_NAME", "Process") # + $imageVersion
$loginSrv = [Environment]::GetEnvironmentVariable("LOCAL_IMAGE_REG", "Process") #"192.168.86.33:5000" #"ghost-server-brysonlabs:5000" # adjust for use of private registry
$imageRepo = "$loginSrv/$imageName"

Write-Output " [*] Building image."
$vTag = $imageRepo+$imageVersion
$lTag = $imageRepo+":latest"
docker image build --rm --no-cache -f $imageFile -t $vTag -t $lTag $parentDir


docker image push --all-tags $imageRepo

# # Save to tar
# Write-Output " [*] Exporting."
# $cur_loc = Get-Location
# Set-Location -Path $PSScriptRoot
# $t_name = [Environment]::GetEnvironmentVariable("APP_NAME", "Process") + ".tar"
# docker save $imageTag > $t_name 

# Set-Location -Path $cur_loc