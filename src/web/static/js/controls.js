/**
 * AI Smart Car Control - Controls Module
 * This module handles joystick controls for movement and camera.
 */

// Joystick variables
let movementJoystick = null;
let cameraJoystick = null;

// Joystick state
let movementJoystickActive = false;
let cameraJoystickActive = false;
let lastMovementX = 0;
let lastMovementY = 0;
let lastCameraX = 0;
let lastCameraY = 0;

/**
 * Initialize joysticks
 */
function initJoysticks() {
    console.log('Initializing joysticks...');
    
    // Create movement joystick
    const movementJoystickElement = document.getElementById('movement-joystick');
    movementJoystick = createJoystick(movementJoystickElement, handleMovementJoystick);
    
    // Create camera joystick
    const cameraJoystickElement = document.getElementById('camera-joystick');
    cameraJoystick = createJoystick(cameraJoystickElement, handleCameraJoystick);
    
    // Start joystick update loop
    startJoystickUpdateLoop();
}

/**
 * Create a joystick
 * 
 * @param {HTMLElement} element - The joystick container element
 * @param {Function} handler - The joystick event handler
 * @returns {Object} The joystick instance
 */
function createJoystick(element, handler) {
    return nipplejs.create({
        zone: element,
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: 'var(--accent-color)',
        size: 100
    }).on('start move end', handler);
}

/**
 * Handle movement joystick events
 * 
 * @param {Event} evt - The joystick event
 * @param {Object} data - The joystick data
 */
function handleMovementJoystick(evt, data) {
    if (evt.type === 'start') {
        movementJoystickActive = true;
    } else if (evt.type === 'end') {
        movementJoystickActive = false;
        lastMovementX = 0;
        lastMovementY = 0;
        
        // Send stop command when joystick is released
        sendJoystickData('movement', 0, 0);
    } else if (evt.type === 'move') {
        // Calculate normalized x and y values (-1 to 1)
        const x = Math.cos(data.angle.radian) * Math.min(1, data.distance / 50);
        const y = Math.sin(data.angle.radian) * Math.min(1, data.distance / 50);
        
        // Update last values
        lastMovementX = x;
        lastMovementY = y;
    }
}

/**
 * Handle camera joystick events
 * 
 * @param {Event} evt - The joystick event
 * @param {Object} data - The joystick data
 */
function handleCameraJoystick(evt, data) {
    if (evt.type === 'start') {
        cameraJoystickActive = true;
    } else if (evt.type === 'end') {
        cameraJoystickActive = false;
        lastCameraX = 0;
        lastCameraY = 0;
        
        // Send stop command when joystick is released
        sendJoystickData('camera', 0, 0);
    } else if (evt.type === 'move') {
        // Calculate normalized x and y values (-1 to 1)
        const x = Math.cos(data.angle.radian) * Math.min(1, data.distance / 50);
        const y = Math.sin(data.angle.radian) * Math.min(1, data.distance / 50);
        
        // Update last values
        lastCameraX = x;
        lastCameraY = y;
    }
}

/**
 * Start the joystick update loop
 */
function startJoystickUpdateLoop() {
    // Send joystick data at a fixed interval
    setInterval(() => {
        // Send movement joystick data if active
        if (movementJoystickActive) {
            sendJoystickData('movement', lastMovementX, lastMovementY);
        }
        
        // Send camera joystick data if active
        if (cameraJoystickActive) {
            sendJoystickData('camera', lastCameraX, lastCameraY);
        }
    }, 100); // 10 Hz update rate
}

/**
 * Send joystick data to the server
 * 
 * @param {string} type - The joystick type ('movement' or 'camera')
 * @param {number} x - The x-axis value (-1 to 1)
 * @param {number} y - The y-axis value (-1 to 1)
 */
function sendJoystickData(type, x, y) {
    // Round to 2 decimal places
    x = Math.round(x * 100) / 100;
    y = Math.round(y * 100) / 100;
    
    // Send the joystick data to the server
    socket.emit('joystick', {
        type: type,
        x: x,
        y: y
    });
    
    // Update the HUD
    if (type === 'movement') {
        // Update direction and speed based on joystick position
        updateJoystickHUD(x, y);
    } else if (type === 'camera') {
        // Camera angles are updated by the server
    }
}

/**
 * Update the HUD based on joystick position
 * 
 * @param {number} x - The x-axis value (-1 to 1)
 * @param {number} y - The y-axis value (-1 to 1)
 */
function updateJoystickHUD(x, y) {
    // Calculate the distance from the center
    const distance = Math.sqrt(x*x + y*y);
    
    // Update the speed value
    updateSpeedValue(distance);
    
    // Update the direction value
    if (distance < 0.1) {
        updateDirectionValue('STOP');
    } else {
        // Calculate the angle
        const angle = Math.atan2(y, x);
        
        // Determine the direction based on the angle
        if (-Math.PI/4 <= angle && angle <= Math.PI/4) {
            updateDirectionValue('RIGHT');
        } else if (Math.PI/4 < angle && angle <= 3*Math.PI/4) {
            updateDirectionValue('FORWARD');
        } else if (-3*Math.PI/4 <= angle && angle < -Math.PI/4) {
            updateDirectionValue('BACKWARD');
        } else {
            updateDirectionValue('LEFT');
        }
    }
} 