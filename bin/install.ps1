if((Get-WmiObject Win32_Processor).AddressWidth == 32){
    $ARCH = "_x86"
} else{ $ARCH = "" }

$loc = "$env:APPDATA\sv-dlp"
$win_binary_url = "https://github.com/juanpisuribe13/sv-dlp/releases/latest/download/dishook$ARCH.exe"

mkdir $loc
setx PATH "$env:path;$loc"

Start-BitsTransfer -Source $win32_binary_url -Destination $loc\sv-dlp.exe
Write-Output "Installed! Please start a new terminal session"