/**
 * PortNet Souscription — Result Page Logic
 *
 * Fetches the validation report from /api/souscription/result/{id}
 * and renders the outcome with document details, cross-reference checks,
 * and rejection/warning reasons.
 */

(function () {
    'use strict';

    // ─── Status configuration ────────────────────────────────────
    var STATUS_CONFIG = {
        'VALID': {
            cssClass: 'valid',
            icon: 'fa-check',
            title: 'Votre demande de souscription a été validée',
            message: 'Félicitations ! Tous les documents ont été vérifiés avec succès. Votre souscription sera activée dans les prochaines 24 à 48 heures.',
        },
        'WARNING': {
            cssClass: 'warning',
            icon: 'fa-exclamation-triangle',
            title: 'Votre demande nécessite une vérification complémentaire',
            message: 'Des écarts mineurs ont été détectés dans vos documents. Un agent du service réclamation examinera votre dossier et vous contactera si nécessaire.',
        },
        'INVALID': {
            cssClass: 'invalid',
            icon: 'fa-times',
            title: 'Votre demande a été rejetée',
            message: 'Des anomalies critiques ont été détectées dans vos documents. Veuillez corriger les erreurs indiquées ci-dessous et soumettre à nouveau votre dossier.',
        },
    };

    // ─── DOM Ready ───────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', function () {
        var urlParams = new URLSearchParams(window.location.search);
        var souscriptionId = urlParams.get('id');

        if (!souscriptionId) {
            showError('Aucun identifiant de souscription trouvé dans l\'URL.');
            return;
        }

        fetchResult(souscriptionId);
    });

    // ─── Fetch Result ────────────────────────────────────────────
    function fetchResult(id) {
        fetch('/api/souscription/result/' + id)
            .then(function (response) {
                if (!response.ok) throw new Error('Souscription introuvable');
                return response.json();
            })
            .then(function (data) {
                renderResult(data);
            })
            .catch(function (err) {
                showError(err.message);
            });
    }

    // ─── Render Result ───────────────────────────────────────────
    function renderResult(data) {
        var container = document.getElementById('resultContent');
        var report = data.validation_report || {};
        var overallStatus = data.overall_status || report.overall_status || 'INVALID';
        var config = STATUS_CONFIG[overallStatus] || STATUS_CONFIG['INVALID'];

        var html = '';

        // 1. Status Hero
        html += '<div class="result-hero">';
        html += '  <div class="result-status-circle ' + config.cssClass + '">';
        html += '    <i class="fas ' + config.icon + '"></i>';
        html += '  </div>';
        html += '  <h2>' + config.title + '</h2>';
        html += '  <p>' + config.message + '</p>';
        html += '</div>';

        // 2. Souscription Info
        html += '<div class="result-section">';
        html += '  <div class="result-section-header">';
        html += '    <span class="legend-icon"><i class="fas fa-building"></i></span>';
        html += '    Informations de la souscription';
        html += '  </div>';
        html += '  <div style="padding:16px 20px;">';
        html += '    <table class="result-checks-table">';
        html += '      <tr><td style="font-weight:600; width:180px;">Raison Sociale</td><td>' + esc(data.raison_sociale) + '</td></tr>';
        html += '      <tr><td style="font-weight:600;">ICE</td><td>' + esc(data.ice) + '</td></tr>';
        html += '      <tr><td style="font-weight:600;">RC</td><td>' + esc(data.rc_number) + ' / ' + esc(data.rc_city) + '</td></tr>';
        html += '      <tr><td style="font-weight:600;">IF</td><td>' + esc(data.if_number) + '</td></tr>';
        html += '      <tr><td style="font-weight:600;">TP</td><td>' + esc(data.tp_number) + '</td></tr>';
        html += '      <tr><td style="font-weight:600;">Gérant</td><td>' + esc(data.gerant_prenom) + ' ' + esc(data.gerant_nom) + ' (CIN: ' + esc(data.gerant_cin) + ')</td></tr>';
        html += '      <tr><td style="font-weight:600;">Date</td><td>' + formatDate(data.created_at) + '</td></tr>';
        html += '      <tr><td style="font-weight:600;">ID Souscription</td><td style="font-family:monospace; font-size:12px;">' + esc(data.id) + '</td></tr>';
        html += '    </table>';
        html += '  </div>';
        html += '</div>';

        // 3. Rejection reasons (only for INVALID)
        var rejectionReasons = data.rejection_reasons || report.rejection_reasons || [];
        if (rejectionReasons.length > 0 && overallStatus === 'INVALID') {
            html += '<div class="result-reasons">';
            html += '  <h3><i class="fas fa-exclamation-circle"></i> Motifs de rejet</h3>';
            html += '  <ul>';
            rejectionReasons.forEach(function (reason) {
                html += '    <li>' + esc(cleanGuidInText(reason, data.documents)) + '</li>';
            });
            html += '  </ul>';
            html += '</div>';
        }

        // 4. Warning reasons (for WARNING status)
        if (rejectionReasons.length > 0 && overallStatus === 'WARNING') {
            html += '<div class="result-warnings">';
            html += '  <h3><i class="fas fa-exclamation-triangle"></i> Points d\'attention</h3>';
            html += '  <ul>';
            rejectionReasons.forEach(function (reason) {
                html += '    <li>' + esc(cleanGuidInText(reason, data.documents)) + '</li>';
            });
            html += '  </ul>';
            html += '</div>';
        }

        // 5. Document Reports (accordion)
        var docReports = report.document_reports || [];
        if (docReports.length > 0) {
            html += '<div class="result-section">';
            html += '  <div class="result-section-header">';
            html += '    <span class="legend-icon"><i class="fas fa-file-alt"></i></span>';
            html += '    Détail des vérifications par document';
            html += '  </div>';

            docReports.forEach(function (doc, idx) {
                var docStatus = doc.status || 'INVALID';
                var statusClass = docStatus.toLowerCase();
                var statusLabel = docStatus === 'VALID' ? 'Conforme' : (docStatus === 'WARNING' ? 'Attention' : 'Non conforme');
                var statusIcon = docStatus === 'VALID' ? 'fa-check' : (docStatus === 'WARNING' ? 'fa-exclamation-triangle' : 'fa-times');

                html += '<div class="result-doc-item">';
                html += '  <div class="result-doc-header" onclick="toggleDocDetail(' + idx + ')">';
                html += '    <div class="result-doc-info">';
                html += '      <i class="fas fa-file-pdf" style="color:#dc3545; font-size:18px;"></i>';
                html += '      <div>';
                html += '        <div class="result-doc-name">' + esc(cleanGuidInText(doc.document_name, data.documents)) + '</div>';
                html += '        <div class="result-doc-type">' + esc(doc.document_type) + '</div>';
                html += '      </div>';
                html += '    </div>';
                html += '    <div style="display:flex; align-items:center; gap:8px;">';
                html += '      <span class="result-status-tag ' + statusClass + '">';
                html += '        <i class="fas ' + statusIcon + '"></i> ' + statusLabel;
                html += '      </span>';
                html += '      <i class="fas fa-chevron-down" style="color:#6c757d; font-size:12px;"></i>';
                html += '    </div>';
                html += '  </div>';

                // Detail content
                html += '  <div class="result-doc-details" id="docDetail-' + idx + '">';

                if (doc.message) {
                    html += '    <p style="font-size:13px; color:#6c757d; margin:0 0 12px;">' + esc(cleanGuidInText(doc.message, data.documents)) + '</p>';
                }

                var checks = doc.local_checks || [];
                if (checks.length > 0) {
                    html += '    <table class="result-checks-table">';
                    html += '      <thead><tr>';
                    html += '        <th>Vérification</th>';
                    html += '        <th>Attendu</th>';
                    html += '        <th>Extrait</th>';
                    html += '        <th>Statut</th>';
                    html += '      </tr></thead>';
                    html += '      <tbody>';

                    checks.forEach(function (check) {
                        var cs = (check.status || '').toLowerCase();
                        var cIcon = cs === 'valid' ? 'fa-check-circle' : (cs === 'warning' ? 'fa-exclamation-triangle' : 'fa-times-circle');
                        var cColor = cs === 'valid' ? '#28a745' : (cs === 'warning' ? '#fd7e14' : '#dc3545');

                        html += '      <tr>';
                        html += '        <td style="font-weight:500;">' + esc(check.field_name) + '</td>';
                        html += '        <td>' + esc(check.expected_value) + '</td>';
                        html += '        <td style="font-family:monospace; font-size:12px;">' + esc(check.extracted_value) + '</td>';
                        html += '        <td>';
                        html += '          <i class="fas ' + cIcon + '" style="color:' + cColor + '"></i> ';
                        html += '          <span style="font-size:12px; color:' + cColor + '">' + esc(cleanGuidInText(check.message || '', data.documents)) + '</span>';
                        html += '        </td>';
                        html += '      </tr>';
                    });

                    html += '      </tbody>';
                    html += '    </table>';
                } else if (!doc.message) {
                    html += '    <p style="font-size:13px; color:#6c757d; margin:0;">Aucune vérification locale applicable.</p>';
                }

                html += '  </div>';
                html += '</div>';
            });

            html += '</div>';
        }

        // 6. Cross-Reference Report
        var crossRef = report.cross_reference_report || {};
        var crossChecks = crossRef.checks || [];
        if (crossChecks.length > 0) {
            html += '<div class="result-section result-cross-ref">';
            html += '  <div class="result-section-header">';
            html += '    <span class="legend-icon"><i class="fas fa-project-diagram"></i></span>';
            html += '    Matrice de cohérence croisée';
            html += '  </div>';
            html += '  <div style="padding:16px 20px;">';
            html += '    <table class="result-checks-table">';
            html += '      <thead><tr>';
            html += '        <th>Champ</th>';
            html += '        <th>Valeur formulaire</th>';
            html += '        <th>Valeur document</th>';
            html += '        <th>Résultat</th>';
            html += '      </tr></thead>';
            html += '      <tbody>';

            crossChecks.forEach(function (check) {
                var cs = (check.status || '').toLowerCase();
                var cIcon = cs === 'valid' ? 'fa-check-circle' : (cs === 'warning' ? 'fa-exclamation-triangle' : 'fa-times-circle');
                var cColor = cs === 'valid' ? '#28a745' : (cs === 'warning' ? '#fd7e14' : '#dc3545');
                var scoreStr = check.score !== null && check.score !== undefined ? ' (' + check.score.toFixed(1) + '%)' : '';

                html += '      <tr>';
                html += '        <td style="font-weight:500;">' + esc(check.field_name) + '</td>';
                html += '        <td style="font-size:12px;">' + esc(check.expected_value) + '</td>';
                html += '        <td style="font-family:monospace; font-size:12px;">' + esc(check.extracted_value) + '</td>';
                html += '        <td>';
                html += '          <i class="fas ' + cIcon + '" style="color:' + cColor + '"></i> ';
                html += '          <span style="font-size:12px; color:' + cColor + '">' + esc(cleanGuidInText(check.message || '', data.documents)) + scoreStr + '</span>';
                html += '        </td>';
                html += '      </tr>';
            });

            html += '      </tbody>';
            html += '    </table>';
            html += '  </div>';
            html += '</div>';
        }

        // 7. Uploaded Documents (GUID listing)
        var uploadedDocs = data.documents || [];
        if (uploadedDocs.length > 0) {
            html += '<div class="result-section">';
            html += '  <div class="result-section-header">';
            html += '    <span class="legend-icon"><i class="fas fa-database"></i></span>';
            html += '    Documents stockés (GUIDs)';
            html += '  </div>';
            html += '  <div style="padding:16px 20px;">';
            html += '    <table class="result-checks-table">';
            html += '      <thead><tr>';
            html += '        <th>Fichier original</th>';
            html += '        <th>Emplacement</th>';
            html += '        <th>GUID</th>';
            html += '        <th>Taille</th>';
            html += '      </tr></thead>';
            html += '      <tbody>';

            uploadedDocs.forEach(function (doc) {
                html += '      <tr>';
                html += '        <td>' + esc(doc.original_filename) + '</td>';
                html += '        <td>' + esc(doc.document_slot) + '</td>';
                html += '        <td style="font-family:monospace; font-size:11px;">' + esc(doc.guid) + '</td>';
                html += '        <td>' + formatSize(doc.file_size_bytes) + '</td>';
                html += '      </tr>';
            });

            html += '      </tbody>';
            html += '    </table>';
            html += '  </div>';
            html += '</div>';
        }

        // 8. Action buttons
        html += '<div class="result-actions">';
        if (overallStatus === 'INVALID') {
            html += '  <a href="/souscription.html" class="sousc-btn sousc-btn-submit">';
            html += '    <i class="fas fa-redo"></i> Corriger et re-soumettre';
            html += '  </a>';
        }
        html += '  <a href="/" class="sousc-btn sousc-btn-prev">';
        html += '    <i class="fas fa-home"></i> Retour à l\'accueil';
        html += '  </a>';
        html += '</div>';

        container.innerHTML = html;
    }

    // ─── Error display ───────────────────────────────────────────
    function showError(message) {
        var container = document.getElementById('resultContent');
        container.innerHTML =
            '<div style="text-align:center; padding:60px 20px;">' +
            '  <div class="result-status-circle invalid">' +
            '    <i class="fas fa-exclamation-triangle"></i>' +
            '  </div>' +
            '  <h2 style="font-size:18px; margin:20px 0 8px;">' + esc(message) + '</h2>' +
            '  <p style="color:#6c757d;">Vérifiez l\'URL ou retournez à la page de souscription.</p>' +
            '  <a href="/souscription.html" class="sousc-btn sousc-btn-submit" style="margin-top:20px; display:inline-flex;">' +
            '    <i class="fas fa-arrow-left"></i> Retour à la souscription' +
            '  </a>' +
            '</div>';
    }

    // ─── Utility functions ───────────────────────────────────────
    function cleanGuidInText(str, docs) {
        if (!str) return '';
        var res = String(str);
        if (docs && docs.length) {
            docs.forEach(function (d) {
                if (d.guid) {
                    var orig = d.original_filename || d.document_slot || 'document';
                    res = res.split(d.guid + '.pdf').join(orig);
                    res = res.split(d.guid).join(orig);
                }
            });
        }
        return res.replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.pdf/gi, 'document');
    }

    function esc(str) {
        if (str === null || str === undefined) return '';
        var div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }

    function formatDate(isoStr) {
        if (!isoStr) return '-';
        try {
            var d = new Date(isoStr);
            var day = String(d.getDate()).padStart(2, '0');
            var month = String(d.getMonth() + 1).padStart(2, '0');
            var year = d.getFullYear();
            var hours = String(d.getHours()).padStart(2, '0');
            var mins = String(d.getMinutes()).padStart(2, '0');
            return day + '/' + month + '/' + year + ' ' + hours + ':' + mins;
        } catch (e) {
            return isoStr;
        }
    }

    function formatSize(bytes) {
        if (!bytes) return '-';
        if (bytes < 1024) return bytes + ' o';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' Ko';
        return (bytes / (1024 * 1024)).toFixed(2) + ' Mo';
    }

    // ─── Global function for accordion toggle ────────────────────
    window.toggleDocDetail = function (idx) {
        var detail = document.getElementById('docDetail-' + idx);
        if (detail) {
            detail.classList.toggle('open');
        }
    };

})();
