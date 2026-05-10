 // stores currently selected fault
let faultPanel = null;   // stores the 3d box shown in the Tree.js scene
let scene, camera, renderer;      //objects to display the 3d graphics
let current_fault_id = null;
import * as THREE from "three";
import { MindARThree } from "https://cdn.jsdelivr.net/npm/mind-ar@1.2.5/dist/mindar-image-three.prod.js";
const AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJDYXJsb3MiLCJleHAiOjE3Nzg0NTA3NzR9.0oIrjkKia0nOjp8FqUW4K4Y4fJd-LU27W7fUfAeN6wg"
const required_tools = [
  { id: 1, name: "Spanner", scanned: false },
  { id: 2, name: "Screwdriver", scanned: false },
  { id: 3, name: "Voltage tester", scanned: false }
];




async function getFault(fault_id) {
  const response = await fetch(`/api/faults/${fault_id}`, {
    headers: {
      Authorization: `Bearer ${AUTH_TOKEN}`
    }
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(JSON.stringify(data));
  }

  return data;
}
// function getFault asks the back end for fault_id and gets the data relating to the fault and returns an error message if there is no fault

async function getTools() {
  const response = await fetch("/api/tools", {
    headers: {
      Authorization: `Bearer ${AUTH_TOKEN}`
    }
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(JSON.stringify(data));
  }

  return data;
}

async function getTool(tool_id) {
  const response = await fetch(`/api/tools/${tool_id}`, {
    headers: {
      Authorization: `Bearer ${AUTH_TOKEN}`
    }
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(JSON.stringify(data));
  }

  return data;
}

async function updateTool(tool_id, status) {
  const response = await fetch(`/api/tools/${tool_id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${AUTH_TOKEN}`
    },
    body: JSON.stringify({
      status: status
    })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(JSON.stringify(data));
  }

  return data;
}

async function updateFault(fault_id, status) {
  const response = await fetch(`/api/faults/${fault_id}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${AUTH_TOKEN}`
    },
    body: JSON.stringify({
      status: status
    })
  });

  if (!response.ok) {
    throw new Error("Could not update fault");
  }

  return response.json();
}
// funtion updateFault will update the fault status in the backend from the front end, so user can mark fault as fixed changing the status to closed



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
// this function sets up the AR 3D scence and alters the view for the user to see the scene better with camera angle, lighting and a grid to map out the space



function createFaultPanel(fault_data, anchor) {

  if (faultPanel && faultPanel.parent) {
    faultPanel.parent.remove(faultPanel);
  }

  const geometry = new THREE.BoxGeometry(0.6, 0.35, 0.05);
    faultPanel.position.set(0, 0, 0.05);
    let colour = 0x00aa00;

  if (fault_data.severity === 3) {
    colour = 0xff0000;
  } else if (fault_data.severity === 2) {
    colour = 0xffaa00;
  }

const material = new THREE.MeshBasicMaterial({
  color: 0xff0000,
  transparent: true,
  opacity: 0.3,
  depthWrite: false,
  side: THREE.DoubleSide
});

  faultPanel = new THREE.Mesh(geometry, material);
  faultPanel.position.set(0, 0.5, 0);

  anchor.group.add(faultPanel);
}
// function createFaultPannel creates the pannel to see the fault "pretty self explanatory lol"... if there is already one open it will close it before opening the new one



function updateFaultInfo(fault_data) {
  document.getElementById("faultInfo").innerHTML = `
    <strong>${fault_data.title}</strong><br>
    Location: ${fault_data.location}<br>
    Severity: ${fault_data.severity}<br>
    Status: ${fault_data.status}
  `;
}
// shows the user the correct fault info, basically updating the table that they are shwon



