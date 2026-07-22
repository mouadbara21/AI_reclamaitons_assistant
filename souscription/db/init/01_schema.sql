-- =====================================================================
--  Schéma : Validation des documents de souscription (PortNet)
--  Base   : PostgreSQL 16
--  Exécuté automatiquement au 1er démarrage du conteneur.
-- =====================================================================

-- Une inscription = un dossier soumis par un opérateur.
CREATE TABLE inscriptions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raison_sociale      VARCHAR(255) NOT NULL,
    ice                 CHAR(15),
    rc_numero           VARCHAR(20),
    rc_ville            VARCHAR(100),
    identifiant_fiscal  VARCHAR(12),
    organisme           VARCHAR(20),        -- DOUANE | PORTNET_DOUANE
    type_entite         VARCHAR(50),
    type_operateur      VARCHAR(50),
    date_commencement   VARCHAR(20),
    siege_social        VARCHAR(255),
    telephone           VARCHAR(30),
    origine             VARCHAR(50),
    banque              VARCHAR(100),
    donnees_completes   JSONB,              -- TOUT le formulaire (snapshot complet)
    rib                 CHAR(24),
    statut              VARCHAR(20) NOT NULL DEFAULT 'EN_ATTENTE',
                        -- EN_ATTENTE | VALIDE | INCOMPLET | REJETE
    cree_le             TIMESTAMPTZ DEFAULT now(),
    maj_le              TIMESTAMPTZ DEFAULT now()
);

-- Les gérants d'une inscription (nom + CIN).
CREATE TABLE gerants (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inscription_id      UUID REFERENCES inscriptions(id) ON DELETE CASCADE,
    nom                 VARCHAR(100),
    prenom              VARCHAR(100),
    cin                 VARCHAR(20)
);

-- Les documents téléversés pour une inscription.
CREATE TABLE documents (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inscription_id      UUID REFERENCES inscriptions(id) ON DELETE CASCADE,
    type_document       VARCHAR(50) NOT NULL,   -- modele_j, ice, document_if, cni, rib...
    nom_fichier         VARCHAR(255),
    est_scanne          BOOLEAN DEFAULT false,
    televerse_le        TIMESTAMPTZ DEFAULT now()
);

-- Le rapport de validation produit par le backend.
CREATE TABLE rapports_validation (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    inscription_id      UUID REFERENCES inscriptions(id) ON DELETE CASCADE,
    statut_global       VARCHAR(20) NOT NULL,   -- VALIDE | WARNING | INVALIDE
    incoherences        JSONB,                  -- liste des problèmes détectés
    details             JSONB,                  -- champs extraits, cross-check...
    traite_le           TIMESTAMPTZ DEFAULT now()
);

-- Index utiles (recherche par inscription).
CREATE INDEX idx_gerants_inscription  ON gerants(inscription_id);
CREATE INDEX idx_documents_inscription ON documents(inscription_id);
CREATE INDEX idx_rapports_inscription  ON rapports_validation(inscription_id);
