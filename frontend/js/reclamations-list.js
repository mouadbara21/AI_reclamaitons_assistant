/* ================================================================
 * reclamations-list.js — "Mes réclamations" list renderer
 * Handles rendering reclamation cards, search, and count display.
 * ================================================================ */

window.PortnetApp = window.PortnetApp || {};

PortnetApp.ReclamationsList = (function () {

    var $list = null;
    var $count = null;
    var $searchInput = null;
    var currentData = [];

    /**
     * Initialize the module — call once after DOM ready.
     */
    function init() {
        $list = $('#reclamationsList');
        $count = $('#reclamationsCount');
        $searchInput = $('#searchInput');

        // Search events
        $('#searchBtn').on('click', function () {
            performSearch();
        });

        $searchInput.on('keypress', function (e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }

    /**
     * Load and render all reclamations.
     */
    async function load() {
        $list.html('<div class="spinner"></div>');

        var data = await PortnetApp.API.getReclamations();
        currentData = data;
        render(data);
    }

    /**
     * Perform search and update list.
     */
    async function performSearch() {
        var term = $searchInput.val();
        $list.html('<div class="spinner"></div>');

        var data = await PortnetApp.API.getReclamations(term);
        currentData = data;
        render(data);
    }

    /**
     * Render the reclamation cards.
     * @param {Array} reclamations
     */
    function render(reclamations) {
        $count.text(reclamations.length + ' réclamation(s)');

        if (reclamations.length === 0) {
            $list.html(
                '<div class="empty-state">' +
                    '<i class="fas fa-inbox"></i>' +
                    '<p>Aucune réclamation trouvée</p>' +
                '</div>'
            );
            return;
        }

        var html = '';
        reclamations.forEach(function (rec) {
            var statut = PortnetApp.API.getStatut(rec.id_statut_reclamation);
            var dateFormatted = PortnetApp.API.formatDate(rec.date_creation);

            html += '<div class="reclamation-card" data-id="' + rec.id + '">';
            html +=   '<div class="card-top-row">';
            html +=     '<span class="card-reference" data-id="' + rec.id + '">' + rec.reference + '</span>';
            html +=     '<span class="status-badge ' + statut.key + '">' + statut.label + '</span>';
            html +=   '</div>';
            html +=   '<div class="card-objet">' + escapeHtml(rec.objet) + '</div>';
            html +=   '<div class="card-bottom-row">';
            html +=     '<span class="card-date">' + dateFormatted + '</span>';
            html +=     '<span class="card-details-link" data-id="' + rec.id + '">Voir détails <i class="fas fa-eye"></i></span>';
            html +=   '</div>';
            html += '</div>';
        });

        $list.html(html);

        // Bind click events on cards
        $list.find('.card-details-link, .card-reference').on('click', function () {
            var id = parseInt($(this).data('id'));
            PortnetApp.ReclamationDetail.open(id);
        });
    }

    /**
     * Escape HTML to prevent XSS.
     */
    function escapeHtml(text) {
        if (!text) return '';
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    return {
        init: init,
        load: load,
        performSearch: performSearch
    };

})();
