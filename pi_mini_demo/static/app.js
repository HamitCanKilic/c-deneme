const ledState = document.getElementById("ledState");
const toggleButton = document.getElementById("toggleButton");
const temperature = document.getElementById("temperature");
const lastUpdate = document.getElementById("lastUpdate");

function renderLed(on) {
  ledState.textContent = on ? "Açık" : "Kapalı";
  ledState.classList.remove("on", "off");
  ledState.classList.add(on ? "on" : "off");
}

async function fetchStatus() {
  const response = await fetch("/api/status");
  const data = await response.json();
  renderLed(data.led_on);
  temperature.textContent = `${data.temperature} °C`;
  lastUpdate.textContent = data.last_update;
}

toggleButton.addEventListener("click", async () => {
  const response = await fetch("/api/led/toggle", { method: "POST" });
  const data = await response.json();
  renderLed(data.led_on);
});

setInterval(fetchStatus, 3000);
fetchStatus();
