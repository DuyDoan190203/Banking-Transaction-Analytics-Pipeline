# Build Lambda deployment package with dependencies
# This script creates a zip file with all Python dependencies

Write-Host "Building Lambda deployment package..." -ForegroundColor Green

# Create temporary directory
$tempDir = "lambda_package"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Install only required dependencies (no pandas to avoid platform issues)
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install requests==2.31.0 Faker==22.0.0 -t $tempDir --quiet

# Copy Lambda function files (using simplified version without pandas)
Write-Host "Copying Lambda function files..." -ForegroundColor Yellow
Copy-Item ../lambda/lambda_handler_simple.py $tempDir/lambda_handler.py

# Create zip file
Write-Host "Creating deployment package..." -ForegroundColor Yellow
if (Test-Path lambda_function.zip) {
    Remove-Item lambda_function.zip
}

# Compress to zip
Compress-Archive -Path "$tempDir\*" -DestinationPath lambda_function.zip

# Cleanup
Remove-Item -Recurse -Force $tempDir

Write-Host "Lambda package created: lambda_function.zip" -ForegroundColor Green
Write-Host "Size: $((Get-Item lambda_function.zip).Length / 1MB) MB" -ForegroundColor Cyan

