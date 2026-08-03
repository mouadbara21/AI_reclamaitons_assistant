/**
 * PortNet Souscription — Document Upload Logic
 *
 * Handles:
 *  - File selection & drag-and-drop for each upload slot
 *  - Real-time document classification via /api/souscription/verify-single
 *  - Form validation (all required files + terms checkbox)
 *  - Final submission via /api/souscription/upload
 *  - Redirect to result page
 */

(function () {
    'use strict';

    // ─── Configuration ───────────────────────────────────────────
    var API_BASE = '';  // Same origin
    var MAX_FILE_SIZE = 3 * 1024 * 1024; // 3 MB

    // Slots that require a file upload (CIN removed from required since procuration is optional)
    var REQUIRED_SLOTS = [
        'cni', 'categorie_operateur', 'statuts', 'model_j',
        'taxe_professionnelle', 'ice', 'attestation_rib', 'document_if'
    ];

    // Store uploaded files by slot
    var uploadedFiles = {};

    // ─── DOM Ready ───────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        initUploadBoxes();
        initFormValidation();
        initSubmitHandler();
    });

    // ─── Upload Box Initialization ───────────────────────────────
    function initUploadBoxes() {
        var boxes = document.querySelectorAll('.sousc-upload-box');

        boxes.forEach(function (box) {
            var slot = box.getAttribute('data-slot');
            var area = box.querySelector('.sousc-upload-area');
            var input = box.querySelector('.sousc-upload-input');
            var btn = box.querySelector('.sousc-upload-btn');
            var removeBtn = box.querySelector('.sousc-upload-remove');
            var textEl = box.querySelector('.sousc-upload-text');
            var iconEl = box.querySelector('.sousc-upload-icon');

            // Click on area or button opens file picker
            area.addEventListener('click', function (e) {
                if (e.target === removeBtn || e.target.closest('.sousc-upload-remove')) return;
                input.click();
            });

            // File selected
            input.addEventListener('change', function () {
                if (input.files.length > 0) {
                    handleFileSelected(slot, input.files[0], area, textEl, iconEl);
                }
            });

            // Remove file
            removeBtn.addEventListener('click', function (e) {
                e.stopPropagation();
                removeFile(slot, area, textEl, iconEl, input);
            });

            // Drag and drop
            area.addEventListener('dragover', function (e) {
                e.preventDefault();
                area.classList.add('drag-over');
            });

            area.addEventListener('dragleave', function () {
                area.classList.remove('drag-over');
            });

            area.addEventListener('drop', function (e) {
                e.preventDefault();
                area.classList.remove('drag-over');
                if (e.dataTransfer.files.length > 0) {
                    var file = e.dataTransfer.files[0];
                    // Update the hidden input with the dropped file
                    var dt = new DataTransfer();
                    dt.items.add(file);
                    input.files = dt.files;
                    handleFileSelected(slot, file, area, textEl, iconEl);
                }
            });
        });
    }

    // ─── Handle File Selected ────────────────────────────────────
    function handleFileSelected(slot, file, area, textEl, iconEl) {
        // Validate PDF
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showBadge(slot, 'error', '<i class="fas fa-exclamation-circle"></i> Seuls les fichiers PDF sont acceptés.');
            return;
        }

        // Validate size
        if (file.size > MAX_FILE_SIZE) {
            showBadge(slot, 'error', '<i class="fas fa-exclamation-circle"></i> Le fichier dépasse 3 MO.');
            return;
        }

        // Update UI
        uploadedFiles[slot] = file;
        area.classList.add('has-file');
        textEl.textContent = file.name;
        textEl.classList.add('has-file');
        iconEl.innerHTML = '<i class="fas fa-file-pdf"></i>';

        // Trigger real-time verification
        verifyDocument(slot, file);

        // Re-validate form
        validateForm();
    }

    // ─── Remove File ─────────────────────────────────────────────
    function removeFile(slot, area, textEl, iconEl, input) {
        delete uploadedFiles[slot];
        area.classList.remove('has-file');
        textEl.textContent = 'Choisir un fichier';
        textEl.classList.remove('has-file');
        iconEl.innerHTML = '<i class="fas fa-cloud-upload-alt"></i>';
        input.value = '';
        hideBadge(slot);
        validateForm();
    }

    // ─── Real-time Document Verification ─────────────────────────
    function verifyDocument(slot, file) {
        // Show loading badge
        showBadge(slot, 'loading', '<div class="spinner-sm"></div> Vérification du document...');

        var formData = new FormData();
        formData.append('file', file);
        formData.append('slot', slot);

        fetch(API_BASE + '/api/souscription/verify-single', {
            method: 'POST',
            body: formData,
        })
        .then(function (response) { return response.json(); })
        .then(function (data) {
            if (data.status === 'success') {
                showBadge(slot, 'success',
                    '<i class="fas fa-check-circle"></i> ' + data.message);
            } else if (data.status === 'warning') {
                showBadge(slot, 'warning',
                    '<i class="fas fa-exclamation-triangle"></i> ' + data.message);
            } else if (data.status === 'manual') {
                showBadge(slot, 'manual',
                    '<i class="fas fa-user-shield"></i> ' + data.message);
            } else {
                showBadge(slot, 'error',
                    '<i class="fas fa-times-circle"></i> ' + data.message);
            }
        })
        .catch(function (err) {
            showBadge(slot, 'warning',
                '<i class="fas fa-exclamation-triangle"></i> Impossible de vérifier le document. Il sera vérifié lors de la soumission.');
        });
    }

    // ─── Badge Helpers ───────────────────────────────────────────
    function showBadge(slot, type, html) {
        var badge = document.getElementById('badge-' + slot);
        if (!badge) return;
        badge.className = 'sousc-verify-badge visible ' + type;
        badge.innerHTML = html;
    }

    function hideBadge(slot) {
        var badge = document.getElementById('badge-' + slot);
        if (!badge) return;
        badge.className = 'sousc-verify-badge';
        badge.innerHTML = '';
    }

    // ─── Form Validation ─────────────────────────────────────────
    function initFormValidation() {
        var termsCheckbox = document.getElementById('termsCheckbox');
        var formInputs = document.querySelectorAll('.sousc-form-input[required]');

        termsCheckbox.addEventListener('change', validateForm);
        formInputs.forEach(function (input) {
            input.addEventListener('input', validateForm);
        });
    }

    function validateForm() {
        var submitBtn = document.getElementById('submitBtn');
        var termsChecked = document.getElementById('termsCheckbox').checked;

        // Check all required form inputs
        var formInputs = document.querySelectorAll('.sousc-form-input[required]');
        var allFormFilled = true;
        formInputs.forEach(function (input) {
            if (!input.value.trim()) {
                allFormFilled = false;
            }
        });

        // Check all required file slots
        var allFilesFilled = true;
        REQUIRED_SLOTS.forEach(function (slot) {
            if (!uploadedFiles[slot]) {
                allFilesFilled = false;
            }
        });

        submitBtn.disabled = !(termsChecked && allFormFilled && allFilesFilled);
    }

    // ─── Submit Handler ──────────────────────────────────────────
    function initSubmitHandler() {
        var form = document.getElementById('souscriptionForm');

        form.addEventListener('submit', function (e) {
            e.preventDefault();

            var submitBtn = document.getElementById('submitBtn');
            if (submitBtn.disabled) return;

            // Show loading overlay
            document.getElementById('loadingOverlay').classList.add('active');
            submitBtn.disabled = true;

            // Build FormData with all form fields and files
            var formData = new FormData();

            // Form fields
            formData.append('raison_sociale', document.getElementById('inputRaisonSociale').value.trim());
            formData.append('ice', document.getElementById('inputICE').value.trim());
            formData.append('rc_number', document.getElementById('inputRC').value.trim());
            formData.append('rc_city', document.getElementById('inputRCCity').value.trim());
            formData.append('if_number', document.getElementById('inputIF').value.trim());
            formData.append('tp_number', document.getElementById('inputTP').value.trim());
            formData.append('siege_social', document.getElementById('inputSiege').value.trim());
            formData.append('gerant_nom', document.getElementById('inputGerantNom').value.trim());
            formData.append('gerant_prenom', document.getElementById('inputGerantPrenom').value.trim());
            formData.append('gerant_cin', document.getElementById('inputGerantCIN').value.trim());
            formData.append('rib', '');

            // Files — use the input names that match the FastAPI parameter names
            var slotToFormName = {
                'cni': 'cni',
                'categorie_operateur': 'categorie_operateur',
                'statuts': 'statuts',
                'model_j': 'model_j',
                'procuration': 'procuration',
                'taxe_professionnelle': 'taxe_professionnelle',
                'ice': 'ice_doc',
                'attestation_rib': 'attestation_rib',
                'document_if': 'document_if',
            };

            Object.keys(uploadedFiles).forEach(function (slot) {
                var formName = slotToFormName[slot] || slot;
                formData.append(formName, uploadedFiles[slot]);
            });

            // Submit
            fetch(API_BASE + '/api/souscription/upload', {
                method: 'POST',
                body: formData,
            })
            .then(function (response) {
                if (!response.ok) {
                    return response.text().then(function (txt) {
                        throw new Error('Erreur ' + response.status + ' : ' + (txt.length > 200 ? txt.substring(0, 200) + '...' : txt));
                    });
                }
                return response.json();
            })
            .then(function (data) {
                // Redirect to result page
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else if (data.souscription_id) {
                    window.location.href = '/resultat.html?id=' + data.souscription_id;
                } else {
                    throw new Error('Pas de redirection reçue');
                }
            })
            .catch(function (err) {
                document.getElementById('loadingOverlay').classList.remove('active');
                submitBtn.disabled = false;
                alert('Erreur lors de la soumission : ' + err.message);
            });
        });
    }

})();
