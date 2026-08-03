"""
Script de démonstration interactif du pipeline de vérification PortNet.
À exécuter devant votre superviseur lors de la réunion.
"""

import os
import sys
from datetime import datetime
from souscription.models.operator import OperatorFormData, FormGerant
from souscription.pipeline.orchestrator import process_submission
from souscription.models.enums import ValidationStatus

# Définition du chemin des documents de test
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUSCRIPTION_DIR = os.path.join(BASE_DIR, "souscription")

# Configurer l'encodage de la console si nécessaire
if sys.platform.startswith("win"):
    import ctypes
    # Activer UTF-8 sur Windows CMD
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass

def print_header(title):
    print("\n" + "=" * 80)
    print(f" {title.upper()} ".center(80, "="))
    print("=" * 80)

def main():
    print_header("Démo PortNet : Système de Vérification Documentaire")
    
    # 1. Préparation des données saisies dans le formulaire numérique (Step 1)
    # Nous simulons un opérateur qui saisit ses informations sur la plateforme
    form_data = OperatorFormData(
        raison_sociale="GOAL EVENTS",
        ice="002225298000015",  # ICE valide de Goal Events
        rc_number="429045",      # Numéro RC correspondant
        rc_city="Casablanca",
        if_number="20751297",    # IF
        tp_number="35778129",    # Patente / TP
        siege_social="34 RUE ALI ABDERREZAK RES AL MAMOUNE RACINE , Casablanca",
        gerants=[FormGerant(nom="HAYAT", prenom="JABRANE", cin="BE50973")],
        rib="011780000009210006415609" # RIB valide de l'attestation scannée (Medi Telecom)
    )
    
    print(f"[*] Données du formulaire chargées pour l'opérateur : {form_data.raison_sociale}")
    print(f"    - ICE déclaré : {form_data.ice}")
    print(f"    - RC déclaré  : {form_data.rc_number} ({form_data.rc_city})")
    print(f"    - Gérant      : {form_data.gerants[0].prenom} {form_data.gerants[0].nom} (CIN: {form_data.gerants[0].cin})")
    
    # 2. Fichiers téléversés par l'opérateur
    files_to_verify = [
        os.path.join(SOUSCRIPTION_DIR, "Model-J.pdf"),
        os.path.join(SOUSCRIPTION_DIR, "document IF.pdf"),
        os.path.join(SOUSCRIPTION_DIR, "ICE.pdf"),
        os.path.join(SOUSCRIPTION_DIR, "taxe_professionelle.pdf"),
        os.path.join(SOUSCRIPTION_DIR, "AttestationRIB-Bank of affrica.pdf")
    ]
    
    print(f"\n[*] Chargement des {len(files_to_verify)} documents PDF téléversés...")
    for f in files_to_verify:
        print(f"    -> {os.path.basename(f)}")
        
    # 3. Exécution du pipeline de vérification automatique
    # Nous simulons une date de soumission proche de la certification du Modèle J (08/08/2022)
    # afin de passer le test de récence des 90 jours.
    submission_date = datetime(2022, 9, 1)
    
    print("\n[>>] Lancement de l'analyse automatique (Classification -> Extraction -> Validation)...")
    start_time = datetime.now()
    report = process_submission(form_data, files_to_verify, submission_date=submission_date)
    duration = (datetime.now() - start_time).total_seconds()
    
    # 4. Affichage du rapport de conformité obtenu
    print_header("Résultats de l'analyse automatique")
    print(f"Statut Global du Dossier : {report.overall_status.value}")
    print(f"Temps de traitement      : {duration:.3f} secondes")
    
    if report.overall_status == ValidationStatus.VALID:
        print("[OK] DOSSIER CONFORME : Prêt pour auto-approbation.")
    elif report.overall_status == ValidationStatus.WARNING:
        print("[AVERTISSEMENT] : Des écarts mineurs ont été détectés. Envoi au tableau de contrôle pour validation manuelle.")
    else:
        print("[REJET] DOSSIER REJETÉ : Écarts critiques ou anomalies de fraude détectés.")
        
    if report.rejection_reasons:
        print("\nMotifs d'invalidation / de rejet :")
        for reason in report.rejection_reasons:
            # Remplacer caractères spéciaux pour éviter les erreurs d'affichage
            safe_reason = reason.replace("é", "e").replace("è", "e").replace("à", "a")
            print(f"  - [X] {safe_reason}")
            
    # 5. Affichage du détail des contrôles croisés (Cross-Reference Matrix)
    print_header("Détail de la Matrice de Cohérence Croisée")
    for check in report.cross_reference_report.checks:
        status_symbol = "[OK]" if check.status == ValidationStatus.VALID else ("[WARN]" if check.status == ValidationStatus.WARNING else "[FAIL]")
        score_str = f" (Fuzzy Score: {check.score:.1f}%)" if check.score is not None else ""
        # Remplacer accents
        safe_msg = check.message.replace("é", "e").replace("è", "e").replace("à", "a").replace("ê", "e")
        print(f" {status_symbol} [{check.field_name}] {safe_msg}{score_str}")
        
    print("\n" + "=" * 80)
    print(" FIN DE LA DÉMONSTRATION ".center(80, "="))
    print("=" * 80)

if __name__ == "__main__":
    main()
