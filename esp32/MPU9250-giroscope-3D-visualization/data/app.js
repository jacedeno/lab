// ============================================================
// 1. WebSocket Client
// ============================================================

let socket = null;
let frameCount = 0;
let msgCount = 0;
let lastHzTime = performance.now();

function connectWebSocket() {
    const host = window.location.hostname || '192.168.4.1';
    socket = new WebSocket('ws://' + host + '/ws');

    socket.onopen = function () {
        document.getElementById('status-dot').className = 'dot connected';
        document.getElementById('status-text').textContent = 'Connected';
        document.getElementById('ws-status').textContent = 'Connected';
    };

    socket.onclose = function () {
        document.getElementById('status-dot').className = 'dot disconnected';
        document.getElementById('status-text').textContent = 'Reconnecting...';
        document.getElementById('ws-status').textContent = 'Disconnected';
        setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = function () {
        socket.close();
    };

    socket.onmessage = function (evt) {
        try {
            const d = JSON.parse(evt.data);
            msgCount++;
            frameCount++;
            onSensorData(d);
        } catch (e) {
            // skip malformed frame
        }
    };
}

// Hz counter
setInterval(function () {
    const now = performance.now();
    const elapsed = (now - lastHzTime) / 1000;
    const hz = Math.round(msgCount / elapsed);
    document.getElementById('hz-display').textContent = hz + ' Hz';
    document.getElementById('rate-status').textContent = hz + ' Hz';
    msgCount = 0;
    lastHzTime = now;
}, 1000);

connectWebSocket();

// ============================================================
// 2. Three.js Scene + Shuttle Model
// ============================================================

const viewport = document.getElementById('viewport');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0a1a);

const camera = new THREE.PerspectiveCamera(
    50, viewport.clientWidth / viewport.clientHeight, 0.1, 100
);
camera.position.set(4, 3, 5);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(viewport.clientWidth, viewport.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio);
viewport.appendChild(renderer.domElement);

// Grid and axes
scene.add(new THREE.GridHelper(10, 10, 0x333355, 0x1a1a3a));
scene.add(new THREE.AxesHelper(3));

// Lighting
scene.add(new THREE.AmbientLight(0x404040, 1.5));
const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);

// Build shuttle model
const shuttle = new THREE.Group();

// Fuselage
const fuselage = new THREE.Mesh(
    new THREE.BoxGeometry(0.6, 0.4, 3.0),
    new THREE.MeshPhongMaterial({ color: 0xeeeeee })
);
shuttle.add(fuselage);

// Nose cone
const nose = new THREE.Mesh(
    new THREE.ConeGeometry(0.25, 0.8, 8),
    new THREE.MeshPhongMaterial({ color: 0x222222 })
);
nose.rotation.x = -Math.PI / 2;
nose.position.z = 1.9;
shuttle.add(nose);

// Wings
const wingGeo = new THREE.BoxGeometry(1.5, 0.05, 1.0);
const wingMat = new THREE.MeshPhongMaterial({ color: 0x444444 });

const wingL = new THREE.Mesh(wingGeo, wingMat);
wingL.position.set(-0.9, 0, -0.3);
shuttle.add(wingL);

const wingR = new THREE.Mesh(wingGeo, wingMat);
wingR.position.set(0.9, 0, -0.3);
shuttle.add(wingR);

// Tail fin
const tail = new THREE.Mesh(
    new THREE.BoxGeometry(0.05, 0.8, 0.6),
    new THREE.MeshPhongMaterial({ color: 0x2244aa })
);
tail.position.set(0, 0.45, -1.2);
shuttle.add(tail);

// Engines (3)
const engineGeo = new THREE.CylinderGeometry(0.1, 0.12, 0.3, 8);
const engineMat = new THREE.MeshPhongMaterial({ color: 0xff6600 });

for (let i = -1; i <= 1; i++) {
    const eng = new THREE.Mesh(engineGeo, engineMat);
    eng.rotation.x = Math.PI / 2;
    eng.position.set(i * 0.2, 0, -1.6);
    shuttle.add(eng);
}

// Cargo bay
const cargo = new THREE.Mesh(
    new THREE.BoxGeometry(0.5, 0.02, 1.5),
    new THREE.MeshPhongMaterial({ color: 0xaaaaaa })
);
cargo.position.y = 0.21;
shuttle.add(cargo);

scene.add(shuttle);

// Handle resize
window.addEventListener('resize', function () {
    camera.aspect = viewport.clientWidth / viewport.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(viewport.clientWidth, viewport.clientHeight);
});

// ============================================================
// 3. Rolling Charts (Canvas 2D)
// ============================================================

function RollingChart(canvasId, minVal, maxVal) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.bufferSize = 100;
    this.min = minVal;
    this.max = maxVal;
    this.dataX = [];
    this.dataY = [];
    this.dataZ = [];
}

RollingChart.prototype.push = function (x, y, z) {
    this.dataX.push(x);
    this.dataY.push(y);
    this.dataZ.push(z);
    if (this.dataX.length > this.bufferSize) {
        this.dataX.shift();
        this.dataY.shift();
        this.dataZ.shift();
    }
};

RollingChart.prototype.draw = function () {
    const c = this.canvas;
    const ctx = this.ctx;
    const w = c.width;
    const h = c.height;

    ctx.clearRect(0, 0, w, h);

    // Zero line
    const zeroY = h * (this.max / (this.max - this.min));
    ctx.strokeStyle = '#333355';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, zeroY);
    ctx.lineTo(w, zeroY);
    ctx.stroke();

    var datasets = [
        { data: this.dataX, color: '#ff4444' },
        { data: this.dataY, color: '#44ff44' },
        { data: this.dataZ, color: '#4488ff' }
    ];

    for (var d = 0; d < datasets.length; d++) {
        var arr = datasets[d].data;
        ctx.strokeStyle = datasets[d].color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        for (var i = 0; i < arr.length; i++) {
            var px = (i / (this.bufferSize - 1)) * w;
            var py = h - ((arr[i] - this.min) / (this.max - this.min)) * h;
            if (i === 0) ctx.moveTo(px, py);
            else ctx.lineTo(px, py);
        }
        ctx.stroke();
    }
};

const accelChart = new RollingChart('accel-chart', -20, 20);
const gyroChart = new RollingChart('gyro-chart', -5, 5);

// ============================================================
// 4. Data Handler + Animation Loop
// ============================================================

function onSensorData(d) {
    // Update quaternion display
    document.getElementById('q-w').textContent = Number(d.w).toFixed(4);
    document.getElementById('q-x').textContent = Number(d.x).toFixed(4);
    document.getElementById('q-y').textContent = Number(d.y).toFixed(4);
    document.getElementById('q-z').textContent = Number(d.z).toFixed(4);

    // Update shuttle orientation (Three.js quaternion order: x, y, z, w)
    shuttle.quaternion.set(
        Number(d.x), Number(d.y), Number(d.z), Number(d.w)
    );

    // Push chart data
    accelChart.push(Number(d.ax), Number(d.ay), Number(d.az));
    gyroChart.push(Number(d.gx), Number(d.gy), Number(d.gz));

    // Frame count
    document.getElementById('frame-count').textContent = frameCount;
}

// Render loop
function animate() {
    requestAnimationFrame(animate);
    accelChart.draw();
    gyroChart.draw();
    renderer.render(scene, camera);
}

animate();
