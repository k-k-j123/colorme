// ColorMe AI - Client-side application logic (Single-Image Cataloging & Zero-Image Styling Generation)

// State
let wardrobe = [];
let presets = {};
let currentSettings = {
  provider: 'gemini',
  base_url: 'https://generativelanguage.googleapis.com/v1beta/openai/',
  model: 'gemini-2.0-flash',
  api_key: ''
};
let selectedOccasion = 'Smart Casual';
let selectedSeason = 'Mild / Spring-Fall';

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const wardrobeGrid = document.getElementById('wardrobe-grid');
const wardrobeEmptyState = document.getElementById('wardrobe-empty-state');
const wardrobeCountPill = document.getElementById('wardrobe-count-pill');
const btnSelectAll = document.getElementById('btn-select-all');
const btnClearWardrobe = document.getElementById('btn-clear-wardrobe');
const btnLoadSample = document.getElementById('btn-load-sample');
const btnLoadSampleEmpty = document.getElementById('btn-load-sample-empty');
const btnGenerateStyle = document.getElementById('btn-generate-style');
const loadingState = document.getElementById('loading-state');
const resultsSection = document.getElementById('results-section');
const demoNotice = document.getElementById('demo-notice');
const uploadProgressBanner = document.getElementById('upload-progress-banner');
const uploadProgressText = document.getElementById('upload-progress-text');

// Settings Modal Elements
const settingsModal = document.getElementById('settings-modal');
const btnOpenSettings = document.getElementById('btn-open-settings');
const btnCloseSettings = document.getElementById('btn-close-settings');
const btnCancelSettings = document.getElementById('btn-cancel-settings');
const btnSaveSettings = document.getElementById('btn-save-settings');
const btnTestConnection = document.getElementById('btn-test-connection');
const testConnectionResult = document.getElementById('test-connection-result');
const settingProviderPreset = document.getElementById('setting-provider-preset');
const settingBaseUrl = document.getElementById('setting-base-url');
const settingModel = document.getElementById('setting-model');
const settingApiKey = document.getElementById('setting-api-key');
const toggleKeyVisibility = document.getElementById('toggle-key-visibility');
const presetDescription = document.getElementById('preset-description');
const settingKeyDoc = document.getElementById('setting-key-doc');
const recommendedModelsContainer = document.getElementById('recommended-models-container');
const currentProviderBadge = document.getElementById('current-provider-badge');

// Edit Item Modal Elements
const editItemModal = document.getElementById('edit-item-modal');
const editItemId = document.getElementById('edit-item-id');
const editItemImgPreview = document.getElementById('edit-item-img-preview');
const editItemName = document.getElementById('edit-item-name');
const editItemCategory = document.getElementById('edit-item-category');
const editItemSubCategory = document.getElementById('edit-item-sub-category');
const editItemColorPicker = document.getElementById('edit-item-color-picker');
const editItemColorHex = document.getElementById('edit-item-color-hex');
const editItemColorPrimary = document.getElementById('edit-item-color-primary');
const editItemColorSecondary = document.getElementById('edit-item-color-secondary');
const editItemPattern = document.getElementById('edit-item-pattern');
const editItemMaterial = document.getElementById('edit-item-material');
const editItemFit = document.getElementById('edit-item-fit');
const editItemFormality = document.getElementById('edit-item-formality');
const editItemVibes = document.getElementById('edit-item-vibes');
const editItemFeatures = document.getElementById('edit-item-features');
const editItemDescription = document.getElementById('edit-item-description');
const btnCancelEditItem = document.getElementById('btn-cancel-edit-item');
const btnCloseEditItem = document.getElementById('btn-close-edit-item');
const btnSaveEditItem = document.getElementById('btn-save-edit-item');
const btnReanalyzeItem = document.getElementById('btn-reanalyze-item');
const quickColorPresets = document.getElementById('quick-color-presets');

const COLOR_PRESETS = [
  { name: 'Crisp White', hex: '#FFFFFF' },
  { name: 'Cream / Ecru', hex: '#F5F5DC' },
  { name: 'Deep Navy', hex: '#1E293B' },
  { name: 'Muted Olive', hex: '#4D5D43' },
  { name: 'Warm Camel', hex: '#C89666' },
  { name: 'Tan / Khaki', hex: '#D2B48C' },
  { name: 'Heather Grey', hex: '#94A3B8' },
  { name: 'Washed Charcoal', hex: '#27272A' },
  { name: 'True Black', hex: '#18181B' },
  { name: 'Forest Green', hex: '#1E3A2F' },
  { name: 'Chocolate Brown', hex: '#5C4033' },
  { name: 'Burgundy', hex: '#581C28' },
  { name: 'Sky Blue', hex: '#38BDF8' }
];

