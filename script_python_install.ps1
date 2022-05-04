$user = $env:UserName
$url = "https://www.python.org/ftp/python/3.10.4/python-3.10.4-amd64.exe"

$output C:\Users\$user\AppData\Local\Programs\Python\Python310
# $output = "C:/tmp/python-3.10.4-amd64.exe"

if (Test-Path $output) {
    Write-Host "Script exists - skipping installation"
    return;
}

New-Item -ItemType Directory -Force -Path C:/tmp

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile $output


& $output /passive InstallAllUsers=1 PrependPath=1 Include_test=0 