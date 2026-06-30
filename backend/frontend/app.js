const state = {
  token: localStorage.getItem("careerpilot_token"),
  user: JSON.parse(localStorage.getItem("careerpilot_user") || "null"),
  roles: [],
  selectedRole: "",
  latestResumeId: null,
};

const authView = document.querySelector("#authView");
const appView = document.querySelector("#appView");
const authStatus = document.querySelector("#authStatus");
const loginForm = document.querySelector("#loginForm");
const registerForm = document.querySelector("#registerForm");
const showLogin = document.querySelector("#showLogin");
const showRegister = document.querySelector("#showRegister");
const googleButton = document.querySelector("#googleButton");
const userEmail = document.querySelector("#userEmail");
const logoutButton = document.querySelector("#logoutButton");
const resumeFile = document.querySelector("#resumeFile");
const fileName = document.querySelector("#fileName");
const uploadForm = document.querySelector("#uploadForm");
const uploadButton = document.querySelector("#uploadButton");
const uploadStatus = document.querySelector("#uploadStatus");
const analyzeForm = document.querySelector("#analyzeForm");
const analyzeButton = document.querySelector("#analyzeButton");
const analyzeStatus = document.querySelector("#analyzeStatus");
const roleSearch = document.querySelector("#roleSearch");
const roleOptions = document.querySelector("#roleOptions");

init();

async function init() {
  initNavigation();
  initAuthTabs();
  initForms();
  initThreeScene();
  await initGoogleLogin();

  if (state.token && state.user) {
    showApp();
    await loadRoles();
  } else {
    showAuth();
  }
}

function initAuthTabs() {
  showLogin.addEventListener("click", () => {
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
    showLogin.classList.add("active");
    showRegister.classList.remove("active");
    setStatus(authStatus, "", "");
  });

  showRegister.addEventListener("click", () => {
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    showRegister.classList.add("active");
    showLogin.classList.remove("active");
    setStatus(authStatus, "", "");
  });
}

function initNavigation() {
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", () => {
      document.querySelectorAll(".nav-link").forEach((item) => item.classList.remove("active"));
      link.classList.add("active");
    });
  });

  logoutButton.addEventListener("click", () => {
    localStorage.removeItem("careerpilot_token");
    localStorage.removeItem("careerpilot_user");
    state.token = null;
    state.user = null;
    showAuth();
  });
}

function initForms() {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await authRequest("/api/auth/login", {
      email: document.querySelector("#loginEmail").value,
      password: document.querySelector("#loginPassword").value,
    });
  });

  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    await authRequest("/api/auth/register", {
      full_name: document.querySelector("#registerName").value,
      email: document.querySelector("#registerEmail").value,
      password: document.querySelector("#registerPassword").value,
    });
  });

  resumeFile.addEventListener("change", () => {
    const file = resumeFile.files[0];
    fileName.textContent = file ? file.name : "Choose resume file";
  });

  uploadForm.addEventListener("submit", uploadResume);
  analyzeForm.addEventListener("submit", analyzeResume);
  roleSearch.addEventListener("input", () => renderRoleOptions(roleSearch.value));
  roleSearch.addEventListener("focus", () => renderRoleOptions(roleSearch.value));
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".combo")) {
      roleOptions.classList.add("hidden");
    }
  });
}

