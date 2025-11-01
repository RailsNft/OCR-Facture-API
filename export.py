"""
Module d'export vers formats comptables
Supporte : Sage, QuickBooks, Xero, FEC (Fichier des Écritures Comptables)
"""

import csv
import io
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP


def _format_date(date_str: str, format_type: str = "YYYY-MM-DD") -> str:
    """
    Formate une date selon le format demandé
    
    Args:
        date_str: Date au format détecté (peut être DD/MM/YYYY, YYYY-MM-DD, etc.)
        format_type: Format de sortie souhaité
    """
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    
    # Essayer de parser différents formats
    formats_to_try = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d.%m.%Y"
    ]
    
    parsed_date = None
    for fmt in formats_to_try:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            break
        except:
            continue
    
    if not parsed_date:
        # Si aucun format ne fonctionne, retourner la date actuelle
        parsed_date = datetime.now()
    
    # Formater selon le format_type
    if format_type == "YYYY-MM-DD":
        return parsed_date.strftime("%Y-%m-%d")
    elif format_type == "DD/MM/YYYY":
        return parsed_date.strftime("%d/%m/%Y")
    elif format_type == "MM/DD/YYYY":
        return parsed_date.strftime("%m/%d/%Y")
    else:
        return parsed_date.strftime("%Y-%m-%d")


def _safe_decimal(value: Any, default: float = 0.0) -> Decimal:
    """Convertit une valeur en Decimal de manière sécurisée"""
    if value is None:
        return Decimal(str(default))
    try:
        if isinstance(value, str):
            # Nettoyer la chaîne (enlever espaces, €, etc.)
            value = value.replace('€', '').replace(',', '.').strip()
        return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except:
        return Decimal(str(default))


