// Configuration automatique de l'adresse IP du serveur
window.getServerUrl = function() {
    // Si on est sur le même réseau que le serveur, utiliser l'IP actuelle
    // Sinon, essayer de se connecter à localhost
    const hostname = window.location.hostname;
    const port = window.location.port || 5000;
    
    // Si on accède via IP, utiliser cette IP pour Socket.IO
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return `http://${hostname}:${port}`;
    }
    
    // Sinon, essayer localhost
    return `http://localhost:${port}`;
};

// URL du serveur Socket.IO
window.SOCKET_IO_URL = window.getServerUrl();
