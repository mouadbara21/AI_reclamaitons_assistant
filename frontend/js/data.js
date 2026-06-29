/* ================================================================
 * data.js — Mock Data Layer
 * Mirrors the Oracle PMPCE database schema exactly.
 * Replace with real API calls in api.js when integrating with DB.
 * ================================================================ */

window.PortnetApp = window.PortnetApp || {};

/* ----- Lookup Tables (Reference Data) ----- */

PortnetApp.STATUTS = {
    1: { id: 1, key: 'affectee',  label: 'Affectée',  color: '#64748B', bgColor: '#F1F5F9', borderColor: '#CBD5E1' },
    2: { id: 2, key: 'repondue',  label: 'Répondue',  color: '#059669', bgColor: '#ECFDF5', borderColor: '#A7F3D0' },
    3: { id: 3, key: 'cloturee',  label: 'Clôturée',  color: '#64748B', bgColor: '#F1F5F9', borderColor: '#CBD5E1' },
    4: { id: 4, key: 'reouverte', label: 'Réouverte', color: '#DC2626', bgColor: '#FEF2F2', borderColor: '#FECACA' }
};

PortnetApp.TYPES_DEMANDE = {
    1: { id: 1, label: "Besoin d'informations" },
    2: { id: 2, label: 'Réclamation' },
    3: { id: 3, label: 'Signaler un incident technique' }
};

PortnetApp.SERVICES = [
    { id: 1,  label: 'Certificats de conformité' },
    { id: 2,  label: "Titres d'import" },
    { id: 3,  label: 'Franchises douanières' },
    { id: 4,  label: 'Import — Équipements télécoms' },
    { id: 5,  label: 'Cautions bancaires' },
    { id: 6,  label: 'Admis pour conforme (annuel)' },
    { id: 7,  label: 'Déclarations Douanières' },
    { id: 8,  label: 'Services CCS' },
    { id: 9,  label: 'Services PCS' },
    { id: 10, label: 'Procurations' },
    { id: 11, label: 'Récépissé import — Céréales & légumineuses' },
    { id: 12, label: 'Import — Instruments de mesure' },
    { id: 13, label: 'Homologation — Instruments de mesure' },
    { id: 14, label: 'Permis CITES' },
    { id: 15, label: 'Import — Sources radioactives' }
];

PortnetApp.USERS = {
    1001: { id: 1001, name: 'imp rachidi',        role: 'client'  },
    2001: { id: 2001, name: 'Maryam OUAFIK',      role: 'client'  },
    3001: { id: 3001, name: 'Service Odoo',        role: 'system'  },
    4001: { id: 4001, name: 'Demo Importateur',    role: 'client'  }
};

PortnetApp.CURRENT_USER = PortnetApp.USERS[4001];

/* ----- PMPCE_RECLAMATION -----
 * Columns: ID, DATE_CREATION, ID_STATUT_RECLAMATION,
 *          ID_SERVICE_RECLAMATION, OBJET, DESCRIPTION,
 *          CREATED_BY, RESPONSE, ID_TYPE_RECLAMATION,
 *          REFERENCE, ID_ODOO
 * ----- */

