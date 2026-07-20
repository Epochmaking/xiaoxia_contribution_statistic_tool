#include <Windows.h>

int main()
{
    ShellExecuteA(
        NULL,
        "open",
        "xiaoxia_tool.exe",   // exe
        NULL,
        "bin",        // working directory
        SW_SHOWNORMAL
    );
    return 0;
}