// Init
document.addEventListener('DOMContentLoaded', async () => {
  loadStoredSettings();
  await fetchPresets();
  await loadWardrobeFromDB();
  setupEventListeners();
  renderWardrobe();
  lucide.createIcons();
});

// Load settings from localStorage
function loadStoredSettings() {
  const saved = localStorage.getItem('colorme_settings');
  if (saved) {
    try {
      const parsed = JSON.parse(saved);
      currentSettings = { ...currentSettings, ...parsed };
    } catch (e) {
      console.error('Failed to parse saved settings', e);
    }
  }
  updateProviderBadge();
}

function updateProviderBadge() {
  const provName = presets[currentSettings.provider]?.name || currentSettings.provider;
  currentProviderBadge.textContent = `${provName} (${currentSettings.model})`;
}

// Fetch available provider presets
async function fetchPresets() {
  try {
    const res = await fetch('/api/presets');
    if (res.ok) {
      const data = await res.json();
      presets = data.presets;
      
      // If no stored settings, use server defaults
      if (!localStorage.getItem('colorme_settings')) {
        currentSettings.base_url = data.defaults.base_url;
        currentSettings.model = data.defaults.model;
      }
      updateProviderBadge();
    }
  } catch (err) {
    console.warn('Could not fetch presets from server:', err);
  }
}

// Load wardrobe items from SQLite DB
async function loadWardrobeFromDB() {
  try {
    const res = await fetch('/api/wardrobe');
    if (res.ok) {
      const data = await res.json();
      wardrobe = (data.items || []).map(item => ({
        ...item,
        selected: true
      }));
    }
  } catch (err) {
    console.warn('Failed to load wardrobe from DB:', err);
  }
}

