/**
 * AI Smart Car Control - Voice Module
 * This module handles voice recognition.
 */

// Voice recognition variables
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

/**
 * Initialize voice recognition
 */
function initVoiceRecognition() {
    console.log('Initializing voice recognition...');
    
    // Get the voice button
    const voiceButton = document.getElementById('voice-button');
    const voiceStatus = document.getElementById('voice-status');
    
    // Check if the browser supports the MediaRecorder API
    if (!window.MediaRecorder) {
        console.error('MediaRecorder is not supported in this browser.');
        voiceStatus.textContent = 'Voice recognition not supported';
        voiceButton.disabled = true;
        return;
    }
    
    // Add event listeners to the voice button
    voiceButton.addEventListener('mousedown', startRecording);
    voiceButton.addEventListener('touchstart', startRecording);
    voiceButton.addEventListener('mouseup', stopRecording);
    voiceButton.addEventListener('touchend', stopRecording);
    voiceButton.addEventListener('mouseleave', stopRecording);
}

/**
 * Request microphone permission
 */
function requestMicrophonePermission() {
    console.log('Requesting microphone permission...');
    
    const permissionsStatus = document.getElementById('permissions-status');
    
    // Request microphone access
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            console.log('Microphone permission granted.');
            permissionsStatus.textContent = 'Microphone access granted';
            permissionsStatus.style.color = '#4dff4d';
            
            // Store the stream for later use
            window.microphoneStream = stream;
        })
        .catch(error => {
            console.error('Error requesting microphone permission:', error);
            permissionsStatus.textContent = 'Microphone access denied';
            permissionsStatus.style.color = '#ff4d4d';
        });
}

/**
 * Start recording audio
 * 
 * @param {Event} event - The event that triggered the recording
 */
function startRecording(event) {
    // Prevent default behavior for touch events
    if (event.type === 'touchstart') {
        event.preventDefault();
    }
    
    console.log('Starting voice recording...');
    
    // Check if already recording
    if (isRecording) {
        console.warn('Already recording.');
        return;
    }
    
    // Check if microphone access is granted
    if (!window.microphoneStream) {
        console.warn('Microphone access not granted.');
        requestMicrophonePermission();
        return;
    }
    
    // Update UI
    const voiceButton = document.getElementById('voice-button');
    const voiceStatus = document.getElementById('voice-status');
    voiceButton.classList.add('active');
    voiceStatus.textContent = 'Listening...';
    
    // Reset audio chunks
    audioChunks = [];
    
    // Create a new MediaRecorder
    try {
        mediaRecorder = new MediaRecorder(window.microphoneStream);
        
        // Set up event handlers
        mediaRecorder.ondataavailable = handleAudioData;
        mediaRecorder.onstop = handleRecordingStop;
        
        // Start recording
        mediaRecorder.start();
        isRecording = true;
    } catch (error) {
        console.error('Error starting recording:', error);
        voiceStatus.textContent = 'Error starting recording';
    }
}

/**
 * Stop recording audio
 * 
 * @param {Event} event - The event that triggered the stop
 */
function stopRecording(event) {
    // Prevent default behavior for touch events
    if (event && event.type === 'touchend') {
        event.preventDefault();
    }
    
    // Check if recording
    if (!isRecording || !mediaRecorder) {
        return;
    }
    
    console.log('Stopping voice recording...');
    
    // Update UI
    const voiceButton = document.getElementById('voice-button');
    const voiceStatus = document.getElementById('voice-status');
    voiceButton.classList.remove('active');
    voiceStatus.textContent = 'Processing...';
    
    // Stop recording
    mediaRecorder.stop();
    isRecording = false;
}

/**
 * Handle audio data
 * 
 * @param {BlobEvent} event - The blob event containing the audio data
 */
function handleAudioData(event) {
    // Add the audio chunk to the array
    audioChunks.push(event.data);
}

/**
 * Handle recording stop
 */
function handleRecordingStop() {
    console.log('Recording stopped.');
    
    // Update UI
    const voiceStatus = document.getElementById('voice-status');
    voiceStatus.textContent = 'Processing...';
    
    // Create a blob from the audio chunks
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    
    // Convert the blob to base64
    const reader = new FileReader();
    reader.readAsDataURL(audioBlob);
    reader.onloadend = function() {
        // Get the base64 data
        const base64data = reader.result.split(',')[1];
        
        // Send the audio data to the server
        sendAudioData(base64data);
    };
}

/**
 * Send audio data to the server
 * 
 * @param {string} base64data - The base64-encoded audio data
 */
function sendAudioData(base64data) {
    console.log('Sending audio data to server...');
    
    // Update UI
    const voiceStatus = document.getElementById('voice-status');
    
    // Send the audio data to the server
    socket.emit('voice', { audio: base64data });
    
    // Update UI
    voiceStatus.textContent = 'Press and hold to speak';
} 