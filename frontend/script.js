// ============================================================
// BACKEND
// ============================================================

const BACKEND = "http://127.0.0.1:8000";


// ============================================================
// GLOBAL DATA
// ============================================================

let cameraData = {};

let allEvents = [];

let allRecordings = [];


// ============================================================
// PAGE NAVIGATION
// ============================================================

function showPage(pageName) {

    const pages = document.querySelectorAll(".page");

    pages.forEach(page => {

        page.style.display = "none";

    });


    const selectedPage =
        document.getElementById(pageName);

    if (selectedPage) {

        selectedPage.style.display = "block";

    }


    const menuItems =
        document.querySelectorAll(".menu-item");

    menuItems.forEach(item => {

        item.classList.remove("active");

        if (
            item.dataset.page === pageName
        ) {

            item.classList.add("active");

        }

    });


    // Load page data

    if (pageName === "recordings") {

        loadRecordings();

    }

    if (pageName === "events") {

        loadEvents();

    }

    if (pageName === "analytics") {

        loadAnalytics();

    }

}


// ============================================================
// CLOCK
// ============================================================

function updateClock() {

    const now = new Date();

    const time =
        now.toLocaleTimeString();

    const clock =
        document.getElementById("clock");

    if (clock) {

        clock.textContent = time;

    }

}

setInterval(
    updateClock,
    1000
);

updateClock();


// ============================================================
// CAMERA UI
// ============================================================

function setCameraUI(
    cameraId,
    isOnline
) {

    const status =
        document.getElementById(
            `status-${cameraId}`
        );


    const button =
        document.getElementById(
            `camera-btn-${cameraId}`
        );


    const screen =
        document.getElementById(
            `screen-${cameraId}`
        );


    const image =
        document.getElementById(
            `stream-${cameraId}`
        );


    const offline =
        document.getElementById(
            `offline-${cameraId}`
        );


    const manageStatus =
        document.getElementById(
            `manage-status-${cameraId}`
        );


    if (isOnline) {

        // STATUS

        if (status) {

            status.textContent =
                "ONLINE";

            status.className =
                "online";

        }


        // BUTTON

        if (button) {

            button.textContent =
                "OFF";

        }


        // SCREEN

        if (screen) {

            screen.classList.add(
                "camera-online"
            );

        }


        // STREAM

        if (image) {

            image.style.display =
                "block";

            image.src =
                `${BACKEND}/api/camera/${cameraId}/stream?time=${Date.now()}`;

        }


        // OFFLINE MESSAGE

        if (offline) {

            offline.style.display =
                "none";

        }


        // MANAGEMENT

        if (manageStatus) {

            manageStatus.textContent =
                "ONLINE";

            manageStatus.className =
                "online";

        }

    }

    else {

        // STATUS

        if (status) {

            status.textContent =
                "OFFLINE";

            status.className =
                "offline";

        }


        // BUTTON

        if (button) {

            button.textContent =
                "ON";

        }


        // STREAM

        if (image) {

            image.src = "";

            image.style.display =
                "none";

        }


        // OFFLINE MESSAGE

        if (offline) {

            offline.style.display =
                "flex";

        }


        // MANAGEMENT

        if (manageStatus) {

            manageStatus.textContent =
                "OFFLINE";

            manageStatus.className =
                "offline";

        }

    }

}


// ============================================================
// LOAD CAMERA STATUS
// ============================================================

async function loadCameraStatus() {

    try {

        const response =
            await fetch(
                `${BACKEND}/api/cameras`
            );


        if (!response.ok) {

            throw new Error(
                "Camera API unavailable"
            );

        }


        cameraData =
            await response.json();


        let onlineCount = 0;


        for (
            let cameraId = 1;
            cameraId <= 3;
            cameraId++
        ) {

            const camera =
                cameraData[
                    String(cameraId)
                ];


            if (!camera) {

                setCameraUI(
                    cameraId,
                    false
                );

                continue;

            }


            const isOnline =
                camera.status === "online";


            setCameraUI(
                cameraId,
                isOnline
            );


            if (isOnline) {

                onlineCount++;

            }

        }


        updateCameraHealth(
            onlineCount
        );

    }

    catch (error) {

        console.error(
            "Camera status error:",
            error
        );

    }

}


// ============================================================
// CAMERA HEALTH
// ============================================================

function updateCameraHealth(
    onlineCount
) {

    const health =
        document.getElementById(
            "camera-health"
        );


    if (health) {

        health.textContent =
            `${onlineCount}/3 CAMERAS ONLINE`;

    }

}


// ============================================================
// TURN ONE CAMERA ON
// ============================================================