// Setup Event Listeners
function setupEventListeners() {
  // Occasion Pills
  document.getElementById('occasion-pills').addEventListener('click', (e) => {
    const btn = e.target.closest('.pill');
    if (!btn) return;
    document.querySelectorAll('#occasion-pills .pill').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    selectedOccasion = btn.getAttribute('data-val');
  });

  // Season Pills
  document.getElementById('season-pills').addEventListener('click', (e) => {
    const btn = e.target.closest('.pill');
    if (!btn) return;
    document.querySelectorAll('#season-pills .pill').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    selectedSeason = btn.getAttribute('data-val');
  });

  // File Upload Drag & Drop
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.add('border-zinc-900', 'bg-zinc-100/50');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-zinc-900', 'bg-zinc-100/50');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length) handleFiles(files);
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) handleFiles(e.target.files);
  });

  // Select all / Clear
  btnSelectAll.addEventListener('click', () => {
    const allSelected = wardrobe.every(item => item.selected);
    wardrobe.forEach(item => item.selected = !allSelected);
    renderWardrobe();
  });

  btnClearWardrobe.addEventListener('click', async () => {
    if (confirm('Clear all garments from your database?')) {
      try {
        await fetch('/api/wardrobe', { method: 'DELETE' });
        wardrobe = [];
        renderWardrobe();
      } catch (err) {
        alert('Failed to clear wardrobe: ' + err.message);
      }
    }
  });

  // Sample Wardrobe buttons
  btnLoadSample.addEventListener('click', loadSampleWardrobe);
  btnLoadSampleEmpty.addEventListener('click', loadSampleWardrobe);

  // Generate Styling Consultation
  btnGenerateStyle.addEventListener('click', generateStyleAdvice);

  // Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.getAttribute('data-tab');
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`content-${tab}`).classList.add('active');
    });
  });

  // Settings Modal Controls
  btnOpenSettings.addEventListener('click', openSettingsModal);
  btnCloseSettings.addEventListener('click', closeSettingsModal);
  btnCancelSettings.addEventListener('click', closeSettingsModal);
  btnSaveSettings.addEventListener('click', saveSettingsModal);
  btnTestConnection.addEventListener('click', testConnection);
  settingProviderPreset.addEventListener('change', onPresetChange);

  toggleKeyVisibility.addEventListener('click', () => {
    const isPassword = settingApiKey.type === 'password';
    settingApiKey.type = isPassword ? 'text' : 'password';
    toggleKeyVisibility.innerHTML = isPassword 
      ? '<i data-lucide="eye-off" class="w-4 h-4"></i>' 
      : '<i data-lucide="eye" class="w-4 h-4"></i>';
    lucide.createIcons();
  });

  // Setup Quick Color Presets in Edit Modal
  if (quickColorPresets) {
    quickColorPresets.innerHTML = COLOR_PRESETS.map(c => `
      <button 
        type="button" 
        onclick="applyColorPreset('${c.name}', '${c.hex}')" 
        class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] font-medium bg-white hover:bg-zinc-100 border border-zinc-200 transition-colors shadow-2xs"
      >
        <span class="w-3 h-3 rounded-full border border-black/15 flex-shrink-0" style="background-color: ${c.hex}"></span>
        <span class="text-zinc-700">${c.name}</span>
      </button>
    `).join('');
  }

  // Color Picker <-> Hex Input Sync
  editItemColorPicker.addEventListener('input', (e) => {
    editItemColorHex.value = e.target.value.toUpperCase();
  });

  editItemColorHex.addEventListener('input', (e) => {
    let val = e.target.value.trim();
    if (!val.startsWith('#')) val = '#' + val;
    if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
      editItemColorPicker.value = val;
    }
  });

  // Edit Item Modal Controls
  btnCancelEditItem.addEventListener('click', () => editItemModal.classList.add('hidden'));
  if (btnCloseEditItem) btnCloseEditItem.addEventListener('click', () => editItemModal.classList.add('hidden'));

  btnSaveEditItem.addEventListener('click', async () => {
    const id = editItemId.value;
    const vibesList = editItemVibes.value.split(',').map(s => s.trim()).filter(Boolean);
    const featuresList = editItemFeatures.value.split(',').map(s => s.trim()).filter(Boolean);

    const payload = {
      name: editItemName.value.trim(),
      category: editItemCategory.value,
      sub_category: editItemSubCategory.value.trim(),
      color_primary: editItemColorPrimary.value.trim(),
      color_secondary: editItemColorSecondary.value.trim(),
      color_hex: editItemColorHex.value.trim() || editItemColorPicker.value,
      pattern: editItemPattern.value,
      material_texture: editItemMaterial.value.trim(),
      fit_silhouette: editItemFit.value.trim(),
      formality_level: editItemFormality.value,
      style_vibes: vibesList,
      key_features: featuresList,
      full_description: editItemDescription.value.trim()
    };

    btnSaveEditItem.disabled = true;
    btnSaveEditItem.innerHTML = '<div class="w-3.5 h-3.5 rounded-full border-2 border-white/30 border-t-white animate-spin"></div> Saving...';

    try {
      const res = await fetch(`/api/wardrobe/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const updated = await res.json();
        const idx = wardrobe.findIndex(w => w.id === id);
        if (idx !== -1) {
          wardrobe[idx] = { ...wardrobe[idx], ...updated };
          renderWardrobe();
        }
        editItemModal.classList.add('hidden');
      } else {
        const err = await res.json();
        alert('Failed to save changes: ' + (err.detail || 'Unknown error'));
      }
    } catch (err) {
      alert('Failed to update item: ' + err.message);
    } finally {
      btnSaveEditItem.disabled = false;
      btnSaveEditItem.innerHTML = '<i data-lucide="check" class="w-4 h-4"></i> Save Changes';
      lucide.createIcons();
    }
  });

  // Re-analyze item directly from the edit modal
  if (btnReanalyzeItem) {
    btnReanalyzeItem.addEventListener('click', async () => {
      const id = editItemId.value;
      if (!id) return;
      btnReanalyzeItem.disabled = true;
      btnReanalyzeItem.innerHTML = '<div class="w-3 h-3 rounded-full border-2 border-zinc-400 border-t-zinc-900 animate-spin"></div> Analyzing...';

      try {
        const res = await fetch(`/api/analyze-item/${id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            base_url: currentSettings.base_url,
            api_key: currentSettings.api_key,
            model: currentSettings.model
          })
        });

        if (res.ok) {
          const updated = await res.json();
          const idx = wardrobe.findIndex(w => w.id === id);
          if (idx !== -1) {
            wardrobe[idx] = { ...wardrobe[idx], ...updated };
            renderWardrobe();
          }
          // Refresh fields in modal
          populateEditModal(updated);
        } else {
          const err = await res.json();
          alert('Re-analysis failed: ' + (err.detail || 'Error'));
        }
      } catch (err) {
        alert('Re-analysis error: ' + err.message);
      } finally {
        btnReanalyzeItem.disabled = false;
        btnReanalyzeItem.innerHTML = '<i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i> Re-Analyze with AI';
        lucide.createIcons();
      }
    });
  }
}