PortnetApp.mockReclamations = [
    {
        id: 20920,
        date_creation: '2026-06-23T12:03:00',
        id_statut_reclamation: 3,
        id_service_reclamation: 1,
        objet: 'test',
        description: 'Test de réclamation pour vérification du système.',
        created_by: 4001,
        response: 'Votre demande a été traitée avec succès.',
        id_type_reclamation: 2,
        reference: '20920',
        id_odoo: 50920
    },
    {
        id: 20919,
        date_creation: '2026-06-23T11:35:00',
        id_statut_reclamation: 3,
        id_service_reclamation: 2,
        objet: 'test',
        description: 'Deuxième test de réclamation.',
        created_by: 4001,
        response: 'Traité.',
        id_type_reclamation: 1,
        reference: '20919',
        id_odoo: 50919
    },
    {
        id: 20918,
        date_creation: '2026-06-23T10:15:00',
        id_statut_reclamation: 1,
        id_service_reclamation: 8,
        objet: "Problème d'accès au service CCS",
        description: "Impossible d'accéder au service CCS depuis ce matin. Le message d'erreur indique 'Session expirée' même après reconnexion.",
        created_by: 4001,
        response: null,
        id_type_reclamation: 3,
        reference: '20918',
        id_odoo: 50918
    },
    {
        id: 20914,
        date_creation: '2026-06-22T16:40:00',
        id_statut_reclamation: 3,
        id_service_reclamation: 3,
        objet: 'DEUXIEME',
        description: 'DEUXIEME réclamation de test.',
        created_by: 2001,
        response: 'ok',
        id_type_reclamation: 2,
        reference: '20914',
        id_odoo: 50914
    },
    {
        id: 20913,
        date_creation: '2026-06-22T16:40:00',
        id_statut_reclamation: 1,
        id_service_reclamation: 5,
        objet: 'okkkkkkkkkkk',
        description: 'Test réclamation cautions bancaires.',
        created_by: 2001,
        response: null,
        id_type_reclamation: 2,
        reference: '20913',
        id_odoo: 50913
    },
    {
        id: 20912,
        date_creation: '2026-06-22T16:34:00',
        id_statut_reclamation: 3,
        id_service_reclamation: 7,
        objet: 'TEST APREM ODOO',
        description: 'Test de synchronisation Odoo après-midi.',
        created_by: 4001,
        response: 'Synchronisation vérifiée et fonctionnelle.',
        id_type_reclamation: 2,
        reference: '20912',
        id_odoo: 50912
    },
    {
        id: 20910,
        date_creation: '2026-06-21T09:30:00',
        id_statut_reclamation: 2,
        id_service_reclamation: 1,
        objet: 'Retard certificat de conformité',
        description: 'Mon certificat de conformité est en retard de 2 semaines. Référence dossier: CF-2026-4521. Cela bloque mes opérations d\'import.',
        created_by: 4001,
        response: 'Votre certificat est en cours de traitement prioritaire.',
        id_type_reclamation: 2,
        reference: '20910',
        id_odoo: 50910
    },
    {
        id: 20908,
        date_creation: '2026-06-20T14:22:00',
        id_statut_reclamation: 4,
        id_service_reclamation: 7,
        objet: 'Erreur dans la déclaration douanière',
        description: 'Il y a une erreur dans ma déclaration douanière numéro DD-2026-7890. Le montant déclaré est incorrect et ne correspond pas à la facture commerciale.',
        created_by: 4001,
        response: null,
        id_type_reclamation: 2,
        reference: '20908',
        id_odoo: 50908
    },
    {
        id: 20905,
        date_creation: '2026-06-19T11:00:00',
        id_statut_reclamation: 3,
        id_service_reclamation: 2,
        objet: "Demande de renseignements import",
        description: "Je souhaite obtenir des informations sur la procédure d'obtention d'un titre d'import pour des équipements industriels.",
        created_by: 4001,
        response: "Les titres d'import pour équipements industriels nécessitent le formulaire TI-2026. Veuillez consulter la rubrique Titres d'import.",
        id_type_reclamation: 1,
        reference: '20905',
        id_odoo: 50905
    },
    {
        id: 20885,
        date_creation: '2026-06-14T14:32:00',
        id_statut_reclamation: 1,
        id_service_reclamation: 1,
        objet: 'test objet',
        description: 'test desc',
        created_by: 1001,
        response: null,
        id_type_reclamation: 2,
        reference: '20885',
        id_odoo: 50885
    }
];

/* ----- PMPCE_RECLAMATION_DOCUMENT -----
 * Columns: ID, ID_RECLAMATION, DOCUMENT_GUID, DOCUMENT_NAME, DATE_UPLOAD
 * ----- */

