/**
 * AI Smart Car Control - WebRTC Module
 * This module handles WebRTC video streaming.
 */

// WebRTC configuration
window.webrtcConfig = {
    video: {
        width: 1280,
        height: 720,
        frameRate: 30
    },
    audio: false
};

// WebRTC variables
let peerConnection = null;
let videoStream = null;

/**
 * Initialize WebRTC
 */
function initWebRTC() {
    console.log('Initializing WebRTC...');
    
    // Check if WebRTC is supported
    if (!navigator.mediaDevices || !window.RTCPeerConnection) {
        console.error('WebRTC is not supported in this browser.');
        updateStatus('WebRTC not supported');
        return;
    }
    
    // Create a new peer connection
    createPeerConnection();
}

/**
 * Create a new WebRTC peer connection
 */
function createPeerConnection() {
    console.log('Creating peer connection...');
    
    // Create a new RTCPeerConnection
    peerConnection = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:stun.l.google.com:19302' }
        ]
    });
    
    // Set up event handlers
    peerConnection.ontrack = handleTrack;
    peerConnection.onicecandidate = handleIceCandidate;
    peerConnection.oniceconnectionstatechange = handleIceConnectionStateChange;
    
    // Create an offer
    createOffer();
}

/**
 * Create a WebRTC offer
 */
async function createOffer() {
    console.log('Creating offer...');
    
    try {
        // Create an offer
        const offer = await peerConnection.createOffer();
        
        // Set the local description
        await peerConnection.setLocalDescription(offer);
        
        // Send the offer to the server
        sendOffer(peerConnection.localDescription);
    } catch (error) {
        console.error('Error creating offer:', error);
    }
}

/**
 * Send the WebRTC offer to the server
 * 
 * @param {RTCSessionDescription} offer - The WebRTC offer
 */
function sendOffer(offer) {
    console.log('Sending offer to server...');
    
    // Send the offer to the server
    fetch('/api/webrtc/offer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sdp: offer.sdp,
            type: offer.type
        })
    })
    .then(response => response.json())
    .then(answer => {
        console.log('Received answer from server.');
        
        // Set the remote description
        const remoteDesc = new RTCSessionDescription(answer);
        peerConnection.setRemoteDescription(remoteDesc).catch(error => {
            console.error('Error setting remote description:', error);
        });
    })
    .catch(error => {
        console.error('Error sending offer:', error);
    });
}

/**
 * Handle incoming tracks
 * 
 * @param {RTCTrackEvent} event - The track event
 */
function handleTrack(event) {
    console.log('Received track:', event.track.kind);
    
    if (event.track.kind === 'video') {
        // Get the video element
        const videoElement = document.getElementById('remote-video');
        
        // Set the video stream
        if (videoElement.srcObject !== event.streams[0]) {
            videoElement.srcObject = event.streams[0];
            console.log('Video stream set.');
        }
    }
}

/**
 * Handle ICE candidates
 * 
 * @param {RTCPeerConnectionIceEvent} event - The ICE candidate event
 */
function handleIceCandidate(event) {
    if (event.candidate) {
        console.log('ICE candidate:', event.candidate);
    }
}

/**
 * Handle ICE connection state changes
 */
function handleIceConnectionStateChange() {
    console.log('ICE connection state:', peerConnection.iceConnectionState);
    
    if (peerConnection.iceConnectionState === 'disconnected' ||
        peerConnection.iceConnectionState === 'failed' ||
        peerConnection.iceConnectionState === 'closed') {
        // Reconnect if the connection is lost
        console.log('ICE connection lost, reconnecting...');
        restartWebRTC();
    }
}

/**
 * Restart the WebRTC connection
 */
function restartWebRTC() {
    console.log('Restarting WebRTC connection...');
    
    // Close the existing connection
    if (peerConnection) {
        peerConnection.close();
        peerConnection = null;
    }
    
    // Create a new connection
    setTimeout(() => {
        createPeerConnection();
    }, 1000);
} 