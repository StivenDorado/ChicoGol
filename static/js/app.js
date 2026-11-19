const menuButton = document.querySelector('.menu-toggle');
const mobileMenu = document.querySelector('#mobile-menu');
if (menuButton && mobileMenu) {
  menuButton.addEventListener('click', () => {
    const open = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!open));
    mobileMenu.hidden = open;
  });
}

const citySelect = document.querySelector('[data-city-select]') || document.querySelector('#id_ciudad');
const barrioTemplate = document.querySelector('#popayan-barrio-template');

if (citySelect && (document.querySelector('[data-barrio-input], [data-barrio-select]') || document.querySelector('#id_barrio')) && barrioTemplate) {
  const syncBarrioControl = () => {
    const barrioControl = document.querySelector('[data-barrio-input], [data-barrio-select]') || document.querySelector('#id_barrio');
    if (!barrioControl) return;
    const isPopayan = citySelect.value === 'Popayán';
    const currentValue = barrioControl.value;
    if (isPopayan && barrioControl.tagName !== 'SELECT') {
      const select = document.createElement('select');
      select.name = barrioControl.name;
      select.id = barrioControl.id;
      select.className = barrioControl.className;
      select.setAttribute('data-barrio-select', 'true');
      const barrioTemplateSelect = barrioTemplate.content?.querySelector('select');
      select.innerHTML = barrioTemplateSelect ? barrioTemplateSelect.innerHTML : barrioTemplate.innerHTML;
      select.value = currentValue;
      select.addEventListener('change', () => {
        if (select.value !== 'otro') return;
        const input = document.createElement('input');
        input.type = 'text';
        input.name = select.name;
        input.id = select.id;
        input.className = select.className;
        input.placeholder = 'Escribe tu barrio o zona';
        input.setAttribute('data-barrio-input', 'true');
        select.replaceWith(input);
        input.focus();
      });
      barrioControl.replaceWith(select);
    } else if (!isPopayan && barrioControl.tagName === 'SELECT') {
      const input = document.createElement('input');
      input.type = 'text';
      input.name = barrioControl.name;
      input.id = barrioControl.id;
      input.className = barrioControl.className;
      input.placeholder = 'Escribe tu barrio o zona';
      input.setAttribute('data-barrio-input', 'true');
      input.value = currentValue;
      barrioControl.replaceWith(input);
    }
  };
  citySelect.setAttribute('data-city-select', 'true');
  citySelect.addEventListener('change', syncBarrioControl);
  syncBarrioControl();
}

const avatarInput = document.querySelector('#id_avatar');
const avatarFrame = document.querySelector('[data-avatar-preview]');
const avatarStatus = document.querySelector('#avatar-preview-status');
if (avatarInput && avatarFrame) {
  avatarInput.addEventListener('change', () => {
    const [file] = avatarInput.files || [];
    if (!file) return;
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 3 * 1024 * 1024) {
      if (avatarStatus) avatarStatus.textContent = 'Elige JPG, PNG o WebP de máximo 3 MB.';
      avatarInput.value = '';
      return;
    }
    const image = document.createElement('img');
    image.src = URL.createObjectURL(file);
    image.alt = 'Vista previa de la nueva fotografía de perfil';
    image.onload = () => URL.revokeObjectURL(image.src);
    avatarFrame.replaceChildren(image);
    if (avatarStatus) avatarStatus.textContent = 'Vista previa lista. Guarda el perfil para confirmar el cambio.';
  });
}

(() => {
  if (!window.L) return;
  const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
  const tileOptions = { attribution: '&copy; OpenStreetMap contributors', maxZoom: 19 };
  const centers = { Popayán: [2.4448, -76.6147], Bogotá: [4.711, -74.0721], Cali: [3.4516, -76.532], Medellín: [6.2442, -75.5812] };
  const addTiles = (map) => { const layer = L.tileLayer(tileUrl, tileOptions).addTo(map); layer.on('tileerror', () => { const node = map.getContainer(); if (!node.querySelector('.map-error-fallback')) { const message = document.createElement('div'); message.className = 'map-error-fallback'; message.textContent = 'El mapa no pudo cargar sus mosaicos. Puedes continuar con las coordenadas seleccionadas.'; node.appendChild(message); } }); };
  const mapNode = document.querySelector('#cancha-create-map');
  if (!mapNode) return;
  const city = document.querySelector('#id_ciudad'); const latInput = document.querySelector('#id_latitud'); const lonInput = document.querySelector('#id_longitud'); const address = document.querySelector('#id_direccion'); const status = document.querySelector('#map-location-status');
  const initial = [parseFloat(latInput?.value) || 2.4448, parseFloat(lonInput?.value) || -76.6147]; const map = L.map(mapNode).setView(initial, 14); addTiles(map); const marker = L.marker(initial, { draggable: true }).addTo(map);
  const setPoint = (point) => { const lat = Number(point.lat).toFixed(6); const lon = Number(point.lng).toFixed(6); if (latInput) latInput.value = lat; if (lonInput) lonInput.value = lon; if (status) status.textContent = `Ubicación seleccionada: ${lat}, ${lon}`; };
  const reverse = async (point) => { try { const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${point.lat}&lon=${point.lng}&accept-language=es`); const data = await response.json(); if (address && data.display_name && !address.value.trim()) address.value = data.display_name; } catch (_) {} };
  const move = (point) => { marker.setLatLng(point); setPoint(point); reverse(point); }; map.on('click', (event) => move(event.latlng)); marker.on('dragend', () => move(marker.getLatLng())); setPoint({ lat: initial[0], lng: initial[1] });
  city?.addEventListener('change', () => { const next = centers[city.value]; if (next) { map.setView(next, 14); move({ lat: next[0], lng: next[1] }); } });
  const photo = document.querySelector('[data-court-photo]'); const preview = document.querySelector('#court-photo-preview'); const previewImage = preview?.querySelector('img'); photo?.addEventListener('change', () => { const file = photo.files?.[0]; if (!file) return; if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 3 * 1024 * 1024) { photo.value = ''; if (status) status.textContent = 'La fotografía debe ser JPG, PNG o WebP y pesar máximo 3 MB.'; return; } if (preview && previewImage) { preview.hidden = false; previewImage.src = URL.createObjectURL(file); } });
})();
