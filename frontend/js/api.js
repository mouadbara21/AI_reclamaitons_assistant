/* ================================================================
 * api.js — API Abstraction Layer
 * Currently uses mock data from data.js.
 * To integrate with real DB: update BASE_URL and replace mock
 * implementations with fetch() calls. This is the ONLY file
 * your binôme needs to modify for database integration.
 * ================================================================ */

window.PortnetApp = window.PortnetApp || {};

PortnetApp.API = (function () {

    // ── Configuration ────────────────────────────────────────────
    // Set this to your backend URL when ready (e.g. 'http://localhost:8080/api')
    var BASE_URL = '';

    // ── Helper: format date for display ──────────────────────────
    function formatDate(isoString) {
        if (!isoString) return '';
        var d = new Date(isoString);
        var day   = String(d.getDate()).padStart(2, '0');
        var month = String(d.getMonth() + 1).padStart(2, '0');
        var year  = d.getFullYear();
        var hours = String(d.getHours()).padStart(2, '0');
        var mins  = String(d.getMinutes()).padStart(2, '0');
        return day + '/' + month + '/' + year + ' ' + hours + ':' + mins;
    }

    // ── Helper: simulate async delay ─────────────────────────────
    function delay(ms) {
        return new Promise(function (resolve) { setTimeout(resolve, ms || 100); });
    }

    // ── Public API ───────────────────────────────────────────────

    /**
     * Fetch all reclamations for the current user, optionally filtered.
     * @param {string} [searchTerm] - Filter by reference or objet
     * @returns {Promise<Array>} sorted by date_creation desc
     */
    async function getReclamations(searchTerm) {
        await delay();
        var results = PortnetApp.mockReclamations.slice();

        if (searchTerm && searchTerm.trim() !== '') {
            var term = searchTerm.trim().toLowerCase();
            results = results.filter(function (r) {
                return r.reference.toLowerCase().indexOf(term) !== -1 ||
                       r.objet.toLowerCase().indexOf(term) !== -1;
            });
        }

        // Sort descending by date
        results.sort(function (a, b) {
            return new Date(b.date_creation) - new Date(a.date_creation);
        });

        return results;
    }

    /**
     * Fetch a single reclamation by ID.
     * @param {number} id
     * @returns {Promise<Object|null>}
     */
    async function getReclamationById(id) {
        await delay();
        return PortnetApp.mockReclamations.find(function (r) { return r.id === id; }) || null;
    }

    /**
     * Create a new reclamation.
     * @param {Object} data - { id_type_reclamation, id_service_reclamation, objet, description, files[] }
     * @returns {Promise<Object>} the created reclamation
     */
    async function createReclamation(data) {
        await delay(300);
        var maxId = Math.max.apply(null, PortnetApp.mockReclamations.map(function (r) { return r.id; }));
        var newId = maxId + 1;

        var newRec = {
            id: newId,
            date_creation: new Date().toISOString(),
            id_statut_reclamation: 1, // Always starts as "Affectée"
            id_service_reclamation: data.id_service_reclamation,
            objet: data.objet,
            description: data.description,
            created_by: PortnetApp.CURRENT_USER.id,
            response: null,
            id_type_reclamation: data.id_type_reclamation,
            reference: String(newId),
            id_odoo: 50000 + newId
        };

        PortnetApp.mockReclamations.unshift(newRec);

        // Create initial status history entry
        var maxHistId = Math.max.apply(null, PortnetApp.mockStatusHistory.map(function (h) { return h.id; }));
        PortnetApp.mockStatusHistory.push({
            id: maxHistId + 1,
            id_reclamation: newId,
            id_statut_avant: null,
            id_statut_apres: 1,
            commentaire: data.description,
            date_changement: newRec.date_creation,
            changed_by: PortnetApp.CURRENT_USER.id,
            reponse: null
        });

        // Handle file attachments
        if (data.files && data.files.length > 0) {
            var maxDocId = PortnetApp.mockDocuments.length > 0
                ? Math.max.apply(null, PortnetApp.mockDocuments.map(function (d) { return d.id; }))
                : 0;

            data.files.forEach(function (file, i) {
                PortnetApp.mockDocuments.push({
                    id: maxDocId + i + 1,
                    id_reclamation: newId,
                    document_guid: 'guid-new-' + (maxDocId + i + 1),
                    document_name: file.name,
                    date_upload: newRec.date_creation
                });
            });
        }

        return newRec;
    }

    /**
     * Get status change history for a reclamation.
     * @param {number} reclamationId
     * @returns {Promise<Array>} sorted by date_changement asc
     */
    async function getStatusHistory(reclamationId) {
        await delay();
        var results = PortnetApp.mockStatusHistory.filter(function (h) {
            return h.id_reclamation === reclamationId;
        });
        results.sort(function (a, b) {
            return new Date(a.date_changement) - new Date(b.date_changement);
        });
        return results;
    }

    /**
     * Get documents attached to a reclamation.
     * @param {number} reclamationId
     * @returns {Promise<Array>}
     */
    async function getDocuments(reclamationId) {
        await delay();
        return PortnetApp.mockDocuments.filter(function (d) {
            return d.id_reclamation === reclamationId;
        });
    }

    /**
     * Get documents attached to a specific status history entry.
     * @param {number} statusHistoryId
     * @returns {Promise<Array>}
     */
    async function getStatusDocuments(statusHistoryId) {
        await delay();
        return PortnetApp.mockStatusDocuments.filter(function (d) {
            return d.id_status_history === statusHistoryId;
        });
    }

    // ── Lookup helpers ───────────────────────────────────────────

    function getStatut(id) {
        return PortnetApp.STATUTS[id] || { label: 'Inconnu', color: '#999', bgColor: '#f5f5f5', borderColor: '#ddd' };
    }

    function getTypeDemande(id) {
        return PortnetApp.TYPES_DEMANDE[id] || { label: 'Inconnu' };
    }

    function getService(id) {
        return PortnetApp.SERVICES.find(function (s) { return s.id === id; }) || { label: 'Inconnu' };
    }

    function getAllServices() {
        return PortnetApp.SERVICES.slice();
    }

    function getAllTypes() {
        return Object.keys(PortnetApp.TYPES_DEMANDE).map(function (k) {
            return PortnetApp.TYPES_DEMANDE[k];
        });
    }

    function getUserName(userId) {
        var u = PortnetApp.USERS[userId];
        return u ? u.name : 'Utilisateur #' + userId;
    }

    // ── Expose public methods ────────────────────────────────────
    return {
        formatDate: formatDate,
        getReclamations: getReclamations,
        getReclamationById: getReclamationById,
        createReclamation: createReclamation,
        getStatusHistory: getStatusHistory,
        getDocuments: getDocuments,
        getStatusDocuments: getStatusDocuments,
        getStatut: getStatut,
        getTypeDemande: getTypeDemande,
        getService: getService,
        getAllServices: getAllServices,
        getAllTypes: getAllTypes,
        getUserName: getUserName
    };

})();
