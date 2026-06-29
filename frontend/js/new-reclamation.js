/* ================================================================
 * new-reclamation.js — 3-step "Nouvelle réclamation" form wizard
 * Manages step navigation, validation, dropdowns, file upload,
 * and submission.
 * ================================================================ */

window.PortnetApp = window.PortnetApp || {};

PortnetApp.NewReclamation = (function () {

    var currentStep = 1;
    var totalSteps  = 3;
    var formData = {
        id_type_reclamation: null,
        id_service_reclamation: null,
        objet: '',
        description: '',
        files: []
    };

    // DOM references
    var $overlay, $footer, $progressFill;
    var $btnRetour, $btnSuivant, $btnSoumettre;

    /**
     * Initialize the module.
     */
    function init() {
        $overlay      = $('#newRecOverlay');
        $footer       = $('#newRecFooter');
        $progressFill = $('#progressFill');
        $btnRetour    = $('#btnRetour');
        $btnSuivant   = $('#btnSuivant');
        $btnSoumettre = $('#btnSoumettre');

        // Navigation buttons
        $btnRetour.on('click', goBack);
        $btnSuivant.on('click', goNext);
        $btnSoumettre.on('click', submitForm);

        // Close button
        $('#newRecCloseBtn').on('click', close);
        $overlay.on('click', function (e) {
            if (e.target === $overlay[0]) close();
        });

        // Initialize dropdowns
        initTypeDropdown();
        initServiceDropdown();

        // File upload
        initFileUpload();

        // Form input listeners for validation
        $('#inputObjet').on('input', validateCurrentStep);
        $('#inputSujet').on('input', validateCurrentStep);
    }

    // ── DROPDOWN: Type de demande ──────────────────────────────

    function initTypeDropdown() {
        var $dropdown = $('#typeDropdown');
        var $trigger  = $('#typeTrigger');
        var $options  = $('#typeOptions');

        // Populate options
        var types = PortnetApp.API.getAllTypes();
        var html = '';
        types.forEach(function (t) {
            html += '<div class="custom-dropdown-option" data-value="' + t.id + '">' + t.label + '</div>';
        });
        $options.html(html);

        // Toggle dropdown
        $trigger.on('click', function (e) {
            e.stopPropagation();
            var isOpen = $options.hasClass('open');
            closeAllDropdowns();
            if (!isOpen) {
                $options.addClass('open');
                $trigger.addClass('open');
            }
        });

        // Select option
        $options.on('click', '.custom-dropdown-option', function () {
            var $opt = $(this);
            var value = parseInt($opt.data('value'));
            var label = $opt.text();

            formData.id_type_reclamation = value;

            $trigger.removeClass('placeholder').find('span').text(label);
            $dropdown.addClass('has-value');
            $options.find('.custom-dropdown-option').removeClass('selected');
            $opt.addClass('selected');

            closeAllDropdowns();
            validateCurrentStep();
        });
    }

    // ── DROPDOWN: Service concerné (searchable) ────────────────

    function initServiceDropdown() {
        var $dropdown    = $('#serviceDropdown');
        var $trigger     = $('#serviceTrigger');
        var $options     = $('#serviceOptions');
        var $optionsList = $('#serviceOptionsList');
        var $searchInput = $('#serviceSearchInput');

        // Populate options
        renderServiceOptions('');

        // Toggle dropdown
        $trigger.on('click', function (e) {
            e.stopPropagation();
            var isOpen = $options.hasClass('open');
            closeAllDropdowns();
            if (!isOpen) {
                $options.addClass('open');
                $trigger.addClass('open');
                setTimeout(function () { $searchInput.focus(); }, 100);
            }
        });

        // Search filter
        $searchInput.on('input', function () {
            renderServiceOptions($(this).val());
        });

        // Prevent dropdown close on search input click
        $searchInput.on('click', function (e) {
            e.stopPropagation();
        });

        // Select option
        $optionsList.on('click', '.custom-dropdown-option', function () {
            var $opt = $(this);
            var value = parseInt($opt.data('value'));
            var label = $opt.text();

            formData.id_service_reclamation = value;

            $trigger.removeClass('placeholder').find('span').text(label);
            $dropdown.addClass('has-value');
            $optionsList.find('.custom-dropdown-option').removeClass('selected');
            $opt.addClass('selected');
            $searchInput.val('');

            closeAllDropdowns();
            validateCurrentStep();
        });
    }

    function renderServiceOptions(filter) {
        var $optionsList = $('#serviceOptionsList');
        var services = PortnetApp.API.getAllServices();
        var term = (filter || '').toLowerCase();

        var filtered = services.filter(function (s) {
            return term === '' || s.label.toLowerCase().indexOf(term) !== -1;
        });

        if (filtered.length === 0) {
            $optionsList.html('<div class="dropdown-no-results">Aucun service trouvé</div>');
            return;
        }

        var html = '';
        filtered.forEach(function (s) {
            var selectedClass = formData.id_service_reclamation === s.id ? ' selected' : '';
            html += '<div class="custom-dropdown-option' + selectedClass + '" data-value="' + s.id + '">' + s.label + '</div>';
        });
        $optionsList.html(html);
    }

    // ── CLOSE DROPDOWNS ────────────────────────────────────────

    function closeAllDropdowns() {
        $('.custom-dropdown-options').removeClass('open');
        $('.custom-dropdown-trigger').removeClass('open');
    }

    // Close dropdowns on outside click
    $(document).on('click', function () {
        closeAllDropdowns();
    });

    // ── FILE UPLOAD ────────────────────────────────────────────

    function initFileUpload() {
        var $zone = $('#fileUploadZone');
        var $input = $('#fileInput');

        // Drag and drop
        $zone.on('dragover', function (e) {
            e.preventDefault();
            $(this).addClass('dragover');
        }).on('dragleave drop', function (e) {
            e.preventDefault();
            $(this).removeClass('dragover');
        }).on('drop', function (e) {
            var files = e.originalEvent.dataTransfer.files;
            addFiles(files);
        });

        // File input change
        $input.on('change', function () {
            addFiles(this.files);
            // Reset input so same file can be re-selected
            this.value = '';
        });
    }

    function addFiles(fileList) {
        for (var i = 0; i < fileList.length; i++) {
            formData.files.push(fileList[i]);
        }
        renderUploadedFiles();
        validateCurrentStep();
    }

    function removeFile(index) {
        formData.files.splice(index, 1);
        renderUploadedFiles();
        validateCurrentStep();
    }

    function renderUploadedFiles() {
        var $container = $('#uploadedFiles');
        if (formData.files.length === 0) {
            $container.html('');
            return;
        }

        var html = '';
        formData.files.forEach(function (file, i) {
            html += '<div class="uploaded-file">';
            html +=   '<i class="fas fa-file"></i>';
            html +=   '<span class="file-name">' + escapeHtml(file.name) + '</span>';
            html +=   '<i class="fas fa-times file-remove" data-index="' + i + '"></i>';
            html += '</div>';
        });
        $container.html(html);

        $container.find('.file-remove').on('click', function () {
            removeFile(parseInt($(this).data('index')));
        });
    }

    // ── STEP NAVIGATION ────────────────────────────────────────

    function goNext() {
        if (!isStepValid(currentStep)) return;
        if (currentStep < totalSteps) {
            currentStep++;
            updateUI();
        }
    }

    function goBack() {
        if (currentStep > 1) {
            currentStep--;
            updateUI();
        }
    }

    function updateUI() {
        // Update step containers
        $('.step-container').removeClass('active');
        $('#step' + currentStep).addClass('active');

        // Update progress bar
        var progress = (currentStep / totalSteps) * 100;
        $progressFill.css('width', progress + '%');

        // Update stepper circles
        for (var i = 1; i <= totalSteps; i++) {
            var $circle = $('#stepperCircle' + i);
            var $step   = $circle.closest('.stepper-step');
            var $line   = $('#stepperLine' + (i - 1));

            $circle.removeClass('active inactive completed');
            $step.removeClass('active completed');

            if (i < currentStep) {
                $circle.addClass('completed').html('<i class="fas fa-check"></i>');
                $step.addClass('completed');
                if ($line.length) $line.addClass('completed').removeClass('active');
            } else if (i === currentStep) {
                $circle.addClass('active').text(i);
                $step.addClass('active');
                if ($line.length) $line.addClass('active').removeClass('completed');
            } else {
                $circle.addClass('inactive').text(i);
                if ($line.length) $line.removeClass('active completed');
            }
        }

        // Update footer buttons
        if (currentStep === 1) {
            $btnRetour.css('visibility', 'hidden');
        } else {
            $btnRetour.css('visibility', 'visible');
        }

        if (currentStep === totalSteps) {
            $btnSuivant.hide();
            $btnSoumettre.show();
        } else {
            $btnSuivant.show();
            $btnSoumettre.hide();
        }

        validateCurrentStep();
    }

    // ── VALIDATION ─────────────────────────────────────────────

    function isStepValid(step) {
        switch (step) {
            case 1: return formData.id_type_reclamation !== null;
            case 2: return formData.id_service_reclamation !== null;
            case 3:
                formData.objet = $('#inputObjet').val().trim();
                formData.description = $('#inputSujet').val().trim();
                return formData.objet !== '' && formData.description !== '';
            default: return false;
        }
    }

    function validateCurrentStep() {
        var valid = isStepValid(currentStep);

        if (currentStep < totalSteps) {
            if (valid) {
                $btnSuivant.removeClass('disabled');
            } else {
                $btnSuivant.addClass('disabled');
            }
        } else {
            // Read inputs for step 3
            formData.objet = $('#inputObjet').val().trim();
            formData.description = $('#inputSujet').val().trim();
            valid = formData.objet !== '' && formData.description !== '';

            if (valid) {
                $btnSoumettre.removeClass('disabled');
            } else {
                $btnSoumettre.addClass('disabled');
            }
        }
    }

    // ── SUBMIT ─────────────────────────────────────────────────

    async function submitForm() {
        if (!isStepValid(currentStep)) return;

        // Disable button
        $btnSoumettre.addClass('disabled').html('<i class="fas fa-spinner fa-spin"></i> Envoi...');

        formData.objet = $('#inputObjet').val().trim();
        formData.description = $('#inputSujet').val().trim();

        try {
            var newRec = await PortnetApp.API.createReclamation(formData);

            // Show success screen
            $('.step-container').removeClass('active');
            $('#stepSuccess').addClass('active');
            $('#successRef').text('Référence : ' + newRec.reference);
            $footer.hide();

            // Refresh the reclamations list
            PortnetApp.ReclamationsList.load();

            // Show toast
            PortnetApp.App.showToast('Réclamation #' + newRec.reference + ' créée avec succès');

        } catch (err) {
            $btnSoumettre.removeClass('disabled').html('<i class="fas fa-check"></i> Soumettre');
            PortnetApp.App.showToast('Erreur lors de la soumission. Veuillez réessayer.');
        }
    }

    // ── OPEN / CLOSE ───────────────────────────────────────────

    function open() {
        reset();
        $overlay.addClass('active');
    }

    function close() {
        $overlay.removeClass('active');
        // Small delay then reset
        setTimeout(reset, 300);
    }

    function reset() {
        currentStep = 1;
        formData = {
            id_type_reclamation: null,
            id_service_reclamation: null,
            objet: '',
            description: '',
            files: []
        };

        // Reset dropdowns
        $('#typeTrigger').addClass('placeholder').find('span').text('Type de demande');
        $('#typeDropdown').removeClass('has-value');
        $('#typeOptions .custom-dropdown-option').removeClass('selected');

        $('#serviceTrigger').addClass('placeholder').find('span').text('Rechercher un service');
        $('#serviceDropdown').removeClass('has-value');
        $('#serviceSearchInput').val('');
        renderServiceOptions('');

        // Reset form inputs
        $('#inputObjet').val('');
        $('#inputSujet').val('');
        $('#uploadedFiles').html('');

        // Reset stepper
        for (var i = 1; i <= totalSteps; i++) {
            var $circle = $('#stepperCircle' + i);
            $circle.text(i).removeClass('active completed inactive');
            if (i === 1) $circle.addClass('active');
            else $circle.addClass('inactive');

            var $step = $circle.closest('.stepper-step');
            $step.removeClass('active completed');
            if (i === 1) $step.addClass('active');
        }
        $('#stepperLine1, #stepperLine2').removeClass('active completed');

        // Reset UI
        $progressFill.css('width', '33.33%');
        $footer.show();
        $btnRetour.css('visibility', 'hidden');
        $btnSuivant.show().addClass('disabled');
        $btnSoumettre.hide().removeClass('disabled').html('<i class="fas fa-check"></i> Soumettre');

        // Reset step containers
        $('.step-container').removeClass('active');
        $('#step1').addClass('active');
    }

    // ── HELPERS ─────────────────────────────────────────────────

    function escapeHtml(text) {
        if (!text) return '';
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    return {
        init: init,
        open: open,
        close: close
    };

})();