async function turnCameraOn(
    cameraId
) {

    try {

        const response =
            await fetch(

                `${BACKEND}/api/camera/${cameraId}/on`,

                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                `Camera ${cameraId} could not start:\n${data.detail}`
            );

            return false;

        }


        setCameraUI(
            cameraId,
            true
        );


        return true;

    }

    catch (error) {

        console.error(error);

        alert(
            `Could not connect to Camera ${cameraId}`
        );

        return false;

    }

}


// ============================================================
// TURN ONE CAMERA OFF
// ============================================================

async function turnCameraOff(
    cameraId
) {

    try {

        const response =
            await fetch(

                `${BACKEND}/api/camera/${cameraId}/off`,

                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            const data =
                await response.json();

            alert(
                `Camera ${cameraId} error:\n${data.detail}`
            );

            return false;

        }


        // IMPORTANT:
        // Immediately remove stream
        setCameraUI(
            cameraId,
            false
        );


        return true;

    }

    catch (error) {

        console.error(error);

        alert(
            `Could not turn OFF Camera ${cameraId}`
        );

        return false;

    }

}


// ============================================================
// TOGGLE CAMERA
// ============================================================

async function toggleCamera(
    cameraId
) {

    const camera =
        cameraData[
            String(cameraId)
        ];


    if (
        camera &&
        camera.status === "online"
    ) {

        await turnCameraOff(
            cameraId
        );

    }

    else {

        await turnCameraOn(
            cameraId
        );

    }


    await loadCameraStatus();

}


// ============================================================
// ALL CAMERAS ON
// ============================================================

