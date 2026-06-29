/* ================================================================
 * reclamation-detail.js — Detail modal with status timeline
 * Opens the "Détails de la réclamation" modal for a given ID.
 * ================================================================ */

window.PortnetApp = window.PortnetApp || {};

PortnetApp.ReclamationDetail = (function () {

    var $overlay = null;
    var $body = null;
    var $ref = null;
    var $badge = null;

    /**
     * Initialize — bind close events.
     */
    function init() {
        $overlay = $('#detailModalOverlay');
        $body    = $('#detailBody');
        $ref     = $('#detailRef');
        $badge   = $('#detailStatusBadge');

        $('#detailCloseBtn').on('click', close);
        $overlay.on('click', function (e) {
            if (e.target === $overlay[0]) close();
        });

        $(document).on('keydown', function (e) {
            if (e.key === 'Escape' && $overlay.hasClass('active')) close();
        });
    }

    /**
     * Open the detail modal for a specific reclamation.
     * @param {number} id
     */
    async function open(id) {
        $body.html('<div class="spinner"></div>');
        $ref.text('');
        $badge.text('').attr('class', 'status-badge');

        $overlay.addClass('active');

        // Fetch data in parallel
        var recPromise      = PortnetApp.API.getReclamationById(id);
        var historyPromise  = PortnetApp.API.getStatusHistory(id);
        var docsPromise     = PortnetApp.API.getDocuments(id);

        var rec     = await recPromise;
        var history = await historyPromise;
        var docs    = await docsPromise;

        if (!rec) {
            $body.html('<div class="empty-state"><p>Réclamation introuvable</p></div>');
            return;
        }

        // Update header
        var statut = PortnetApp.API.getStatut(rec.id_statut_reclamation);
        $ref.text(rec.reference);
        $badge.text(statut.label).attr('class', 'status-badge ' + statut.key);

        // Build body HTML
        var html = '';

        // Type de demande
        html += buildField('Type de demande', PortnetApp.API.getTypeDemande(rec.id_type_reclamation).label);

        // Service concerné
        html += buildField('Service concerné', PortnetApp.API.getService(rec.id_service_reclamation).label);

        // Référence
        html += buildField('Référence', rec.reference);

        // Objet
        html += buildField('Objet', rec.objet);

        // Description
        html += '<div class="detail-field">';
        html +=   '<div class="detail-field-label">Description</div>';
        html +=   '<div class="detail-description-box">' + escapeHtml(rec.description) + '</div>';
        html += '</div>';

        // Date de création
        html += buildField('Date de création', PortnetApp.API.formatDate(rec.date_creation));

        // Pièces jointes
        if (docs.length > 0) {
            html += '<div class="detail-attachments-title">Pièces jointes (' + docs.length + ')</div>';
            docs.forEach(function (doc) {
                html += buildAttachment(doc.document_name, doc.date_upload);
            });
        }

        // Status history timeline
        if (history.length > 0) {
            html += '<div class="timeline-title">Historique des statuts</div>';
            html += '<div class="timeline">';

            for (var i = 0; i < history.length; i++) {
                var entry = history[i];
                html += await buildTimelineEntry(entry, i === 0);
            }

            html += '</div>'; // .timeline
        }

        $body.html(html);
    }

    /**
     * Build a simple field row.
     */
    function buildField(label, value) {
        return '<div class="detail-field">' +
                   '<div class="detail-field-label">' + label + '</div>' +
                   '<div class="detail-field-value">' + escapeHtml(value) + '</div>' +
               '</div>';
    }

    /**
     * Build an attachment row.
     */
    function buildAttachment(name, dateStr) {
        var date = dateStr ? 'Ajouté le ' + PortnetApp.API.formatDate(dateStr) : '';
        return '<div class="attachment-item">' +
                   '<i class="fas fa-paperclip attachment-icon"></i>' +
                   '<div class="attachment-info">' +
                       '<div class="attachment-name">' + escapeHtml(name) + '</div>' +
                       '<div class="attachment-date">' + date + '</div>' +
                   '</div>' +
                   '<i class="fas fa-download attachment-download" title="Télécharger"></i>' +
               '</div>';
    }

    /**
     * Build a single timeline entry.
     * @param {Object} entry - status history record
     * @param {boolean} isFirst - whether it's the initial status
     */
    async function buildTimelineEntry(entry, isFirst) {
        var statutApres = PortnetApp.API.getStatut(entry.id_statut_apres);
        var statusClass = 'status-' + statutApres.key;
        var labelClass  = statutApres.key;

        // Build the status transition label
        var labelHtml = '';
        if (isFirst || entry.id_statut_avant === null) {
            // Initial status
            labelHtml = '<i class="fas fa-clipboard-list"></i> ' + statutApres.label;
        } else {
            // Transition
            var statutAvant = PortnetApp.API.getStatut(entry.id_statut_avant);
            labelHtml = '<i class="fas fa-clipboard-list"></i> ' +
                        statutAvant.label + ' → ' + statutApres.label;
        }

        var userName = PortnetApp.API.getUserName(entry.changed_by);
        var dateFormatted = PortnetApp.API.formatDate(entry.date_changement);

        var html = '<div class="timeline-entry ' + statusClass + '">';
        html += '<div class="timeline-dot"></div>';
        html += '<div class="timeline-status-label ' + labelClass + '">' + labelHtml + '</div>';
        html += '<div class="timeline-meta">' + escapeHtml(userName) + ' · ' + dateFormatted + '</div>';

        // Comment / message box
        if (entry.commentaire) {
            html += '<div class="timeline-message-box">' + escapeHtml(entry.commentaire) + '</div>';
        }

        // Response box (from CRC / Odoo)
        if (entry.reponse) {
            html += '<div class="timeline-response-box">';
            html +=   '<div class="timeline-response-label"><i class="fas fa-comment-dots"></i> Réponse</div>';
            html +=   '<div class="timeline-response-text">' + escapeHtml(entry.reponse) + '</div>';
            html += '</div>';
        }

        // Status documents
        var statusDocs = await PortnetApp.API.getStatusDocuments(entry.id);
        if (statusDocs.length > 0) {
            statusDocs.forEach(function (doc) {
                html += '<div class="timeline-attachment">';
                html +=   '<i class="fas fa-paperclip"></i>';
                html +=   '<span class="att-name">' + escapeHtml(doc.document_name) + '</span>';
                html +=   '<i class="fas fa-download att-download" title="Télécharger"></i>';
                html += '</div>';
            });
        }

        html += '</div>'; // .timeline-entry
        return html;
    }

    /**
     * Close the modal.
     */
    function close() {
        $overlay.removeClass('active');
    }

    /**
     * Escape HTML.
     */
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