async function authRequest(url, payload) {
  setStatus(authStatus, "Authenticating...", "");
  try {
    const data = await api(url, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    saveSession(data);
    showApp();
    await loadRoles();
    setStatus(authStatus, "", "");
  } catch (error) {
    setStatus(authStatus, error.message, "error");
  }
}

async function initGoogleLogin() {
  try {
    const config = await api("/api/auth/config");
    if (!config.google_client_id) {
      googleButton.textContent = "Add GOOGLE_CLIENT_ID in .env to enable Google login.";
      googleButton.classList.add("status");
      return;
    }

    const timer = setInterval(() => {
      if (!window.google?.accounts?.id) return;
      clearInterval(timer);
      window.google.accounts.id.initialize({
        client_id: config.google_client_id,
        callback: async (response) => {
          try {
            const data = await api("/api/auth/google", {
              method: "POST",
              body: JSON.stringify({ id_token: response.credential }),
            });
            saveSession(data);
            showApp();
            await loadRoles();
          } catch (error) {
            setStatus(authStatus, error.message, "error");
          }
        },
      });
      window.google.accounts.id.renderButton(googleButton, {
        theme: "filled_blue",
        size: "large",
        width: 320,
      });
    }, 250);
  } catch {
    googleButton.textContent = "Google login config could not be loaded.";
    googleButton.classList.add("status");
  }
}

async function uploadResume(event) {
  event.preventDefault();
  const file = resumeFile.files[0];
  if (!file) {
    setStatus(uploadStatus, "Please choose a resume file.", "error");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  setBusy(uploadButton, true, "Uploading...");
  setStatus(uploadStatus, "Extracting resume text...", "");

  try {
    const data = await api("/api/upload-resume", {
      method: "POST",
      body: formData,
      skipJsonHeader: true,
    });
    state.latestResumeId = data.resume_id;
    setStatus(uploadStatus, `${data.filename} uploaded successfully.`, "ok");
  } catch (error) {
    setStatus(uploadStatus, error.message, "error");
  } finally {
    setBusy(uploadButton, false, "Upload Resume");
  }
}

async function analyzeResume(event) {
  event.preventDefault();
  const role = state.selectedRole || roleSearch.value.trim();
  if (!role) {
    setStatus(analyzeStatus, "Please select a job role.", "error");
    return;
  }

  setBusy(analyzeButton, true, "Analyzing...");
  setStatus(analyzeStatus, "Building skill gap and ATS insight...", "");

  try {
    const data = await api("/api/analyze", {
      method: "POST",
      body: JSON.stringify({
        role,
        resume_id: state.latestResumeId,
      }),
    });
    renderResults(data);
    setStatus(analyzeStatus, "Analysis completed.", "ok");
    document.querySelector("#insights").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    setStatus(analyzeStatus, error.message, "error");
  } finally {
    setBusy(analyzeButton, false, "Analyze Resume");
  }
}

async function loadRoles() {
  try {
    state.roles = await api("/api/roles");
    document.querySelector("#roleCount").textContent = `${state.roles.length} roles available from database`;
    renderRolePills();
    renderRoleOptions("");
  } catch (error) {
    document.querySelector("#roleCount").textContent = error.message;
  }
}

function renderRolePills() {
  const container = document.querySelector("#rolePills");
  container.innerHTML = "";
  state.roles.slice(0, 12).forEach((role) => {
    const pill = document.createElement("button");
    pill.className = "pill";
    pill.type = "button";
    pill.textContent = role;
    pill.addEventListener("click", () => selectRole(role));
    container.appendChild(pill);
  });
}

function renderRoleOptions(query) {
  roleOptions.innerHTML = "";
  const normalized = query.trim().toLowerCase();
  const filtered = state.roles
    .filter((role) => role.toLowerCase().includes(normalized))
    .slice(0, 30);

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "combo-option";
    empty.textContent = "No database role found";
    roleOptions.appendChild(empty);
  }

  filtered.forEach((role) => {
    const option = document.createElement("button");
    option.className = "combo-option";
    option.type = "button";
    option.textContent = role;
    option.addEventListener("click", () => selectRole(role));
    roleOptions.appendChild(option);
  });

  roleOptions.classList.remove("hidden");
}

function selectRole(role) {
  state.selectedRole = role;
  roleSearch.value = role;
  roleOptions.classList.add("hidden");
}

function renderResults(data) {
  document.querySelector("#insights").classList.remove("hidden");
  setScore("#matchScore", "#miniMatch", "#matchRing", data.match_score);
  setScore("#atsScore", "#miniAts", "#atsRing", data.ats_score);
  renderChips("#currentSkills", data.current_skills);
  renderChips("#missingSkills", data.missing_skills);
  renderList("#projects", data.recommended_projects);
  renderList("#certifications", data.certifications);
  renderList("#resumeTips", data.resume_improvement_suggestions);
  renderList("#atsTips", data.ats_improvement_suggestions);
  document.querySelector("#careerAdvice").textContent = data.career_advice || "No career guidance returned.";
}

function setScore(scoreSelector, miniSelector, ringSelector, value = 0) {
  const score = Math.max(0, Math.min(100, Number(value) || 0));
  document.querySelector(scoreSelector).textContent = score;
  document.querySelector(miniSelector).textContent = `${score}%`;
  document.querySelector(ringSelector).parentElement.style.background =
    `conic-gradient(var(--cyan) ${score * 3.6}deg, rgba(255,255,255,0.12) 0deg)`;
}

function renderChips(selector, items = []) {
  const container = document.querySelector(selector);
  container.innerHTML = "";
  if (!items.length) {
    container.appendChild(emptyText("No items found."));
    return;
  }
  items.forEach((item) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = item;
    container.appendChild(chip);
  });
}

