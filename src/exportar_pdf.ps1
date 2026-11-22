param([string]$Docx, [string]$Pdf)
# Abre o .docx no Word, atualiza sumário/campos, ajusta estilos do sumário e exporta para PDF.
$ErrorActionPreference = "Stop"
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($Docx)
    $d.Fields.Update() | Out-Null
    $d.TablesOfContents.Item(1).Update()
    # estilos do sumário: Times 12, sem recuo de 1ª linha; nível 1 em negrito
    foreach ($i in -20, -21, -22) {
        $s = $d.Styles.Item($i)
        $s.Font.Name = "Times New Roman"; $s.Font.Size = 12; $s.Font.Color = 0
        $s.ParagraphFormat.FirstLineIndent = 0
        $s.ParagraphFormat.Alignment = 0
        $s.ParagraphFormat.SpaceBefore = 0
        $s.ParagraphFormat.SpaceAfter = 4
    }
    $d.Styles.Item(-20).Font.Bold = $true
    $d.Repaginate()
    $d.TablesOfContents.Item(1).Update()
    $d.TablesOfContents.Item(1).UpdatePageNumbers()
    $d.Save()
    $d.ExportAsFixedFormat($Pdf, 17)
    "paginas: " + $d.ComputeStatistics(2)
    "pdf: " + $Pdf
    $d.Close(0)
}
finally {
    $w.Quit()
}
