/**
 * AI Smart Car Control - Main Application Script
 * This script initializes and coordinates all the components of the web interface.
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initApp();
});

/**
 * Initialize the application
 */
function initApp() {
    console.log('Initializing AI Smart Car Control application...');
    
    // Initialize components
    initSocketConnection();
    initWebRTC();
    initJoysticks();
    initVoiceRecognition();
    initChatInterface();
    initSettingsModal();
    
    // Update status
    updateStatus('Initializing...');
    
    console.log('Application initialized.');
}

/**
 * Initialize the Socket.IO connection
 */
function initSocketConnection() {
    console.log('Initializing Socket.IO connection...');
    
    // Create a new Socket.IO connection
    window.socket = io();
    
    // Connection event handlers
    socket.on('connect', function() {
        console.log('Socket.IO connected.');
        updateStatus('Connected');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Socket.IO disconnected.');
        updateStatus('Disconnected');
        updateConnectionStatus(false);
    });
    
    socket.on('status', function(data) {
        console.log('Received status:', data);
        updateStatus(data.status);
    });
    
    // Control response handlers
    socket.on('control_response', function(data) {
        console.log('Received control response:', data);
        if (data.status === 'ok') {
            // Update UI based on the control response
            if (data.result && data.result.direction) {
                updateDirectionValue(data.result.direction);
            }
            if (data.result && data.result.speed !== undefined) {
                updateSpeedValue(data.result.speed);
            }
        } else {
            console.error('Control error:', data.message);
        }
    });
    
    // Joystick response handlers
    socket.on('joystick_response', function(data) {
        console.log('Received joystick response:', data);
    });
    
    // Voice response handlers
    socket.on('voice_response', function(data) {
        console.log('Received voice response:', data);
        if (data.status === 'ok') {
            // Add the transcription and response to the chat
            addMessage('user', data.result.transcription);
            addMessage('ai', data.result.response);
        } else {
            console.error('Voice error:', data.message);
        }
    });
    
    // Text response handlers
    socket.on('text_response', function(data) {
        console.log('Received text response:', data);
        if (data.status === 'ok') {
            // Add the response to the chat
            addMessage('ai', data.result.response);
        } else {
            console.error('Text error:', data.message);
        }
    });
}

/**
 * Initialize the chat interface
 */