def export_to_sage(invoice_data: Dict) -> str:
    """
    Exporte les données de facture au format Sage (CSV)
    
    Format Sage attendu :
    - Date, Numéro facture, Fournisseur, Référence, Description, Qté, Prix unitaire, Total HT, TVA, Total TTC
    
    Args:
        invoice_data: Données extraites de la facture
    
    Returns:
        CSV au format Sage
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', lineterminator='\n')
    
    # En-têtes Sage
    headers = [
        "Date",
        "Numéro facture",
        "Fournisseur",
        "Référence",
        "Description",
        "Quantité",
        "Prix unitaire",
        "Total HT",
        "Taux TVA",
        "Montant TVA",
        "Total TTC"
    ]
    writer.writerow(headers)
    
    # Date de facture
    invoice_date = _format_date(invoice_data.get("date", ""))
    invoice_number = invoice_data.get("invoice_number", "N/A")
    vendor = invoice_data.get("vendor", "Fournisseur inconnu")
    
    # Calculer le taux de TVA
    total_ht = _safe_decimal(invoice_data.get("total_ht") or invoice_data.get("total", 0))
    total_ttc = _safe_decimal(invoice_data.get("total_ttc") or invoice_data.get("total", 0))
    tva_amount = _safe_decimal(invoice_data.get("tva", 0))
    
    if total_ht > 0:
        tva_rate = ((total_ttc - total_ht) / total_ht * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        tva_rate = Decimal("20.00")  # Par défaut 20%
    
    # Exporter les lignes (items)
    items = invoice_data.get("items", [])
    if items:
        for item in items:
            description = item.get("description", "Article")
            quantity = _safe_decimal(item.get("quantity", 1))
            unit_price = _safe_decimal(item.get("unit_price", 0))
            item_total = _safe_decimal(item.get("total", unit_price * quantity))
            
            # Calculer TVA pour cette ligne
            item_ht = item_total
            item_tva = (item_ht * tva_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            item_ttc = item_ht + item_tva
            
            writer.writerow([
                invoice_date,
                invoice_number,
                vendor,
                item.get("reference", ""),
                description,
                str(quantity),
                str(unit_price),
                str(item_ht),
                str(tva_rate) + "%",
                str(item_tva),
                str(item_ttc)
            ])
    else:
        # Pas d'items détaillés, créer une ligne globale
        writer.writerow([
            invoice_date,
            invoice_number,
            vendor,
            "",
            "Facture complète",
            "1",
            str(total_ht),
            str(total_ht),
            str(tva_rate) + "%",
            str(tva_amount),
            str(total_ttc)
        ])
    
    return output.getvalue()


def export_to_quickbooks(invoice_data: Dict) -> str:
    """
    Exporte les données au format QuickBooks (IIF - Intuit Interchange Format)
    
    Format IIF :
    !TRNS	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO
    !SPL	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO
    !ENDTRNS
    
    Args:
        invoice_data: Données extraites de la facture
    
    Returns:
        Fichier IIF au format QuickBooks
    """
    lines = []
    
    # En-têtes IIF
    lines.append("!TRNS\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO")
    lines.append("!SPL\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO")
    lines.append("!ENDTRNS")
    lines.append("")  # Ligne vide
    
    # Transaction principale
    invoice_date = _format_date(invoice_data.get("date", ""), "MM/DD/YYYY")
    invoice_number = invoice_data.get("invoice_number", "INV-001")
    vendor = invoice_data.get("vendor", "Vendor")
    total_ttc = _safe_decimal(invoice_data.get("total_ttc") or invoice_data.get("total", 0))
    
    # Ligne transaction (débit)
    lines.append(f"TRNS\t{invoice_date}\tAccounts Payable\t{vendor}\t{total_ttc}\t{invoice_number}\tInvoice")
    
    # Splits (crédits)
    total_ht = _safe_decimal(invoice_data.get("total_ht") or invoice_data.get("total", 0))
    tva_amount = _safe_decimal(invoice_data.get("tva", total_ttc - total_ht))
    
    # Crédit : Expense Account (HT)
    lines.append(f"SPL\t{invoice_date}\tExpense Account\t{vendor}\t-{total_ht}\t{invoice_number}\tInvoice items")
    
    # Crédit : Tax Account (TVA)
    if tva_amount > 0:
        lines.append(f"SPL\t{invoice_date}\tTax Account\t{vendor}\t-{tva_amount}\t{invoice_number}\tVAT")
    
    # Fin de transaction
    lines.append("ENDTRNS")
    
    return "\n".join(lines)


def export_to_xero(invoice_data: Dict) -> str:
    """
    Exporte les données au format Xero (CSV)
    
    Format Xero attendu :
    ContactName, EmailAddress, POAddressLine1, POAddressLine2, POAddressLine3, POCity, PORegion, POPostalCode, POCountry,
    InvoiceNumber, Reference, InvoiceDate, DueDate, InventoryItemCode, Description, Quantity, UnitAmount, LineAmount,
    AccountCode, TaxType, TaxAmount, CurrencyCode
    
    Args:
        invoice_data: Données extraites de la facture
    
    Returns:
        CSV au format Xero
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', lineterminator='\n')
    
    # En-têtes Xero
    headers = [
        "ContactName",
        "EmailAddress",
        "POAddressLine1",
        "POAddressLine2",
        "POAddressLine3",
        "POCity",
        "PORegion",
        "POPostalCode",
        "POCountry",
        "InvoiceNumber",
        "Reference",
        "InvoiceDate",
        "DueDate",
        "InventoryItemCode",
        "Description",
        "Quantity",
        "UnitAmount",
        "LineAmount",
        "AccountCode",
        "TaxType",
        "TaxAmount",
        "CurrencyCode"
    ]
    writer.writerow(headers)
    
    # Données de base
    invoice_date = _format_date(invoice_data.get("date", ""))
    invoice_number = invoice_data.get("invoice_number", "INV-001")
    vendor = invoice_data.get("vendor", "Vendor")
    currency = invoice_data.get("currency", "EUR")
    
    # Calculer la date d'échéance (30 jours par défaut)
    try:
        parsed_date = datetime.strptime(invoice_date, "%Y-%m-%d")
        due_date = parsed_date + timedelta(days=30)
        due_date_str = due_date.strftime("%Y-%m-%d")
    except:
        due_date_str = invoice_date
    
    total_ht = _safe_decimal(invoice_data.get("total_ht") or invoice_data.get("total", 0))
    total_ttc = _safe_decimal(invoice_data.get("total_ttc") or invoice_data.get("total", 0))
    tva_amount = _safe_decimal(invoice_data.get("tva", total_ttc - total_ht))
    
    # Calculer le taux de TVA
    if total_ht > 0:
        tva_rate = ((total_ttc - total_ht) / total_ht * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        tva_rate = Decimal("20.00")
    
    # Déterminer le TaxType Xero selon le taux
    if tva_rate == Decimal("20.00"):
        tax_type = "FR.Standard (20%)"
    elif tva_rate == Decimal("10.00"):
        tax_type = "FR.Reduced (10%)"
    elif tva_rate == Decimal("5.50"):
        tax_type = "FR.Super Reduced (5.5%)"
    else:
        tax_type = f"FR.Standard ({tva_rate}%)"
    
    # Exporter les lignes
    items = invoice_data.get("items", [])
    if items:
        for item in items:
            description = item.get("description", "Item")
            quantity = _safe_decimal(item.get("quantity", 1))
            unit_price = _safe_decimal(item.get("unit_price", 0))
            line_amount = _safe_decimal(item.get("total", unit_price * quantity))
            
            # Calculer TVA pour cette ligne
            line_tva = (line_amount * tva_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            writer.writerow([
                vendor,  # ContactName
                "",  # EmailAddress
                "",  # POAddressLine1
                "",  # POAddressLine2
                "",  # POAddressLine3
                "",  # POCity
                "",  # PORegion
                "",  # POPostalCode
                "FR",  # POCountry
                invoice_number,  # InvoiceNumber
                invoice_number,  # Reference
                invoice_date,  # InvoiceDate
                due_date_str,  # DueDate
                item.get("reference", ""),  # InventoryItemCode
                description,  # Description
                str(quantity),  # Quantity
                str(unit_price),  # UnitAmount
                str(line_amount),  # LineAmount
                "200",  # AccountCode (dépenses par défaut)
                tax_type,  # TaxType
                str(line_tva),  # TaxAmount
                currency  # CurrencyCode
            ])
    else:
        # Ligne globale
        writer.writerow([
            vendor,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "FR",
            invoice_number,
            invoice_number,
            invoice_date,
            due_date_str,
            "",
            "Invoice total",
            "1",
            str(total_ht),
            str(total_ht),
            "200",
            tax_type,
            str(tva_amount),
            currency
        ])
    
    return output.getvalue()


def export_to_fec(invoice_data: Dict) -> str:
    """
    Exporte les données au format FEC (Fichier des Écritures Comptables)
    Format requis par l'administration fiscale française
    
    Format FEC (CSV séparé par tabulation) :
    JournalCode, JournalLib, EcritureNum, EcritureDate, CompteNum, CompteLib, CompAuxNum, CompAuxLib,
    PieceRef, PieceDate, EcritureLib, Debit, Credit, EcritureLet, DateLet, ValidDate, Montantdevise, Idevise
    
    Args:
        invoice_data: Données extraites de la facture
    
    Returns:
        Fichier FEC au format CSV (séparateur tabulation)
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter='\t', lineterminator='\n')
    
    # En-têtes FEC
    headers = [
        "JournalCode",
        "JournalLib",
        "EcritureNum",
        "EcritureDate",
        "CompteNum",
        "CompteLib",
        "CompAuxNum",
        "CompAuxLib",
        "PieceRef",
        "PieceDate",
        "EcritureLib",
        "Debit",
        "Credit",
        "EcritureLet",
        "DateLet",
        "ValidDate",
        "Montantdevise",
        "Idevise"
    ]
    writer.writerow(headers)
    
    # Données de base
    invoice_date = _format_date(invoice_data.get("date", ""), "YYYYMMDD")
    invoice_number = invoice_data.get("invoice_number", "FAC-001")
    vendor = invoice_data.get("vendor", "Fournisseur")
    
    total_ht = _safe_decimal(invoice_data.get("total_ht") or invoice_data.get("total", 0))
    total_ttc = _safe_decimal(invoice_data.get("total_ttc") or invoice_data.get("total", 0))
    tva_amount = _safe_decimal(invoice_data.get("tva", total_ttc - total_ht))
    
    # Écriture 1 : Débit - Compte Fournisseur (401)
    writer.writerow([
        "ACH",  # JournalCode
        "Achats",  # JournalLib
        "1",  # EcritureNum
        invoice_date,  # EcritureDate
        "401",  # CompteNum (Fournisseurs)
        "Fournisseurs",  # CompteLib
        "",  # CompAuxNum
        vendor,  # CompAuxLib
        invoice_number,  # PieceRef
        invoice_date,  # PieceDate
        f"Facture {invoice_number} - {vendor}",  # EcritureLib
        str(total_ttc),  # Debit
        "",  # Credit
        "",  # EcritureLet
        "",  # DateLet
        invoice_date,  # ValidDate
        "",  # Montantdevise
        "EUR"  # Idevise
    ])
    
    # Écriture 2 : Crédit - Compte Achats (607)
    writer.writerow([
        "ACH",
        "Achats",
        "2",
        invoice_date,
        "607",  # CompteNum (Achats)
        "Achats de marchandises",  # CompteLib
        "",
        "",
        invoice_number,
        invoice_date,
        f"Facture {invoice_number} - {vendor}",
        "",  # Debit
        str(total_ht),  # Credit
        "",
        "",
        invoice_date,
        "",
        "EUR"
    ])
    
    # Écriture 3 : Crédit - Compte TVA déductible (44566)
    if tva_amount > 0:
        writer.writerow([
            "ACH",
            "Achats",
            "3",
            invoice_date,
            "44566",  # CompteNum (TVA déductible)
            "TVA déductible sur autres biens et services",  # CompteLib
            "",
            "",
            invoice_number,
            invoice_date,
            f"TVA facture {invoice_number}",
            "",  # Debit
            str(tva_amount),  # Credit
            "",
            "",
            invoice_date,
            "",
            "EUR"
        ])
    
    return output.getvalue()


def export_to_csv_generic(invoice_data: Dict) -> str:
    """
    Exporte les données au format CSV générique (compatible avec la plupart des logiciels comptables)
    
    Args:
        invoice_data: Données extraites de la facture
    
    Returns:
        CSV générique
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', lineterminator='\n')
    
    # En-têtes
    headers = [
        "Date",
        "Invoice Number",
        "Vendor",
        "Client",
        "Description",
        "Quantity",
        "Unit Price",
        "Total HT",
        "VAT Rate",
        "VAT Amount",
        "Total TTC",
        "Currency"
    ]
    writer.writerow(headers)
    
    # Données de base
    invoice_date = _format_date(invoice_data.get("date", ""))
    invoice_number = invoice_data.get("invoice_number", "N/A")
    vendor = invoice_data.get("vendor", "")
    client = invoice_data.get("client", "")
    currency = invoice_data.get("currency", "EUR")
    
    total_ht = _safe_decimal(invoice_data.get("total_ht") or invoice_data.get("total", 0))
    total_ttc = _safe_decimal(invoice_data.get("total_ttc") or invoice_data.get("total", 0))
    tva_amount = _safe_decimal(invoice_data.get("tva", total_ttc - total_ht))
    
    # Calculer le taux de TVA
    if total_ht > 0:
        tva_rate = ((total_ttc - total_ht) / total_ht * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        tva_rate = Decimal("0.00")
    
    # Exporter les lignes
    items = invoice_data.get("items", [])
    if items:
        for item in items:
            description = item.get("description", "")
            quantity = _safe_decimal(item.get("quantity", 1))
            unit_price = _safe_decimal(item.get("unit_price", 0))
            item_total = _safe_decimal(item.get("total", unit_price * quantity))
            
            # Calculer TVA pour cette ligne
            item_tva = (item_total * tva_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            item_ttc = item_total + item_tva
            
            writer.writerow([
                invoice_date,
                invoice_number,
                vendor,
                client,
                description,
                str(quantity),
                str(unit_price),
                str(item_total),
                str(tva_rate) + "%",
                str(item_tva),
                str(item_ttc),
                currency
            ])
    else:
        # Ligne globale
        writer.writerow([
            invoice_date,
            invoice_number,
            vendor,
            client,
            "Invoice total",
            "1",
            str(total_ht),
            str(total_ht),
            str(tva_rate) + "%",
            str(tva_amount),
            str(total_ttc),
            currency
        ])
    
    return output.getvalue()


def export_to_json(invoice_data: Dict) -> str:
    """
    Exporte les données au format JSON structuré
    
    Args:
        invoice_data: Données extraites de la facture
    
    Returns:
        JSON formaté
    """
    import json
    
    # Créer une structure JSON propre
    export_data = {
        "invoice": {
            "number": invoice_data.get("invoice_number"),
            "date": invoice_data.get("date"),
            "vendor": invoice_data.get("vendor"),
            "client": invoice_data.get("client"),
            "currency": invoice_data.get("currency", "EUR")
        },
        "amounts": {
            "total_ht": float(_safe_decimal(invoice_data.get("total_ht") or invoice_data.get("total", 0))),
            "total_ttc": float(_safe_decimal(invoice_data.get("total_ttc") or invoice_data.get("total", 0))),
            "vat_amount": float(_safe_decimal(invoice_data.get("tva", 0)))
        },
        "items": invoice_data.get("items", []),
        "banking_info": invoice_data.get("banking_info", {}),
        "extracted_at": datetime.now().isoformat()
    }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)