// Upload each file one-by-one to extract info using single-image vision call
async function handleFiles(files) {
  const validFiles = Array.from(files).filter(f => f.type.startsWith('image/'));
  if (validFiles.length === 0) return;

  uploadProgressBanner.classList.remove('hidden');

  for (let i = 0; i < validFiles.length; i++) {
    const file = validFiles[i];
    uploadProgressText.textContent = `Cataloging ${file.name} (${i + 1} of ${validFiles.length})...`;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' '));
    if (currentSettings.base_url) formData.append('base_url', currentSettings.base_url);
    if (currentSettings.api_key) formData.append('api_key', currentSettings.api_key);
    if (currentSettings.model) formData.append('model', currentSettings.model);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const item = await res.json();
        item.selected = true;
        // Check if already in array
        const existingIdx = wardrobe.findIndex(w => w.id === item.id);
        if (existingIdx !== -1) {
          wardrobe[existingIdx] = item;
        } else {
          wardrobe.unshift(item);
        }
        renderWardrobe();
      }
    } catch (err) {
      console.error('Upload error for file', file.name, err);
    }
  }

  uploadProgressBanner.classList.add('hidden');
  renderWardrobe();
}

// Load sample wardrobe into SQLite DB
async function loadSampleWardrobe() {
  btnLoadSample.disabled = true;
  btnLoadSampleEmpty.disabled = true;
  try {
    const res = await fetch('/api/samples', { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      wardrobe = (data.items || []).map(item => ({ ...item, selected: true }));
      renderWardrobe();
    }
  } catch (err) {
    alert('Failed to load sample wardrobe: ' + err.message);
  } finally {
    btnLoadSample.disabled = false;
    btnLoadSampleEmpty.disabled = false;
  }
}

// Render wardrobe grid
function renderWardrobe() {
  const count = wardrobe.length;
  const selectedCount = wardrobe.filter(w => w.selected).length;

  wardrobeCountPill.textContent = `${count} ${count === 1 ? 'item' : 'items'} (${selectedCount} selected)`;

  if (count === 0) {
    wardrobeGrid.innerHTML = '';
    wardrobeEmptyState.classList.remove('hidden');
    btnGenerateStyle.disabled = true;
    return;
  }

  wardrobeEmptyState.classList.add('hidden');
  btnGenerateStyle.disabled = selectedCount === 0;

  wardrobeGrid.innerHTML = wardrobe.map((item) => {
    const badgeClass = getCategoryBadgeClass(item.category);
    const colorHex = item.color_hex || '#71717A';
    const subCat = item.sub_category || item.category;
    const isAnalyzed = item.is_analyzed;

    return `
      <div class="garment-card group relative bg-white rounded-xl border ${item.selected ? 'border-zinc-400 ring-2 ring-zinc-900/10' : 'border-zinc-200 opacity-60'} overflow-hidden flex flex-col">
        
        <!-- Top Toolbar & Checkbox -->
        <div class="absolute top-2 left-2 z-10">
          <input 
            type="checkbox" 
            ${item.selected ? 'checked' : ''} 
            onchange="toggleItemSelection('${item.id}')"
            class="w-4 h-4 rounded text-zinc-900 focus:ring-zinc-900 border-zinc-300 cursor-pointer shadow-sm"
          />
        </div>

        <div class="absolute top-2 right-2 z-10 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            onclick="openEditItemModal('${item.id}')" 
            class="w-6 h-6 rounded-md bg-white/90 text-zinc-700 hover:text-black flex items-center justify-center shadow-sm"
            title="Edit details"
          >
            <i data-lucide="pencil" class="w-3 h-3"></i>
          </button>
          <button 
            onclick="deleteItem('${item.id}')" 
            class="w-6 h-6 rounded-md bg-white/90 text-rose-600 hover:text-rose-800 flex items-center justify-center shadow-sm"
            title="Delete"
          >
            <i data-lucide="trash-2" class="w-3 h-3"></i>
          </button>
        </div>

        <!-- Image Container -->
        <div class="aspect-square w-full bg-zinc-50 flex items-center justify-center overflow-hidden cursor-pointer relative" onclick="toggleItemSelection('${item.id}')">
          <img src="${item.image_url}" alt="${item.name}" class="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-300">
          
          <!-- Analyzed Status Badge -->
          <div class="absolute bottom-2 left-2 flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white/90 backdrop-blur-xs text-[10px] font-semibold text-zinc-800 border border-zinc-200/80 shadow-xs">
            <span class="w-2.5 h-2.5 rounded-full border border-black/10 shadow-xs" style="background-color: ${colorHex}"></span>
            <span class="truncate max-w-[80px]">${item.color_primary || 'Color'}</span>
          </div>

          ${isAnalyzed ? `
            <div class="absolute bottom-2 right-2 flex items-center gap-0.5 px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-semibold border border-emerald-200" title="Analyzed & stored in DB for zero-image styling">
              <i data-lucide="check" class="w-3 h-3"></i>
              <span>Indexed</span>
            </div>
          ` : `
            <button onclick="analyzeItemDirectly(event, '${item.id}')" class="absolute bottom-2 right-2 px-2 py-0.5 rounded-full bg-zinc-900 text-white text-[10px] font-semibold shadow-xs hover:bg-black transition-colors">
              Analyze
            </button>
          `}
        </div>

        <!-- Item Info -->
        <div class="p-3 border-t border-zinc-100 flex-1 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between gap-1 mb-1">
              <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${badgeClass}">
                ${subCat}
              </span>
            </div>
            <h4 class="text-xs font-semibold text-zinc-900 truncate" title="${item.name}">${item.name}</h4>
            <p class="text-[11px] text-zinc-500 truncate mt-0.5" title="${item.material_texture || ''}">${item.material_texture || item.fit_silhouette || ''}</p>
          </div>
        </div>
      </div>
    `;
  }).join('');

  lucide.createIcons();
}

window.toggleItemSelection = function(id) {
  const item = wardrobe.find(w => w.id === id);
  if (item) {
    item.selected = !item.selected;
    renderWardrobe();
  }
};

window.deleteItem = async function(id) {
  try {
    const res = await fetch(`/api/wardrobe/${id}`, { method: 'DELETE' });
    if (res.ok) {
      wardrobe = wardrobe.filter(w => w.id !== id);
      renderWardrobe();
    }
  } catch (err) {
    alert('Failed to delete item: ' + err.message);
  }
};

window.openEditItemModal = function(id) {
  const item = wardrobe.find(w => w.id === id);
  if (!item) return;
  populateEditModal(item);
  editItemModal.classList.remove('hidden');
  lucide.createIcons();
};

function populateEditModal(item) {
  editItemId.value = item.id;
  editItemName.value = item.name || '';
  if (editItemImgPreview) editItemImgPreview.src = item.image_url || '';
  
  // Color fields
  const hex = (item.color_hex && item.color_hex.startsWith('#') && item.color_hex.length === 7) 
    ? item.color_hex 
    : '#4A5568';
  editItemColorPicker.value = hex;
  editItemColorHex.value = hex;
  editItemColorPrimary.value = item.color_primary || '';
  editItemColorSecondary.value = item.color_secondary || '';

  // Classifications
  editItemCategory.value = item.category || 'Tops';
  editItemSubCategory.value = item.sub_category || '';
  editItemPattern.value = item.pattern || 'Solid';

  // Details
  editItemMaterial.value = item.material_texture || '';
  editItemFit.value = item.fit_silhouette || '';
  editItemFormality.value = item.formality_level || 'Casual';

  // Vibes & Features
  const vibes = Array.isArray(item.style_vibes) ? item.style_vibes.join(', ') : (item.style_vibes || '');
  const features = Array.isArray(item.key_features) ? item.key_features.join(', ') : (item.key_features || '');
  editItemVibes.value = vibes;
  editItemFeatures.value = features;
  editItemDescription.value = item.full_description || '';
}

window.applyColorPreset = function(colorName, hex) {
  editItemColorPrimary.value = colorName;
  editItemColorHex.value = hex;
  editItemColorPicker.value = hex;
};

window.analyzeItemDirectly = async function(event, id) {
  event.stopPropagation();
  const btn = event.currentTarget;
  btn.textContent = '...';
  try {
    const res = await fetch(`/api/analyze-item/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: currentSettings.base_url,
        api_key: currentSettings.api_key,
        model: currentSettings.model
      })
    });
    if (res.ok) {
      const updated = await res.json();
      const idx = wardrobe.findIndex(w => w.id === id);
      if (idx !== -1) {
        wardrobe[idx] = { ...wardrobe[idx], ...updated };
        renderWardrobe();
      }
    }
  } catch (err) {
    alert('Extraction failed: ' + err.message);
  }
};

function getCategoryBadgeClass(category) {
  switch ((category || '').toLowerCase()) {
    case 'tops': return 'badge-tops';
    case 'bottoms': return 'badge-bottoms';
    case 'outerwear': return 'badge-outerwear';
    case 'footwear': return 'badge-footwear';
    case 'accessories': return 'badge-accessories';
    default: return 'badge-default';
  }
}

// Generate Outfits & Shopping Advice using ZERO IMAGES
async function generateStyleAdvice() {
  const selectedItems = wardrobe.filter(w => w.selected);
  if (selectedItems.length === 0) {
    alert('Please select at least 1 clothing item to style.');
    return;
  }

  // Scroll to consultation view & show loading state
  loadingState.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  btnGenerateStyle.disabled = true;
  loadingState.scrollIntoView({ behavior: 'smooth' });

  const vibeNotes = document.getElementById('vibe-notes').value.trim();

  // Send ONLY item IDs & text data - NO IMAGES SENT TO MODEL!
  const payload = {
    item_ids: selectedItems.map(i => i.id),
    occasion: selectedOccasion,
    season: selectedSeason,
    vibe_notes: vibeNotes,
    base_url: currentSettings.base_url,
    api_key: currentSettings.api_key,
    model: currentSettings.model
  };

  try {
    const res = await fetch('/api/style', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate recommendations');
    }

    const data = await res.json();
    renderResults(data);
  } catch (err) {
    alert('Styling Consultation Error: ' + err.message);
  } finally {
    loadingState.classList.add('hidden');
    btnGenerateStyle.disabled = false;
  }
}

// Render Results
function renderResults(data) {
  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth' });

  // Notice Banner (Demo mode or Model fallback)
  if (data._notice) {
    demoNotice.classList.remove('hidden');
    const titleElem = demoNotice.querySelector('p.font-semibold');
    const textElem = demoNotice.querySelector('p.text-amber-800');
    if (titleElem) {
      titleElem.textContent = data._fallback_mode ? 'Styling Model Advisory' : 'Showing Demo Stylist Results';
    }
    if (textElem) {
      textElem.innerHTML = `${data._notice} <button class="underline font-semibold ml-1" onclick="document.getElementById('btn-open-settings').click()">Change Model</button>`;
    }
  } else if (data._demo_mode) {
    demoNotice.classList.remove('hidden');
  } else {
    demoNotice.classList.add('hidden');
  }

  // 1. Render Outfits
  const outfitsContainer = document.getElementById('outfits-container');
  const outfits = data.outfits || [];
  
  outfitsContainer.innerHTML = outfits.map((outfit) => {
    // Find matching images from local wardrobe
    const piecesImages = (outfit.piece_ids || []).map(id => {
      const match = wardrobe.find(w => w.id === id);
      return match ? `<img src="${match.image_url}" alt="${match.name}" title="${match.name}" class="w-10 h-10 rounded-lg object-contain bg-white border border-zinc-200 p-1 shadow-xs">` : '';
    }).filter(Boolean).join('');

    const piecePills = (outfit.piece_names || []).map(name => 
      `<span class="text-[11px] font-medium px-2 py-0.5 rounded-md bg-zinc-100 text-zinc-700">${name}</span>`
    ).join('');

    return `
      <div class="bg-white rounded-2xl border border-zinc-200/90 shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="space-y-4">
          
          <div class="flex items-start justify-between gap-2">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200/60">
                ${outfit.occasion || 'Outfit Look'}
              </span>
              <h3 class="font-serif text-xl font-bold text-zinc-900 mt-1.5">${outfit.title}</h3>
            </div>
            <span class="text-xs font-semibold px-2 py-1 bg-zinc-100 rounded-lg text-zinc-600">
              ${outfit.vibe || 'Curated'}
            </span>
          </div>

          <!-- Uploaded pieces preview -->
          <div class="space-y-2 pt-2 border-t border-zinc-100">
            <span class="text-[11px] font-bold uppercase tracking-wider text-zinc-400">Garments Used</span>
            ${piecesImages ? `<div class="flex items-center gap-2">${piecesImages}</div>` : ''}
            <div class="flex flex-wrap gap-1.5 pt-1">${piecePills}</div>
          </div>

          <!-- Styling Guide -->
          <div class="space-y-1.5 pt-2 border-t border-zinc-100">
            <span class="text-[11px] font-bold uppercase tracking-wider text-zinc-500 flex items-center gap-1.5">
              <i data-lucide="sparkle" class="w-3.5 h-3.5 text-amber-500"></i>
              Styling Execution
            </span>
            <p class="text-xs text-zinc-700 leading-relaxed font-normal">${outfit.styling_guide}</p>
          </div>

          <!-- Why it works -->
          <div class="space-y-1.5 pt-2 border-t border-zinc-100">
            <span class="text-[11px] font-bold uppercase tracking-wider text-zinc-500 flex items-center gap-1.5">
              <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-emerald-600"></i>
              Why This Works
            </span>
            <p class="text-xs text-zinc-600 leading-relaxed">${outfit.why_it_works}</p>
          </div>

        </div>
      </div>
    `;
  }).join('');

  // 2. Render What to Buy
  const buyingContainer = document.getElementById('buying-container');
  const suggestions = data.buying_suggestions || [];

  buyingContainer.innerHTML = suggestions.map((item) => {
    const query = item.search_query || `${item.ideal_color || ''} ${item.item_name}`;
    const googleShopUrl = `https://www.google.com/search?tbm=shop&q=${encodeURIComponent(query)}`;
    const amazonUrl = `https://www.amazon.com/s?k=${encodeURIComponent(query)}`;
    const asosUrl = `https://www.asos.com/search/?q=${encodeURIComponent(query)}`;

    let priorityBadge = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    if (item.priority?.includes('Staple')) {
      priorityBadge = 'bg-blue-50 text-blue-700 border-blue-200';
    } else if (item.priority?.includes('Accent')) {
      priorityBadge = 'bg-purple-50 text-purple-700 border-purple-200';
    }

    return `
      <div class="bg-white rounded-2xl border border-zinc-200 shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="space-y-4">
          
          <div class="flex items-start justify-between gap-2">
            <div>
              <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${priorityBadge}">
                ${item.priority || 'Recommended'}
              </span>
              <h3 class="font-serif text-lg font-bold text-zinc-900 mt-2">${item.item_name}</h3>
              <span class="text-xs text-zinc-500">${item.category}</span>
            </div>
            <div class="w-8 h-8 rounded-lg bg-zinc-100 text-zinc-700 flex items-center justify-center flex-shrink-0">
              <i data-lucide="tag" class="w-4 h-4"></i>
            </div>
          </div>

          <!-- Color & Material -->
          <div class="space-y-1 bg-zinc-50 p-3 rounded-xl border border-zinc-100 text-xs">
            <div><span class="font-bold text-zinc-700">Ideal Color:</span> <span class="text-zinc-600">${item.ideal_color}</span></div>
            <div><span class="font-bold text-zinc-700">Material & Cut:</span> <span class="text-zinc-600">${item.ideal_material_and_fit}</span></div>
          </div>

          <!-- Wardrobe Multiplier -->
          <div class="space-y-1 pt-2 border-t border-zinc-100">
            <span class="text-[11px] font-bold uppercase tracking-wider text-zinc-500 flex items-center gap-1.5">
              <i data-lucide="repeat" class="w-3.5 h-3.5 text-indigo-500"></i>
              Wardrobe Multiplier
            </span>
            <p class="text-xs text-zinc-700 leading-relaxed">${item.wardrobe_multiplier}</p>
          </div>

        </div>

        <!-- Shopping Search Actions -->
        <div class="pt-5 mt-5 border-t border-zinc-100 space-y-2">
          <span class="text-[10px] font-bold uppercase tracking-wider text-zinc-400">Find & Shop Online</span>
          <div class="grid grid-cols-3 gap-2">
            <a 
              href="${googleShopUrl}" 
              target="_blank" 
              class="px-2 py-2 text-center text-xs font-semibold bg-zinc-900 hover:bg-black text-white rounded-lg transition-colors flex items-center justify-center gap-1"
            >
              Google
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
            <a 
              href="${amazonUrl}" 
              target="_blank" 
              class="px-2 py-2 text-center text-xs font-semibold bg-zinc-100 hover:bg-zinc-200 text-zinc-800 rounded-lg transition-colors flex items-center justify-center gap-1"
            >
              Amazon
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
            <a 
              href="${asosUrl}" 
              target="_blank" 
              class="px-2 py-2 text-center text-xs font-semibold bg-zinc-100 hover:bg-zinc-200 text-zinc-800 rounded-lg transition-colors flex items-center justify-center gap-1"
            >
              ASOS
              <i data-lucide="external-link" class="w-3 h-3"></i>
            </a>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // 3. Render Wardrobe Audit
  const audit = data.wardrobe_audit || {};
  document.getElementById('audit-score').textContent = audit.versatility_score || '85';
  document.getElementById('audit-aesthetic').textContent = audit.style_aesthetic || 'Modern Casual';
  
  const paletteContainer = document.getElementById('audit-palette');
  const palette = audit.color_palette || [];
  paletteContainer.innerHTML = palette.map(c => `
    <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-zinc-200 bg-white shadow-xs">
      <span class="w-4 h-4 rounded-full border border-black/10 shadow-xs" style="background-color: ${c.hex}"></span>
      <span class="text-xs font-medium text-zinc-800">${c.name}</span>
      <span class="text-[10px] text-zinc-400 font-mono">${c.hex}</span>
    </div>
  `).join('');

  const strengthsContainer = document.getElementById('audit-strengths');
  const strengths = audit.strengths || [];
  strengthsContainer.innerHTML = strengths.map(s => `
    <li class="flex items-start gap-2">
      <i data-lucide="check" class="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5"></i>
      <span>${s}</span>
    </li>
  `).join('');

  lucide.createIcons();
}

// Settings Modal Logic
function openSettingsModal() {
  settingProviderPreset.value = currentSettings.provider;
  settingBaseUrl.value = currentSettings.base_url;
  settingModel.value = currentSettings.model;
  settingApiKey.value = currentSettings.api_key;
  testConnectionResult.classList.add('hidden');
  renderPresetDetails(currentSettings.provider);
  settingsModal.classList.remove('hidden');
  lucide.createIcons();
}

function closeSettingsModal() {
  settingsModal.classList.add('hidden');
}

function onPresetChange() {
  const chosen = settingProviderPreset.value;
  renderPresetDetails(chosen);
}

function renderPresetDetails(providerKey) {
  const info = presets[providerKey];
  if (!info) return;

  settingBaseUrl.value = info.base_url || '';
  settingModel.value = info.default_model || '';
  presetDescription.textContent = info.description || '';
  
  if (info.doc_url) {
    settingKeyDoc.href = info.doc_url;
    settingKeyDoc.classList.remove('hidden');
  } else {
    settingKeyDoc.classList.add('hidden');
  }

  // Recommended model tags
  const recs = info.recommended_models || [];
  recommendedModelsContainer.innerHTML = recs.map(m => `
    <button 
      type="button" 
      onclick="selectModel('${m}')" 
      class="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-700 transition-colors"
    >
      ${m}
    </button>
  `).join('');
}

window.selectModel = function(modelName) {
  settingModel.value = modelName;
};

async function testConnection() {
  btnTestConnection.disabled = true;
  btnTestConnection.innerHTML = '<div class="w-3 h-3 rounded-full border-2 border-zinc-400 border-t-zinc-900 animate-spin"></div> Testing...';
  testConnectionResult.classList.add('hidden');

  try {
    const res = await fetch('/api/test-connection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_url: settingBaseUrl.value.trim(),
        api_key: settingApiKey.value.trim(),
        model: settingModel.value.trim()
      })
    });

    const data = await res.json();
    testConnectionResult.classList.remove('hidden');
    if (data.success) {
      testConnectionResult.className = 'p-3 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 text-xs';
      testConnectionResult.innerHTML = `<strong>Connected!</strong> ${data.message}`;
    } else {
      testConnectionResult.className = 'p-3 rounded-xl bg-rose-50 text-rose-800 border border-rose-200 text-xs';
      testConnectionResult.innerHTML = `<strong>Error:</strong> ${data.message}`;
    }
  } catch (err) {
    testConnectionResult.classList.remove('hidden');
    testConnectionResult.className = 'p-3 rounded-xl bg-rose-50 text-rose-800 border border-rose-200 text-xs';
    testConnectionResult.innerHTML = `<strong>Connection error:</strong> ${err.message}`;
  } finally {
    btnTestConnection.disabled = false;
    btnTestConnection.innerHTML = '<i data-lucide="activity" class="w-3.5 h-3.5"></i> Test Connection';
    lucide.createIcons();
  }
}

function saveSettingsModal() {
  currentSettings.provider = settingProviderPreset.value;
  currentSettings.base_url = settingBaseUrl.value.trim();
  currentSettings.model = settingModel.value.trim();
  currentSettings.api_key = settingApiKey.value.trim();

  localStorage.setItem('colorme_settings', JSON.stringify(currentSettings));
  updateProviderBadge();
  closeSettingsModal();
}
