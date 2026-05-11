import * as THREE from "three";
import { MindARThree } from "https://cdn.jsdelivr.net/npm/mind-ar@1.2.5/dist/mindar-image-three.prod.js";

// stores currently selected fault
let faultPanel = null; // stores the 3d box shown in the scene
let scene, camera, renderer; // objects for the 3d graphics
let currentFaultId = null;
let faultAnchor = null;
let nextToolIndex = 0;

const AUTH_TOKEN =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDYXJsb3MiLCJleHAiOjE3Nzg1MTE3MzR9.U_uLEnXD-Apriy0hResUtxMDl-ZkPeAw73R1LhZsEcA";

const requiredTools = [
  { id: 1, name: "Spanner", scanned: false },
  { id: 2, name: "Screwdriver", scanned: false },
  { id: 3, name: "Voltage tester", scanned: false }
];

// this just handles backend requests so i dont repeat fetch 500 times
async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${AUTH_TOKEN}`,
      ...options.headers
    }
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(JSON.stringify(data));
  }

  return data;
}

// asks backend for a fault and returns it
async function getFault(faultId) {
  return apiRequest(`/api/faults/${faultId}`);
}

// gets all tools
async function getTools() {
  return apiRequest("/api/tools");
}

// gets one tool
async function getTool(toolId) {
  return apiRequest(`/api/tools/${toolId}`);
}

// updates tool status in backend
async function updateTool(toolId, status) {
  return apiRequest(`/api/tools/${toolId}`, {
    method: "PATCH",
    body: JSON.stringify({ status })
  });
}

// updates fault status from frontend to backend
async function updateFault(faultId, status) {
  return apiRequest(`/api/faults/${faultId}`, {
    method: "PATCH",
    body: JSON.stringify({ status })
  });
}

// creates a new fault from user input
async function createFault(title, location, severity) {
  return apiRequest("/api/faults", {
    method: "POST",
    body: JSON.stringify({
      title,
      location,
      severity
    })
  });
}

// sets up the normal 3d scene
function initThreeScene() {
  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(
    70,
    window.innerWidth / window.innerHeight,
    0.01,
    100
  );

  camera.position.z = 4;

  renderer = new THREE.WebGLRenderer({
    antialias: true
  });

  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  const light = new THREE.AmbientLight(0xffffff, 1);
  scene.add(light);

  const grid = new THREE.GridHelper(10, 10);
  scene.add(grid);

  animate();
}

// creates the fault panel thing
function createFaultPanel(faultData, anchor = faultAnchor) {
  if (faultPanel && faultPanel.parent) {
    faultPanel.parent.remove(faultPanel);
  }

  const geometry = new THREE.BoxGeometry(0.6, 0.35, 0.05);

  let colour = 0x00aa00;

  if (faultData.severity === 3) {
    colour = 0xff0000;
  } else if (faultData.severity === 2) {
    colour = 0xffaa00;
  }

  const material = new THREE.MeshBasicMaterial({
    color: colour,
    transparent: true,
    opacity: 0.3,
    depthWrite: false,
    side: THREE.DoubleSide
  });

  faultPanel = new THREE.Mesh(geometry, material);
  faultPanel.position.set(0, 0.5, 0);

  if (anchor) {
    anchor.group.add(faultPanel);
  } else {
    scene.add(faultPanel);
  }
}

// updates the fault info box shown to user
function updateFaultInfo(faultData) {
  document.getElementById("faultInfo").innerHTML = `
    <strong>${faultData.title}</strong><br>
    Location: ${faultData.location}<br>
    Severity: ${faultData.severity}<br>
    Status: ${faultData.status}
  `;
}

// rotates the fault panel so it looks cool i guess
function animate() {
  requestAnimationFrame(animate);

  if (faultPanel) {
    faultPanel.rotation.y += 0.01;
  }

  renderer.render(scene, camera);
}

// updates tool checklist ui
function updateToolCheckUI() {
  const scanned_count = requiredTools.filter(
    tool => tool.scanned
  ).length;

  document.getElementById("toolInfo").textContent =
    `Tools scanned: ${scanned_count} / ${requiredTools.length}`;

  document.getElementById("toolList").innerHTML = requiredTools
    .map(tool =>
      `<li>${tool.name}: ${tool.scanned ? "present" : "missing"}</li>`
    )
    .join("");
}

// fake markers for testing
function createSimulatedMarkers() {
  const markerPositions = {
    1: { x: -2, y: -1.2, z: 0 },
    2: { x: 0, y: -1.2, z: 0 },
    3: { x: 2, y: -1.2, z: 0 }
  };

  Object.entries(markerPositions).forEach(([id, position]) => {
    const geometry = new THREE.PlaneGeometry(0.8, 0.8);

    const material = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      wireframe: true
    });

    const marker = new THREE.Mesh(geometry, material);

    marker.position.set(position.x, position.y, position.z);

    scene.add(marker);

    const label = createTextSprite(`Marker ${id}`);
    label.position.set(position.x, position.y + 0.7, position.z);

    scene.add(label);
  });
}

// makes text labels for markers
function createTextSprite(text) {
  const canvas = document.createElement("canvas");
  const context = canvas.getContext("2d");

  canvas.width = 256;
  canvas.height = 128;

  context.fillStyle = "white";
  context.font = "32px Arial";
  context.textAlign = "center";
  context.fillText(text, 128, 64);

  const texture = new THREE.CanvasTexture(canvas);

  const material = new THREE.SpriteMaterial({
    map: texture
  });

  const sprite = new THREE.Sprite(material);

  sprite.scale.set(1.5, 0.75, 1);

  return sprite;
}

// starts the AR scene
async function initARScene() {
  console.log("initARScene started");

  const mindarThree = new MindARThree({
    container: document.body,
    imageTargetSrc: "/static/targets.mind"
  });

const markerFaultMap = {
  0: 1,
  1: 2,
  2: 3
};

Object.entries(markerFaultMap).forEach(([marker_index, fault_id]) => {
  const faultAnchor = mindarThree.addAnchor(Number(marker_index));

  faultAnchor.onTargetFound = async () => {
    console.log(`Fault marker ${marker_index} detected`);

    current_fault_id = fault_id;

    try {
      const fault_data = await getFault(current_fault_id);

      updateFaultInfo(fault_data);
      closeFaultBtn.disabled = false;

      createFaultPanel(fault_data, faultAnchor);
    } catch (error) {
      document.getElementById("faultInfo").innerText =
        "Could not load fault from backend.";

      console.error(error);
    }
  };
});


  renderer = mindarThree.renderer;
  scene = mindarThree.scene;
  camera = mindarThree.camera;


    try {
      const faultData = await getFault(currentFaultId);

      updateFaultInfo(faultData);
      document.getElementById("closeFaultBtn").disabled = false;

      createFaultPanel(faultData, anchor);
    } catch (error) {
      document.getElementById("faultInfo").innerText =
        "Could not load fault from backend.";

      console.error(error);
    }
  };

  const spannerAnchor = mindarThree.addAnchor(3);
  const screwdriverAnchor = mindarThree.addAnchor(4);
  const voltageTesterAnchor = mindarThree.addAnchor(5);

  spannerAnchor.onTargetFound = () => {
    requiredTools[0].scanned = true;
    updateToolCheckUI();
    console.log("Spanner detected");
  };

  screwdriverAnchor.onTargetFound = () => {
    requiredTools[1].scanned = true;
    updateToolCheckUI();
    console.log("Screwdriver detected");
  };

  voltageTesterAnchor.onTargetFound = () => {
    requiredTools[2].scanned = true;
    updateToolCheckUI();
    console.log("Voltage tester detected");
  };

  // tool markers
  const toolMarkerMap = {
    1: 1,
    2: 2,
    3: 3
  };

  Object.entries(toolMarkerMap).forEach(([markerIndex, toolId]) => {
    const toolAnchor = mindarThree.addAnchor(Number(markerIndex));

    toolAnchor.onTargetFound = async () => {
      console.log(`Tool marker ${markerIndex} detected`);

      try {
        const toolData = await updateTool(toolId, "checked_out");

        const matchingTool = requiredTools.find(
          (tool) => tool.id === toolId
        );

        if (matchingTool) {
          matchingTool.scanned = true;
        }

        updateToolCheckUI();

        console.log("Tool updated:", toolData);
      } catch (error) {
        console.error("Could not update tool:", error);
      }
    };
  });

  await mindarThree.start();

  renderer.setAnimationLoop(() => {
    renderer.render(scene, camera);
  });

  // hides loading ui
  document
    .querySelectorAll(".mindar-ui-loading")
    .forEach((element) => {
      element.style.display = "none";
    });

  setTimeout(() => {
    document
      .querySelectorAll(
        ".mindar-ui-loading, .mindar-ui-overlay, .mindar-ui-scanning"
      )
      .forEach((element) => {
        element.style.display = "none";
      });
  }, 5);

  console.log("MindAR started");
  console.log("Camera started");
}

// keeps screen resizing properly
window.addEventListener("resize", () => {
  if (!camera || !renderer) return;

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);
});

// runs when page loads
document.addEventListener("DOMContentLoaded", () => {
  initARScene();
  updateToolCheckUI();

  const closeFaultBtn = document.getElementById("closeFaultBtn");
  const titleEl = document.getElementById("title");
  const locationEl = document.getElementById("location");
  const severityEl = document.getElementById("severity");
  const addBtn = document.getElementById("addBtn");
  const msgEl = document.getElementById("msg");


  // closes fault
  closeFaultBtn.addEventListener("click", async () => {
    if (!currentFaultId) return;

    try {
      const updatedFaultData = await updateFault(
        currentFaultId,
        "closed"
      );

      createFaultPanel(updatedFaultData);
      updateFaultInfo(updatedFaultData);

      closeFaultBtn.disabled = true;
    } catch (error) {
      document.getElementById("faultInfo").innerText =
        "Could not update fault.";

      console.error(error);
    }
  });

  // fake tool scanner button


  // adds a new fault
  addBtn.addEventListener("click", async () => {
    msgEl.textContent = "";

    try {
      const title = titleEl.value.trim();
      const location = locationEl.value.trim();
      const severity = parseInt(severityEl.value);

      const createdFault = await createFault(
        title,
        location,
        severity
      );

      msgEl.textContent = `Created fault ID: ${createdFault.id}`;

      titleEl.value = "";
      locationEl.value = "";
      severityEl.value = "low";

      currentFaultId = createdFault.id;

      createFaultPanel(createdFault);
      updateFaultInfo(createdFault);

      closeFaultBtn.disabled = false;
    } catch (error) {
      msgEl.textContent = "Error: " + error.message;

      console.error(error);
    }
  });

  // manual marker buttons
  const markerButtons = document.querySelectorAll(".markerBtn");

  markerButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      currentFaultId = parseInt(button.dataset.faultId);

      try {
        const faultData = await getFault(currentFaultId);

        createFaultPanel(faultData);
        updateFaultInfo(faultData);

        closeFaultBtn.disabled = false;
      } catch (error) {
        document.getElementById("faultInfo").innerText =
          "Could not load fault from backend.";

        console.error(error);
      }
    });
  });
});