function initChatInterface() {
    console.log('Initializing chat interface...');
    
    const chatInput = document.getElementById('chat-input');
    const chatSend = document.getElementById('chat-send');
    
    // Send button click handler
    chatSend.addEventListener('click', function() {
        sendChatMessage();
    });
    
    // Enter key handler
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

/**
 * Send a chat message
 */
function sendChatMessage() {
    const chatInput = document.getElementById('chat-input');
    const text = chatInput.value.trim();
    
    if (text) {
        console.log('Sending chat message:', text);
        
        // Add the message to the chat
        addMessage('user', text);
        
        // Send the message to the server
        socket.emit('text', { text: text });
        
        // Clear the input
        chatInput.value = '';
    }
}

/**
 * Add a message to the chat
 * 
 * @param {string} type - The type of message ('user' or 'ai')
 * @param {string} text - The message text
 */
function addMessage(type, text) {
    const chatMessages = document.getElementById('chat-messages');
    
    // Create a new message element
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(type === 'user' ? 'user-message' : 'ai-message');
    messageElement.textContent = text;
    
    // Add the message to the chat
    chatMessages.appendChild(messageElement);
    
    // Scroll to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Initialize the settings modal
 */
function initSettingsModal() {
    console.log('Initializing settings modal...');
    
    const settingsButton = document.getElementById('settings-button');
    const settingsModal = document.getElementById('settings-modal');
    const closeButton = document.querySelector('.close-button');
    
    // Settings controls
    const voiceVolume = document.getElementById('voice-volume');
    const voiceVolumeValue = document.getElementById('voice-volume-value');
    const voiceRate = document.getElementById('voice-rate');
    const voiceRateValue = document.getElementById('voice-rate-value');
    const videoQuality = document.getElementById('video-quality');
    const requestPermissions = document.getElementById('request-permissions');
    
    // Open modal
    settingsButton.addEventListener('click', function() {
        settingsModal.style.display = 'block';
    });
    
    // Close modal
    closeButton.addEventListener('click', function() {
        settingsModal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === settingsModal) {
            settingsModal.style.display = 'none';
        }
    });
    
    // Voice volume change
    voiceVolume.addEventListener('input', function() {
        const volume = parseFloat(voiceVolume.value);
        voiceVolumeValue.textContent = `${Math.round(volume * 100)}%`;
        
        // Send the volume to the server
        socket.emit('control', {
            command: 'voice',
            params: {
                action: 'volume',
                value: volume
            }
        });
    });
    
    // Voice rate change
    voiceRate.addEventListener('input', function() {
        const rate = parseInt(voiceRate.value);
        voiceRateValue.textContent = `${rate} wpm`;
        
        // Send the rate to the server
        socket.emit('control', {
            command: 'voice',
            params: {
                action: 'rate',
                value: rate
            }
        });
    });
    
    // Video quality change
    videoQuality.addEventListener('change', function() {
        const quality = videoQuality.value;
        console.log('Video quality changed:', quality);
        
        // Update WebRTC configuration
        updateVideoQuality(quality);
    });
    
    // Request permissions
    requestPermissions.addEventListener('click', function() {
        requestMicrophonePermission();
    });
}

/**
 * Update the video quality
 * 
 * @param {string} quality - The video quality ('low', 'medium', or 'high')
 */
function updateVideoQuality(quality) {
    // Update WebRTC configuration based on quality
    let width, height;
    
    switch (quality) {
        case 'low':
            width = 640;
            height = 480;
            break;
        case 'medium':
            width = 1280;
            height = 720;
            break;
        case 'high':
            width = 1920;
            height = 1080;
            break;
        default:
            width = 1280;
            height = 720;
    }
    
    // Update WebRTC configuration
    if (window.webrtcConfig) {
        window.webrtcConfig.video.width = width;
        window.webrtcConfig.video.height = height;
        
        // Restart WebRTC connection
        restartWebRTC();
    }
}

/**
 * Update the status text
 * 
 * @param {string} status - The status text
 */
function updateStatus(status) {
    const statusText = document.getElementById('status-text');
    statusText.textContent = status;
}

/**
 * Update the connection status indicator
 * 
 * @param {boolean} connected - Whether the connection is established
 */
function updateConnectionStatus(connected) {
    const connectionStatus = document.getElementById('connection-status');
    
    if (connected) {
        connectionStatus.classList.remove('disconnected');
        connectionStatus.classList.add('connected');
    } else {
        connectionStatus.classList.remove('connected');
        connectionStatus.classList.add('disconnected');
    }
}

/**
 * Update the direction value in the HUD
 * 
 * @param {string} direction - The direction value
 */
function updateDirectionValue(direction) {
    const directionValue = document.getElementById('direction-value');
    directionValue.textContent = direction.toUpperCase();
}

/**
 * Update the speed value in the HUD
 * 
 * @param {number} speed - The speed value
 */
function updateSpeedValue(speed) {
    const speedValue = document.getElementById('speed-value');
    speedValue.textContent = Math.round(speed * 100) + '%';
}

/**
 * Update the camera angle value in the HUD
 * 
 * @param {number} horizontalAngle - The horizontal angle
 * @param {number} verticalAngle - The vertical angle
 */
function updateCameraAngleValue(horizontalAngle, verticalAngle) {
    const cameraAngleValue = document.getElementById('camera-angle-value');
    cameraAngleValue.textContent = `H: ${Math.round(horizontalAngle)}° V: ${Math.round(verticalAngle)}°`;
} 