async function createFault(title, location, severity) {
  
  const response = await fetch("/api/faults", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${AUTH_TOKEN}`
    },
    body: JSON.stringify({
      title: title,
      location: location,
      severity: severity
    })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(JSON.stringify(data));
  }

  return data;
}
// creates a new fault for an item by first taking user input sending it to FastAPI, where the fault is created






function animate() {
  requestAnimationFrame(animate);

  if (faultPanel) {
    faultPanel.rotation.y += 0.01;
  }

  renderer.render(scene, camera);
}


let next_tool_index = 0;

function updateToolCheckUI() {
  const scanned_count = required_tools.filter(tool => tool.scanned).length;

  document.getElementById("toolInfo").textContent =
    `Tools scanned: ${scanned_count} / ${required_tools.length}`;

  document.getElementById("toolList").innerHTML = required_tools
    .map(tool =>
      `<li>${tool.name}: ${tool.scanned ? "present" : "missing"}</li>`
    )
    .join("");
}
// ============================================================================================================
function createSimulatedMarkers() {
  const marker_positions = {
    1: { x: -2, y: -1.2, z: 0 },
    2: { x: 0, y: -1.2, z: 0 },
    3: { x: 2, y: -1.2, z: 0 }
  };

  Object.entries(marker_positions).forEach(([id, position]) => {
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
// -------------------------------------------------------------------------
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
  const material = new THREE.SpriteMaterial({ map: texture });
  const sprite = new THREE.Sprite(material);

  sprite.scale.set(1.5, 0.75, 1);

  return sprite;
}
// =========================================================================================================

async function initARScene() {
  console.log("initARScene started");

  const mindarThree = new MindARThree({
    container: document.body,
    imageTargetSrc: "/static/targets.mind"
  });

  renderer = mindarThree.renderer;
  scene = mindarThree.scene;
  camera = mindarThree.camera;

  const anchor = mindarThree.addAnchor(0);

anchor.onTargetFound = async () => {
  console.log("Marker detected");

  current_fault_id = 1;

  try {
    const fault_data = await getFault(current_fault_id);

    updateFaultInfo(fault_data);
    closeFaultBtn.disabled = false;

    createFaultPanel(fault_data, anchor);

  } catch (error) {
    document.getElementById("faultInfo").innerText =
      "Could not load fault from backend.";

    console.error(error);
  }
};

await mindarThree.start();


const toolMarkerMap = {
  1: 1, // marker target 1 = tool ID 1 Spanner
  2: 2, // marker target 2 = tool ID 2 Screwdriver
  3: 3  // marker target 3 = tool ID 3 Voltage tester
};

Object.entries(toolMarkerMap).forEach(([marker_index, tool_id]) => {
  const toolAnchor = mindarThree.addAnchor(Number(marker_index));

  toolAnchor.onTargetFound = async () => {
    console.log(`Tool marker ${marker_index} detected`);

    try {
      const tool_data = await updateTool(tool_id, "checked_out");

      const matching_tool = required_tools.find(tool => tool.id === tool_id);

      if (matching_tool) {
        matching_tool.scanned = true;
      }

      updateToolCheckUI();

      console.log("Tool updated:", tool_data);
    } catch (error) {
      console.error("Could not update tool:", error);
    }
  };
});




renderer.setAnimationLoop(() => {
  renderer.render(scene, camera);
});
document.querySelectorAll(".mindar-ui-loading").forEach((element) => {
  element.style.display = "none";
});

console.log("MindAR started");

setTimeout(() => {
  document.querySelectorAll(
    ".mindar-ui-loading, .mindar-ui-overlay, .mindar-ui-scanning"
  ).forEach((element) => {
    element.style.display = "none";
  });
}, 5);

  console.log("Camera started");
}




window.addEventListener("resize", () => {
  if (!camera || !renderer) return;

  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);
});




document.addEventListener("DOMContentLoaded", () => {
  initARScene();
  updateToolCheckUI();
 // createSimulatedMarkers();


  const closeFaultBtn = document.getElementById("closeFaultBtn");


  const titleEl = document.getElementById("title");
  const locationEl = document.getElementById("location");
  const severityEl = document.getElementById("severity");
  const addBtn = document.getElementById("addBtn");
  const msgEl = document.getElementById("msg");



// complete fault button
  closeFaultBtn.addEventListener("click", async () => {
    if (!current_fault_id) return;

    try {
      const updated_fault_data = await updateFault(current_fault_id, "closed");

      createFaultPanel(updated_fault_data);
      updateFaultInfo(updated_fault_data);

      closeFaultBtn.disabled = true;
    } catch (error) {
      document.getElementById("faultInfo").innerText =
        "Could not update fault.";

      console.error(error);
    }

  const scanToolBtn = document.getElementById("scanToolBtn");

  scanToolBtn.addEventListener("click", () => {
   if (next_tool_index >= required_tools.length) {
     return;
    }

   required_tools[next_tool_index].scanned = true;
   next_tool_index += 1;

   updateToolCheckUI();
});



  });

  // create a new fault
  addBtn.addEventListener("click", async () => {
    msgEl.textContent = "";

    try {
      const title = titleEl.value.trim();
      const location = locationEl.value.trim();
      const severity = parseInt(severityEl.value);

      const created_fault = await createFault(title, location, severity);

      msgEl.textContent = `Created fault ID: ${created_fault.id}`;

      titleEl.value = "";
      locationEl.value = "";
      severityEl.value = "low";

      current_fault_id = created_fault.id;

      createFaultPanel(created_fault);
      updateFaultInfo(created_fault);

      closeFaultBtn.disabled = false;
    } catch (error) {
      msgEl.textContent = "Error: " + error.message;
      console.error(error);
    }
  });
  const markerButtons = document.querySelectorAll(".markerBtn")
  markerButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      current_fault_id = parseInt(button.dataset.faultId);
    try {
      const fault_data = await getFault(current_fault_id);

      createFaultPanel(fault_data);
      updateFaultInfo(fault_data);

      closeFaultBtn.disabled = false;
    } catch (error) {
      document.getElementById("faultInfo").innerText =
        "Could not load fault from backend.";

      console.error(error);
    }
  });
}); 
    })
