import subprocess

# Define the PowerShell command
powershell_command = '''
$headers = @{ 
    "accept" = "application/json"; 
    "Authorization" = "FortifyToken xxxx" 
}

$response = Invoke-WebRequest -Uri 'domain/api/v2/applications' -Headers $headers -Method GET
$response.Content
'''
#domain/api/v2/applications
# Execute the PowerShell command
process = subprocess.run(['powershell', '-Command', powershell_command], capture_output=True, text=True)
print('Status Code:', process.returncode)
print('Response Body:', process.stdout)
