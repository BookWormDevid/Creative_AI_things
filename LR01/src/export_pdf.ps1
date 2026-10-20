$ErrorActionPreference = 'Stop'
$labFolder = Split-Path -Parent $PSScriptRoot
$labWord = $null
$labDocument = $null
$labLayout = @{}
try {
    $labWord = New-Object -ComObject Word.Application
    $labWord.Visible = $false
    $labWord.DisplayAlerts = 0
    foreach ($labName in @('report')) {
        $labDocx = Join-Path $labFolder ('reports\' + $labName + '.docx')
        $labPdf = [System.IO.Path]::ChangeExtension($labDocx, '.pdf')
        $labDocument = $labWord.Documents.Open($labDocx, $false, $true)
        $labDocument.Repaginate()
        $labDocument.ExportAsFixedFormat($labPdf, 17)
        $labLayout[$labName] = $labDocument.ComputeStatistics(2)
        $labDocument.Close(0)
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($labDocument) | Out-Null
        $labDocument = $null
    }
    $labLayout | ConvertTo-Json -Compress
} finally {
    if ($null -ne $labDocument) { $labDocument.Close(0) }
    if ($null -ne $labWord) {
        $labWord.Quit()
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($labWord) | Out-Null
    }
}