PortnetApp.mockDocuments = [
    {
        id: 1,
        id_reclamation: 20885,
        document_guid: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        document_name: 'sampleTest2.pdf',
        date_upload: '2026-06-14T14:32:00'
    },
    {
        id: 2,
        id_reclamation: 20908,
        document_guid: 'b2c3d4e5-f6a7-8901-bcde-f12345678901',
        document_name: 'facture_commerciale.pdf',
        date_upload: '2026-06-20T14:22:00'
    },
    {
        id: 3,
        id_reclamation: 20910,
        document_guid: 'c3d4e5f6-a7b8-9012-cdef-123456789012',
        document_name: 'dossier_CF-2026-4521.pdf',
        date_upload: '2026-06-21T09:30:00'
    }
];

/* ----- PMPCE_RECLAMATION_STATUS_HISTORY -----
 * Columns: ID, ID_RECLAMATION, ID_STATUT_AVANT, ID_STATUT_APRES,
 *          COMMENTAIRE, DATE_CHANGEMENT, CHANGED_BY, REPONSE
 * ----- */

PortnetApp.mockStatusHistory = [
    // --- Reclamation #20914 (full lifecycle shown in screenshot 8) ---
    {
        id: 1,
        id_reclamation: 20914,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'DEUXIEME',
        date_changement: '2026-06-22T16:40:00',
        changed_by: 2001,
        reponse: null
    },
    {
        id: 2,
        id_reclamation: 20914,
        id_statut_avant: 1,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-22T16:41:00',
        changed_by: 3001,
        reponse: 'ok'
    },
    {
        id: 3,
        id_reclamation: 20914,
        id_statut_avant: 2,
        id_statut_apres: 4,
        commentaire: 'REOUVERT',
        date_changement: '2026-06-22T16:42:00',
        changed_by: 2001,
        reponse: null
    },
    {
        id: 4,
        id_reclamation: 20914,
        id_statut_avant: 4,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-22T16:43:00',
        changed_by: 3001,
        reponse: 'ok'
    },
    {
        id: 5,
        id_reclamation: 20914,
        id_statut_avant: 2,
        id_statut_apres: 3,
        commentaire: null,
        date_changement: '2026-06-22T16:45:00',
        changed_by: 2001,
        reponse: null
    },

    // --- Reclamation #20885 (shown in detail screenshots 2-3) ---
    {
        id: 6,
        id_reclamation: 20885,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'test desc',
        date_changement: '2026-06-14T14:32:00',
        changed_by: 1001,
        reponse: null
    },

    // --- Reclamation #20910 (Répondue) ---
    {
        id: 7,
        id_reclamation: 20910,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'Mon certificat de conformité est en retard de 2 semaines. Référence dossier: CF-2026-4521.',
        date_changement: '2026-06-21T09:30:00',
        changed_by: 4001,
        reponse: null
    },
    {
        id: 8,
        id_reclamation: 20910,
        id_statut_avant: 1,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-21T11:15:00',
        changed_by: 3001,
        reponse: 'Bonjour, votre certificat est en cours de traitement. Le délai est dû à un volume élevé de demandes. Votre dossier sera traité en priorité.'
    },

    // --- Reclamation #20908 (Réouverte) ---
    {
        id: 9,
        id_reclamation: 20908,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'Erreur dans ma déclaration douanière DD-2026-7890. Le montant est incorrect.',
        date_changement: '2026-06-20T14:22:00',
        changed_by: 4001,
        reponse: null
    },
    {
        id: 10,
        id_reclamation: 20908,
        id_statut_avant: 1,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-20T16:00:00',
        changed_by: 3001,
        reponse: 'La correction a été effectuée sur votre déclaration.'
    },
    {
        id: 11,
        id_reclamation: 20908,
        id_statut_avant: 2,
        id_statut_apres: 4,
        commentaire: "Le montant n'est toujours pas correct. Veuillez vérifier à nouveau svp.",
        date_changement: '2026-06-21T08:30:00',
        changed_by: 4001,
        reponse: null
    },

    // --- Reclamation #20920 (Clôturée, simple) ---
    {
        id: 12,
        id_reclamation: 20920,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'Test de réclamation pour vérification du système.',
        date_changement: '2026-06-23T12:03:00',
        changed_by: 4001,
        reponse: null
    },
    {
        id: 13,
        id_reclamation: 20920,
        id_statut_avant: 1,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-23T12:30:00',
        changed_by: 3001,
        reponse: 'Votre demande a été traitée avec succès.'
    },
    {
        id: 14,
        id_reclamation: 20920,
        id_statut_avant: 2,
        id_statut_apres: 3,
        commentaire: null,
        date_changement: '2026-06-23T13:00:00',
        changed_by: 4001,
        reponse: null
    },

    // --- Reclamation #20919 (Clôturée) ---
    {
        id: 15,
        id_reclamation: 20919,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'Deuxième test.',
        date_changement: '2026-06-23T11:35:00',
        changed_by: 4001,
        reponse: null
    },
    {
        id: 16,
        id_reclamation: 20919,
        id_statut_avant: 1,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-23T11:50:00',
        changed_by: 3001,
        reponse: 'Traité.'
    },
    {
        id: 17,
        id_reclamation: 20919,
        id_statut_avant: 2,
        id_statut_apres: 3,
        commentaire: null,
        date_changement: '2026-06-23T12:00:00',
        changed_by: 4001,
        reponse: null
    },

    // --- Reclamation #20918 (Affectée, just initial) ---
    {
        id: 18,
        id_reclamation: 20918,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: "Impossible d'accéder au service CCS depuis ce matin.",
        date_changement: '2026-06-23T10:15:00',
        changed_by: 4001,
        reponse: null
    },

    // --- Reclamation #20913 (Affectée) ---
    {
        id: 19,
        id_reclamation: 20913,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'okkkkkkkkkkk',
        date_changement: '2026-06-22T16:40:00',
        changed_by: 2001,
        reponse: null
    },

    // --- Reclamation #20912 (Clôturée) ---
    {
        id: 20,
        id_reclamation: 20912,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: 'Test de synchronisation Odoo.',
        date_changement: '2026-06-22T16:34:00',
        changed_by: 4001,
        reponse: null
    },
    {
        id: 21,
        id_reclamation: 20912,
        id_statut_avant: 1,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-22T16:50:00',
        changed_by: 3001,
        reponse: 'Synchronisation vérifiée et fonctionnelle.'
    },
    {
        id: 22,
        id_reclamation: 20912,
        id_statut_avant: 2,
        id_statut_apres: 3,
        commentaire: null,
        date_changement: '2026-06-22T17:00:00',
        changed_by: 4001,
        reponse: null
    },

    // --- Reclamation #20905 (Clôturée) ---
    {
        id: 23,
        id_reclamation: 20905,
        id_statut_avant: null,
        id_statut_apres: 1,
        commentaire: "Demande d'informations sur titres d'import.",
        date_changement: '2026-06-19T11:00:00',
        changed_by: 4001,
        reponse: null
    },
    {
        id: 24,
        id_reclamation: 20905,
        id_statut_avant: 1,
        id_statut_apres: 2,
        commentaire: null,
        date_changement: '2026-06-19T14:30:00',
        changed_by: 3001,
        reponse: "Les titres d'import pour équipements industriels nécessitent le formulaire TI-2026."
    },
    {
        id: 25,
        id_reclamation: 20905,
        id_statut_avant: 2,
        id_statut_apres: 3,
        commentaire: null,
        date_changement: '2026-06-19T15:00:00',
        changed_by: 4001,
        reponse: null
    }
];

/* ----- PMPCE_RECLAMATION_STATUS_DOCUMENT -----
 * Columns: ID, ID_STATUS_HISTORY, DOCUMENT_GUID, DOCUMENT_NAME, DATE_UPLOAD
 * ----- */

PortnetApp.mockStatusDocuments = [
    {
        id: 1,
        id_status_history: 6,
        document_guid: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
        document_name: 'sampleTest2.pdf',
        date_upload: '2026-06-14T14:32:00'
    },
    {
        id: 2,
        id_status_history: 9,
        document_guid: 'b2c3d4e5-f6a7-8901-bcde-f12345678901',
        document_name: 'facture_commerciale.pdf',
        date_upload: '2026-06-20T14:22:00'
    }
];
