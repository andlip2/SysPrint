const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            preload: path.join(__dirname, 'preload.js'), // Usar o arquivo preload.js para permitir IPC
        }
    });

    // Carregar a tela de login inicialmente
    mainWindow.loadFile('frontend/login.html');

    // Quando o login for bem-sucedido, carregue o dashboard
    ipcMain.on('open-dashboard', () => {
        mainWindow.loadFile('frontend/dashboard.html'); // Carrega a tela principal após login
    });

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
