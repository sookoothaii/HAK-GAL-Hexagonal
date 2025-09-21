# HAK-GAL Grafana Automatic Setup
# ================================

Write-Host "🚀 Setting up Grafana automatically..." -ForegroundColor Green

# Wait for Grafana to be ready
Write-Host "⏳ Waiting for Grafana to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Function to make API calls to Grafana
function Invoke-GrafanaAPI {
    param(
        [string]$Method,
        [string]$Endpoint,
        [object]$Body = $null,
        [string]$ContentType = "application/json"
    )
    
    $headers = @{
        "Content-Type" = $ContentType
        "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin"))
    }
    
    $uri = "http://localhost:3000/api$Endpoint"
    
    try {
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers -Body $jsonBody
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Headers $headers
        }
        return $response
    } catch {
        Write-Host "❌ API Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Step 1: Add Prometheus Data Source
Write-Host "📊 Adding Prometheus Data Source..." -ForegroundColor Cyan

$datasource = @{
    name = "HAK-GAL Prometheus"
    type = "prometheus"
    access = "proxy"
    url = "http://localhost:8000"
    isDefault = $true
    editable = $true
    jsonData = @{
        httpMethod = "GET"
        queryTimeout = "60s"
        timeInterval = "5s"
    }
}

$result = Invoke-GrafanaAPI -Method "POST" -Endpoint "/datasources" -Body $datasource

if ($result) {
    Write-Host "✅ Prometheus Data Source added successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Data Source might already exist, continuing..." -ForegroundColor Yellow
}

# Step 2: Create Dashboard
Write-Host "📈 Creating HAK-GAL Dashboard..." -ForegroundColor Cyan

$dashboard = @{
    dashboard = @{
        id = $null
        title = "HAK-GAL System Metrics"
        tags = @("hakgal", "system", "monitoring")
        timezone = "browser"
        panels = @(
            @{
                id = 1
                title = "Facts Count"
                type = "stat"
                targets = @(
                    @{
                        expr = "hakgal_facts_total"
                        refId = "A"
                    }
                )
                fieldConfig = @{
                    defaults = @{
                        color = @{ mode = "thresholds" }
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ color = "green"; value = $null }
                                @{ color = "red"; value = 1000 }
                            )
                        }
                        unit = "short"
                    }
                }
                gridPos = @{ h = 8; w = 6; x = 0; y = 0 }
            },
            @{
                id = 2
                title = "CPU Usage"
                type = "stat"
                targets = @(
                    @{
                        expr = "hakgal_system_cpu_percent"
                        refId = "A"
                    }
                )
                fieldConfig = @{
                    defaults = @{
                        color = @{ mode = "thresholds" }
                        max = 100
                        min = 0
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ color = "green"; value = $null }
                                @{ color = "yellow"; value = 70 }
                                @{ color = "red"; value = 90 }
                            )
                        }
                        unit = "percent"
                    }
                }
                gridPos = @{ h = 8; w = 6; x = 6; y = 0 }
            },
            @{
                id = 3
                title = "Memory Usage"
                type = "stat"
                targets = @(
                    @{
                        expr = "hakgal_system_memory_percent"
                        refId = "A"
                    }
                )
                fieldConfig = @{
                    defaults = @{
                        color = @{ mode = "thresholds" }
                        max = 100
                        min = 0
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ color = "green"; value = $null }
                                @{ color = "yellow"; value = 70 }
                                @{ color = "red"; value = 90 }
                            )
                        }
                        unit = "percent"
                    }
                }
                gridPos = @{ h = 8; w = 6; x = 12; y = 0 }
            },
            @{
                id = 4
                title = "Query Time"
                type = "stat"
                targets = @(
                    @{
                        expr = "hakgal_query_time_seconds"
                        refId = "A"
                    }
                )
                fieldConfig = @{
                    defaults = @{
                        color = @{ mode = "thresholds" }
                        thresholds = @{
                            mode = "absolute"
                            steps = @(
                                @{ color = "green"; value = $null }
                                @{ color = "yellow"; value = 0.1 }
                                @{ color = "red"; value = 0.5 }
                            )
                        }
                        unit = "s"
                    }
                }
                gridPos = @{ h = 8; w = 6; x = 18; y = 0 }
            }
        )
        time = @{ from = "now-1h"; to = "now" }
        refresh = "5s"
    }
    overwrite = $true
}

$dashboardResult = Invoke-GrafanaAPI -Method "POST" -Endpoint "/dashboards/db" -Body $dashboard

if ($dashboardResult) {
    Write-Host "✅ HAK-GAL Dashboard created successfully!" -ForegroundColor Green
    Write-Host "🌐 Dashboard URL: http://localhost:3000/d/hakgal-system-metrics/hak-gal-system-metrics" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to create dashboard" -ForegroundColor Red
}

Write-Host "`n🎉 Grafana setup complete!" -ForegroundColor Green
Write-Host "📊 Access Grafana at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔑 Login: admin / admin" -ForegroundColor Yellow