function renderList(selector, items = []) {
  const list = document.querySelector(selector);
  list.innerHTML = "";
  if (!items.length) {
    const item = document.createElement("li");
    item.textContent = "No items returned.";
    list.appendChild(item);
    return;
  }
  items.forEach((value) => {
    const item = document.createElement("li");
    item.textContent = value;
    list.appendChild(item);
  });
}

function emptyText(text) {
  const span = document.createElement("span");
  span.className = "status";
  span.textContent = text;
  return span;
}

async function api(url, options = {}) {
  const headers = options.headers ? { ...options.headers } : {};
  if (!options.skipJsonHeader) {
    headers["Content-Type"] = "application/json";
  }
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed.");
  }
  return data;
}

function saveSession(data) {
  state.token = data.access_token;
  state.user = data.user;
  localStorage.setItem("careerpilot_token", state.token);
  localStorage.setItem("careerpilot_user", JSON.stringify(state.user));
}

function showAuth() {
  authView.classList.remove("hidden");
  appView.classList.add("hidden");
}

function showApp() {
  authView.classList.add("hidden");
  appView.classList.remove("hidden");
  userEmail.textContent = state.user?.email || "Signed in";
}

function setBusy(button, busy, text) {
  button.disabled = busy;
  button.textContent = text;
}

function setStatus(element, message, type) {
  element.className = `status ${type}`.trim();
  element.textContent = message;
}

async function initThreeScene() {
  const canvas = document.querySelector("#hero3d");
  try {
    const THREE = await import("https://unpkg.com/three@0.160.0/build/three.module.js");
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, canvas.clientWidth / canvas.clientHeight, 0.1, 100);
    camera.position.set(0, 0, 7);

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const group = new THREE.Group();
    scene.add(group);

    const nodeGeometry = new THREE.IcosahedronGeometry(0.12, 1);
    const nodeMaterial = new THREE.MeshStandardMaterial({
      color: 0x20d7c7,
      emissive: 0x0a5bff,
      emissiveIntensity: 0.25,
      roughness: 0.35,
    });

    for (let i = 0; i < 85; i += 1) {
      const node = new THREE.Mesh(nodeGeometry, nodeMaterial);
      const radius = 1.6 + Math.random() * 2.6;
      const angle = Math.random() * Math.PI * 2;
      node.position.set(
        Math.cos(angle) * radius,
        (Math.random() - 0.5) * 4.3,
        Math.sin(angle) * radius
      );
      group.add(node);
    }

    const torus = new THREE.Mesh(
      new THREE.TorusKnotGeometry(1.25, 0.14, 160, 18),
      new THREE.MeshStandardMaterial({
        color: 0x2f7cff,
        metalness: 0.35,
        roughness: 0.22,
        emissive: 0x123b91,
        emissiveIntensity: 0.35,
      })
    );
    group.add(torus);

    scene.add(new THREE.AmbientLight(0x8bb7ff, 1.2));
    const light = new THREE.PointLight(0x20d7c7, 2.3, 20);
    light.position.set(4, 4, 5);
    scene.add(light);

    const resize = () => {
      const width = canvas.clientWidth || canvas.parentElement.clientWidth;
      const height = canvas.clientHeight || canvas.parentElement.clientHeight;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    window.addEventListener("resize", resize);
    resize();

    const animate = () => {
      group.rotation.y += 0.004;
      group.rotation.x = Math.sin(performance.now() * 0.0004) * 0.12;
      torus.rotation.z += 0.006;
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    animate();
  } catch {
    canvas.style.background = "radial-gradient(circle, rgba(32,215,199,.28), transparent 55%)";
  }
}