async function turnAllCamerasOn() {

    try {

        const response =
            await fetch(

                `${BACKEND}/api/cameras/on`,

                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        console.log(
            "All cameras ON:",
            data
        );


        // Refresh UI

        await loadCameraStatus();


        // Tell user which cameras failed

        const failed = [];


        for (
            const [id, result]
            of Object.entries(
                data.cameras
            )
        ) {

            if (!result.success) {

                failed.push(
                    `Camera ${id}: ${result.message}`
                );

            }

        }


        if (failed.length > 0) {

            alert(
                "Some cameras could not start:\n\n"
                + failed.join("\n")
            );

        }

    }

    catch (error) {

        console.error(error);

        alert(
            "Could not connect to backend."
        );

    }

}


// ============================================================
// ALL CAMERAS OFF
// ============================================================

async function turnAllCamerasOff() {

    try {

        const response =
            await fetch(

                `${BACKEND}/api/cameras/off`,

                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        console.log(
            "All cameras OFF:",
            data
        );


        // Immediately clear all streams

        for (
            let cameraId = 1;
            cameraId <= 3;
            cameraId++
        ) {

            setCameraUI(
                cameraId,
                false
            );

        }


        await loadCameraStatus();

    }

    catch (error) {

        console.error(error);

        alert(
            "Could not turn cameras OFF."
        );

    }

}


// ============================================================
// STATISTICS
// ============================================================

async function loadStats() {

    try {

        const response =
            await fetch(
                `${BACKEND}/api/stats`
            );


        const data =
            await response.json();


        document.getElementById(
            "people-in"
        ).textContent =
            data.people_in;


        document.getElementById(
            "people-out"
        ).textContent =
            data.people_out;


        document.getElementById(
            "people-staying"
        ).textContent =
            data.people_staying;


        document.getElementById(
            "active-alerts"
        ).textContent =
            data.active_alerts;

    }

    catch (error) {

        console.error(
            "Stats error:",
            error
        );

    }

}


// ============================================================
// EVENTS
// ============================================================

async function loadEvents() {

    try {

        const response =
            await fetch(
                `${BACKEND}/api/events`
            );


        allEvents =
            await response.json();


        renderEvents(
            allEvents
        );


        renderRecentEvents(
            allEvents
        );

    }

    catch (error) {

        console.error(
            "Events error:",
            error
        );

    }

}


// ============================================================
// RENDER EVENTS
// ============================================================

function renderEvents(
    eventsList
) {

    const container =
        document.getElementById(
            "events-table"
        );


    if (!container) return;


    if (
        eventsList.length === 0
    ) {

        container.innerHTML =
            `<p class="empty-message">
                No events detected yet.
            </p>`;

        return;

    }


    container.innerHTML =
        eventsList.map(
            event => `

            <div class="event-item">

                <strong>
                    ${event.camera}
                </strong>

                <span>
                    ${event.objects.join(", ")}
                </span>

                <small>
                    ${event.time}
                </small>

            </div>

        `
        ).join("");

}


// ============================================================
// RECENT EVENTS
// ============================================================

function renderRecentEvents(
    eventsList
) {

    const container =
        document.getElementById(
            "recent-events"
        );


    if (!container) return;


    if (
        eventsList.length === 0
    ) {

        container.innerHTML =
            `<p class="empty-message">
                No events detected yet.
            </p>`;

        return;

    }


    const recent =
        eventsList.slice(0, 5);


    container.innerHTML =
        recent.map(
            event => `

            <div class="event-item">

                <strong>
                    ${event.camera}
                </strong>

                <span>
                    ${event.objects.join(", ")}
                </span>

                <small>
                    ${event.time}
                </small>

            </div>

        `
        ).join("");

}


// ============================================================
// EVENT FILTER
// ============================================================

function filterEvents(
    type
) {

    if (type === "ALL") {

        renderEvents(
            allEvents
        );

        return;

    }


    let filtered =
        allEvents.filter(
            event =>

                event.objects.some(
                    object =>
                        object.toUpperCase()
                        === type
                )
        );


    renderEvents(
        filtered
    );

}


// ============================================================
// RECORDINGS
// ============================================================

async function loadRecordings() {

    try {

        const response =
            await fetch(
                `${BACKEND}/api/recordings`
            );


        allRecordings =
            await response.json();


        renderRecordings(
            allRecordings
        );


    }

    catch (error) {

        console.error(
            "Recording error:",
            error
        );

    }

}


// ============================================================
// RENDER RECORDINGS
// ============================================================

function renderRecordings(
    recordings
) {

    const container =
        document.getElementById(
            "recordings-list"
        );


    if (!container) return;


    if (
        recordings.length === 0
    ) {

        container.innerHTML =
            `<p class="empty-message">
                No recordings available.
            </p>`;

        return;

    }


    container.innerHTML =
        recordings.map(
            recording => `

            <div class="recording-item">

                <div>

                    <strong>
                        ${recording.filename}
                    </strong>

                    <br>

                    <span>
                        ${recording.created}
                    </span>

                </div>

                <div>

                    <a
                        href="${BACKEND}${recording.url}"
                        target="_blank"
                        style="
                            color:#38df9a;
                            text-decoration:none;
                        "
                    >
                        OPEN
                    </a>

                    &nbsp;&nbsp;

                    <a
                        href="${BACKEND}${recording.url}"
                        download
                        style="
                            color:#ffffff;
                            text-decoration:none;
                        "
                    >
                        DOWNLOAD
                    </a>

                </div>

            </div>

        `
        ).join("");

}


// ============================================================
// RECORDING SEARCH
// ============================================================

function filterRecordings() {

    const input =
        document.getElementById(
            "recording-search"
        );


    const search =
        input.value.toLowerCase();


    const filtered =
        allRecordings.filter(
            recording =>
                recording.filename
                    .toLowerCase()
                    .includes(search)
        );


    renderRecordings(
        filtered
    );

}


// ============================================================
// ANALYTICS
// ============================================================

async function loadAnalytics() {

    try {

        const eventsResponse =
            await fetch(
                `${BACKEND}/api/events`
            );


        const eventsData =
            await eventsResponse.json();


        const recordingsResponse =
            await fetch(
                `${BACKEND}/api/recordings`
            );


        const recordingsData =
            await recordingsResponse.json();


        let totalDetections = 0;

        let totalPeople = 0;

        let totalVehicles = 0;


        eventsData.forEach(
            event => {

                event.detections.forEach(
                    detection => {

                        totalDetections++;


                        if (
                            detection.object
                            === "person"
                        ) {

                            totalPeople++;

                        }


                        const vehicles = [

                            "car",

                            "truck",

                            "bus",

                            "motorcycle"
                        ];


                        if (
                            vehicles.includes(
                                detection.object
                            )
                        ) {

                            totalVehicles++;

                        }

                    }
                );

            }
        );


        document.getElementById(
            "total-detections"
        ).textContent =
            totalDetections;


        document.getElementById(
            "total-people"
        ).textContent =
            totalPeople;


        document.getElementById(
            "total-vehicles"
        ).textContent =
            totalVehicles;


        document.getElementById(
            "total-recordings"
        ).textContent =
            recordingsData.length;

    }

    catch (error) {

        console.error(
            "Analytics error:",
            error
        );

    }

}


// ============================================================
// INITIALIZATION
// ============================================================

async function initialize() {

    await loadCameraStatus();

    await loadStats();

    await loadEvents();

}


// Start application

initialize();


// Refresh status every 2 seconds

setInterval(
    loadCameraStatus,
    2000
);


// Refresh statistics every 2 seconds

setInterval(
    loadStats,
    2000
);


// Refresh events every 5 seconds

setInterval(
    loadEvents,
    5000
);