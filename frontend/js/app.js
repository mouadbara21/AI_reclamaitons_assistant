/* ================================================================
 * app.js — Main Application Controller
 * Initializes all modules and manages panel/navigation state.
 * ================================================================ */

window.PortnetApp = window.PortnetApp || {};

PortnetApp.App = (function () {

    /**
     * Initialize the application — called on DOM ready.
     */
    function init() {
        // Display current user name
        $('#navUserName').text(PortnetApp.CURRENT_USER.name);

        // Initialize modules
        PortnetApp.ReclamationsList.init();
        PortnetApp.ReclamationDetail.init();
        PortnetApp.NewReclamation.init();

        // Bind panel events
        bindPanelEvents();
        bindMenuEvents();
    }

    // ── CENTRE D'AIDE PANEL ────────────────────────────────────

    function bindPanelEvents() {
        // Open panel
        $('#helpFloatingBtn').on('click', openPanel);

        // Close panel
        $('#panelCloseBtn').on('click', closePanel);
        $('#centreAideOverlay').on('click', closePanel);

        // Close reclamations section
        $('#sectionCloseBtn').on('click', function () {
            $('#mesReclamationsSection').removeClass('active');
        });

        // Escape key
        $(document).on('keydown', function (e) {
            if (e.key === 'Escape') {
                if ($('#newRecOverlay').hasClass('active')) {
                    PortnetApp.NewReclamation.close();
                } else if ($('#detailModalOverlay').hasClass('active')) {
                    PortnetApp.ReclamationDetail.close();
                } else if ($('#centreAidePanel').hasClass('active')) {
                    closePanel();
                }
            }
        });
    }

    function openPanel() {
        $('#centreAidePanel').addClass('active');
        $('#centreAideOverlay').addClass('active');
        $('#helpFloatingBtn').addClass('hidden');
    }

    function closePanel() {
        $('#centreAidePanel').removeClass('active');
        $('#centreAideOverlay').removeClass('active');
        $('#helpFloatingBtn').removeClass('hidden');
        // Close sub-sections
        $('#mesReclamationsSection').removeClass('active');
    }

    // ── MENU NAVIGATION ────────────────────────────────────────

    function bindMenuEvents() {
        $('.panel-menu-item').on('click', function () {
            var action = $(this).data('action');

            switch (action) {
                case 'mes-reclamations':
                    openMesReclamations();
                    break;

                case 'nouvelle-reclamation':
                    PortnetApp.NewReclamation.open();
                    break;

                case 'faq':
                    showToast('Foires aux questions — bientôt disponible');
                    break;

                case 'contact':
                    showToast('Contactez-nous — bientôt disponible');
                    break;

                case 'tijaria':
                    showToast('TijarIA — bientôt disponible');
                    break;

                case 'historique-tijaria':
                    showToast('Historique TijarIA — bientôt disponible');
                    break;
            }
        });
    }

    function openMesReclamations() {
        $('#mesReclamationsSection').addClass('active');
        PortnetApp.ReclamationsList.load();
    }

    // ── TOAST NOTIFICATION ─────────────────────────────────────

    function showToast(message) {
        var $toast = $('#toast');
        $toast.text(message).addClass('show');
        setTimeout(function () {
            $toast.removeClass('show');
        }, 3000);
    }

    // ── PUBLIC API ──────────────────────────────────────────────
    return {
        init: init,
        openPanel: openPanel,
        closePanel: closePanel,
        showToast: showToast
    };

})();

// ── Bootstrap on DOM ready ─────────────────────────────────────
$(document).ready(function () {
    PortnetApp.App.init();
});
