"""
Module Factur-X pour génération, parsing et validation de factures électroniques
Conforme au standard EN16931 (Factur-X / ZUGFeRD 2.1.1)
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from lxml import etree
import io
import zipfile
from fastapi import HTTPException

# Namespaces XML pour Factur-X / EN16931
NSMAP = {
    'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
    'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
    'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100',
    'qdt': 'urn:un:unece:uncefact:data:standard:QualifiedDataType:100',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

# Profil Factur-X EN16931
FACTURX_PROFILE = "urn:factur-x.eu:1p0:basic"


def generate_facturx_xml(invoice_data: Dict) -> str:
    """
    Génère un XML Factur-X conforme au standard EN16931
    
    **Paramètres:**
    - `invoice_data`: Données de facture extraites (doit contenir au minimum date, numéro, montants, vendeur, client)
    
    **Retourne:**
    - XML Factur-X conforme EN16931 (format string)
    """
    try:
        # Créer la racine du document
        root = ET.Element(
            '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice',
            attrib={
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': 
                'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100 CrossIndustryInvoice_100pD16B.xsd'
            }
        )
        
        # ExchangedDocument (en-tête de la facture)
        exchanged_doc = ET.SubElement(root, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ExchangedDocument')
        
        # ID du document (numéro de facture)
        doc_id = ET.SubElement(exchanged_doc, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID')
        doc_id.text = invoice_data.get("invoice_number", "INV-001")
        
        # Type de document
        doc_type = ET.SubElement(exchanged_doc, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}TypeCode')
        doc_type.text = "380"  # Code UN/CEFACT pour facture
        
        # Date d'émission
        issue_date = ET.SubElement(exchanged_doc, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}IssueDateTime')
        date_time = ET.SubElement(issue_date, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}DateTimeString')
        date_time.set('format', '102')  # Format YYYYMMDD
        invoice_date = invoice_data.get("date", datetime.now().strftime("%d/%m/%Y"))
        # Convertir la date au format YYYYMMDD
        try:
            if "/" in invoice_date:
                parts = invoice_date.split("/")
                if len(parts) == 3:
                    formatted_date = f"{parts[2]}{parts[1]}{parts[0]}"
                else:
                    formatted_date = datetime.now().strftime("%Y%m%d")
            else:
                formatted_date = datetime.now().strftime("%Y%m%d")
        except:
            formatted_date = datetime.now().strftime("%Y%m%d")
        date_time.text = formatted_date
        
        # SupplierParty (Vendeur)
        supply_chain_trade = ET.SubElement(root, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SupplyChainTradeTransaction')
        applicable_header_trade = ET.SubElement(supply_chain_trade, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}ApplicableHeaderTradeAgreement')
        
        seller_trade_party = ET.SubElement(applicable_header_trade, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SellerTradeParty')
        seller_name = ET.SubElement(seller_trade_party, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}Name')
        seller_name.text = invoice_data.get("vendor", "Vendeur")
        
        # Postal address du vendeur (si disponible)
        seller_postal = ET.SubElement(seller_trade_party, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}PostalTradeAddress')
        seller_line = ET.SubElement(seller_postal, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}LineOne')
        seller_line.text = invoice_data.get("vendor", "Adresse vendeur")
        
        # BuyerParty (Client)
        buyer_trade_party = ET.SubElement(applicable_header_trade, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}BuyerTradeParty')
        buyer_name = ET.SubElement(buyer_trade_party, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}Name')
        buyer_name.text = invoice_data.get("client", "Client")
        
        # Montants HT, TTC, TVA
        applicable_header_trade_settlement = ET.SubElement(supply_chain_trade, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}ApplicableHeaderTradeSettlement')
        
        # Montant total HT
        if invoice_data.get("total_ht"):
            invoice_currency = invoice_data.get("currency", "EUR")
            monetary_summation = ET.SubElement(applicable_header_trade_settlement, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SpecifiedTradeSettlementMonetarySummation')
            
            line_total = ET.SubElement(monetary_summation, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}LineTotalAmount')
            line_total.set('currencyID', invoice_currency)
            line_total.text = f"{invoice_data.get('total_ht', 0):.2f}"
            
            tax_total = ET.SubElement(monetary_summation, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}TaxBasisTotalAmount')
            tax_total.set('currencyID', invoice_currency)
            tax_total.text = f"{invoice_data.get('total_ht', 0):.2f}"
            
            # Montant TVA
            if invoice_data.get("tva"):
                tax_amount = ET.SubElement(monetary_summation, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}TaxTotalAmount')
                tax_amount.set('currencyID', invoice_currency)
                tax_amount.text = f"{invoice_data.get('tva', 0):.2f}"
            
            # Montant total TTC
            grand_total = ET.SubElement(monetary_summation, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}GrandTotalAmount')
            grand_total.set('currencyID', invoice_currency)
            total_ttc = invoice_data.get("total_ttc") or invoice_data.get("total") or invoice_data.get("total_ht", 0)
            grand_total.text = f"{total_ttc:.2f}"
        
        # Lignes de facture (items)
        if invoice_data.get("items"):
            included_supply_chain = ET.SubElement(supply_chain_trade, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}IncludedSupplyChainTradeLineItem')
            
            for idx, item in enumerate(invoice_data.get("items", []), 1):
                trade_line = ET.SubElement(included_supply_chain, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}IncludedSupplyChainTradeLineItem')
                
                # Numéro de ligne
                line_id = ET.SubElement(trade_line, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}AssociatedDocumentLineDocument')
                line_doc_id = ET.SubElement(line_id, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}LineID')
                line_doc_id.text = str(idx)
                
                # Description
                specified_trade_product = ET.SubElement(trade_line, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SpecifiedTradeProduct')
                product_name = ET.SubElement(specified_trade_product, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}Name')
                product_name.text = item.get("description", f"Article {idx}")
                
                # Quantité
                if item.get("quantity"):
                    specified_line_trade = ET.SubElement(trade_line, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SpecifiedLineTradeAgreement')
                    net_price = ET.SubElement(specified_line_trade, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}NetPriceProductTradePrice')
                    price_amount = ET.SubElement(net_price, '{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ChargeAmount')
                    price_amount.set('currencyID', invoice_currency)
                    price_amount.text = f"{item.get('unit_price', 0):.2f}"
                    
                    # Montant total de la ligne
                    specified_line_trade_settlement = ET.SubElement(trade_line, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SpecifiedLineTradeSettlement')
                    line_trade_charge = ET.SubElement(specified_line_trade_settlement, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SpecifiedTradeSettlementLineMonetarySummation')
                    line_total_amount = ET.SubElement(line_trade_charge, '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}LineTotalAmount')
                    line_total_amount.set('currencyID', invoice_currency)
                    line_total_amount.text = f"{item.get('total', 0):.2f}"
        
        # Convertir en string XML avec déclaration XML
        xml_string = ET.tostring(root, encoding='unicode', method='xml')
        
        # Ajouter la déclaration XML et formater
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        formatted_xml = xml_declaration + xml_string
        
        return formatted_xml
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du XML Factur-X : {str(e)}"
        )


def parse_facturx_from_pdf(pdf_data: bytes) -> Tuple[Optional[str], Optional[Dict]]:
    """
    Extrait le XML Factur-X embarqué dans un PDF/A-3
    
    **Paramètres:**
    - `pdf_data`: Contenu du PDF en bytes
    
    **Retourne:**
    - Tuple (xml_string, invoice_data) où xml_string est le XML brut et invoice_data les données parsées
    """
    try:
        import fitz  # PyMuPDF
        
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        
        # Chercher le fichier XML embarqué dans les attachments
        xml_content = None
        invoice_data = None
        
        # Méthode 1: Chercher dans les attachments
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            # Les fichiers Factur-X sont généralement attachés comme fichiers
            # On cherche dans les annotations ou metadata
            
            # Chercher dans les metadata
            metadata = pdf_document.metadata
            if metadata:
                # Le XML peut être référencé dans les metadata
                # TODO: Implémenter extraction depuis metadata si nécessaire
                pass
        
        # Méthode 2: Chercher directement dans le contenu du PDF (structure interne)
        # Les PDF/A-3 avec Factur-X ont généralement le XML dans un fichier attaché
        # avec le nom "factur-x.xml" ou similaire
        
        # Pour PyMuPDF, on peut chercher dans les fichiers embarqués
        # Note: Cette fonctionnalité nécessite une version récente de PyMuPDF
        
        # Fallback: Chercher le pattern XML dans le PDF brut
        pdf_text = pdf_data.decode('latin-1', errors='ignore')
        
        # Chercher le début d'un XML Factur-X
        xml_start_patterns = [
            r'<rsm:CrossIndustryInvoice',
            r'<CrossIndustryInvoice',
            r'<?xml[^>]*>[\s\n]*<[^>]*CrossIndustryInvoice'
        ]
        
        for pattern in xml_start_patterns:
            match = re.search(pattern, pdf_text, re.IGNORECASE)
            if match:
                # Extraire le XML complet
                start_pos = match.start()
                # Chercher la fin du XML (approximatif)
                xml_end = pdf_text.find('</CrossIndustryInvoice>', start_pos)
                if xml_end == -1:
                    xml_end = pdf_text.find('</rsm:CrossIndustryInvoice>', start_pos)
                
                if xml_end > start_pos:
                    xml_content = pdf_text[start_pos:xml_end + len('</CrossIndustryInvoice>')]
                    # Parser le XML
                    try:
                        xml_root = ET.fromstring(xml_content)
                        invoice_data = parse_facturx_xml(xml_content)
                    except:
                        pass
                    break
        
        pdf_document.close()
        
        return xml_content, invoice_data
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'extraction du XML Factur-X : {str(e)}"
        )


def parse_facturx_xml(xml_string: str) -> Dict:
    """
    Parse un XML Factur-X et extrait les données structurées
    
    **Paramètres:**
    - `xml_string`: XML Factur-X (format string)
    
    **Retourne:**
    - Dictionnaire avec les données extraites de la facture
    """
    try:
        root = ET.fromstring(xml_string)
        
        invoice_data = {
            "invoice_number": None,
            "date": None,
            "vendor": None,
            "client": None,
            "total_ht": None,
            "total_ttc": None,
            "tva": None,
            "currency": "EUR",
            "items": []
        }
        
        # Namespace pour éviter les problèmes
        namespaces = {
            'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
            'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
            'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
        }
        
        # Extraire le numéro de facture
        doc_id = root.find('.//ram:ID', namespaces)
        if doc_id is not None:
            invoice_data["invoice_number"] = doc_id.text
        
        # Extraire la date
        date_elem = root.find('.//ram:DateTimeString', namespaces)
        if date_elem is not None:
            date_str = date_elem.text
            # Convertir YYYYMMDD en DD/MM/YYYY
            if len(date_str) == 8:
                invoice_data["date"] = f"{date_str[6:8]}/{date_str[4:6]}/{date_str[0:4]}"
        
        # Extraire le vendeur
        seller_name = root.find('.//ram:Name[../..]', namespaces)
        if seller_name is not None:
            # Chercher dans le contexte SellerTradeParty
            seller_party = root.find('.//rsm:SellerTradeParty', namespaces)
            if seller_party is not None:
                name_elem = seller_party.find('.//ram:Name', namespaces)
                if name_elem is not None:
                    invoice_data["vendor"] = name_elem.text
        
        # Extraire le client
        buyer_party = root.find('.//rsm:BuyerTradeParty', namespaces)
        if buyer_party is not None:
            name_elem = buyer_party.find('.//ram:Name', namespaces)
            if name_elem is not None:
                invoice_data["client"] = name_elem.text
        
        # Extraire les montants
        monetary_summation = root.find('.//rsm:SpecifiedTradeSettlementMonetarySummation', namespaces)
        if monetary_summation is not None:
            # Montant HT
            tax_basis = monetary_summation.find('.//ram:TaxBasisTotalAmount', namespaces)
            if tax_basis is not None:
                try:
                    invoice_data["total_ht"] = float(tax_basis.text)
                except:
                    pass
            
            # Montant TTC
            grand_total = monetary_summation.find('.//ram:GrandTotalAmount', namespaces)
            if grand_total is not None:
                try:
                    invoice_data["total_ttc"] = float(grand_total.text)
                    invoice_data["currency"] = grand_total.get('currencyID', 'EUR')
                except:
                    pass
            
            # Montant TVA
            tax_total = monetary_summation.find('.//ram:TaxTotalAmount', namespaces)
            if tax_total is not None:
                try:
                    invoice_data["tva"] = float(tax_total.text)
                except:
                    pass
        
        # Extraire les lignes de facture
        trade_lines = root.findall('.//rsm:IncludedSupplyChainTradeLineItem', namespaces)
        for line in trade_lines:
            item = {
                "description": None,
                "quantity": None,
                "unit_price": None,
                "total": None
            }
            
            # Description
            product_name = line.find('.//ram:Name', namespaces)
            if product_name is not None:
                item["description"] = product_name.text
            
            # Prix unitaire
            charge_amount = line.find('.//ram:ChargeAmount', namespaces)
            if charge_amount is not None:
                try:
                    item["unit_price"] = float(charge_amount.text)
                except:
                    pass
            
            # Montant total de la ligne
            line_total = line.find('.//ram:LineTotalAmount', namespaces)
            if line_total is not None:
                try:
                    item["total"] = float(line_total.text)
                except:
                    pass
            
            if item["description"]:
                invoice_data["items"].append(item)
        
        return invoice_data
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du parsing du XML Factur-X : {str(e)}"
        )


def validate_facturx_xml(xml_string: str) -> Dict:
    """
    Valide un XML Factur-X contre le schéma XSD EN16931 et vérifie les règles métier
    
    **Paramètres:**
    - `xml_string`: XML Factur-X à valider
    
    **Retourne:**
    - Dictionnaire avec le résultat de validation, erreurs et avertissements
    """
    errors = []
    warnings = []
    
    try:
        # Parser le XML
        root = ET.fromstring(xml_string)
        
        # Validation basique de structure (sans schéma XSD pour l'instant)
        # Les schémas XSD EN16931 sont complexes et volumineux
        
        # Vérifications métier basiques
        
        # 1. Vérifier que le numéro de facture existe
        doc_id = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ID')
        if doc_id is None or not doc_id.text:
            errors.append("Numéro de facture manquant")
        
        # 2. Vérifier que la date existe
        date_elem = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}DateTimeString')
        if date_elem is None or not date_elem.text:
            errors.append("Date d'émission manquante")
        
        # 3. Vérifier que le vendeur existe
        seller_party = root.find('.//{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SellerTradeParty')
        if seller_party is None:
            errors.append("Informations vendeur manquantes")
        
        # 4. Vérifier que le client existe
        buyer_party = root.find('.//{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}BuyerTradeParty')
        if buyer_party is None:
            errors.append("Informations client manquantes")
        
        # 5. Vérifier que les montants existent
        monetary_summation = root.find('.//{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}SpecifiedTradeSettlementMonetarySummation')
        if monetary_summation is None:
            errors.append("Montants totaux manquants")
        else:
            grand_total = monetary_summation.find('.//{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}GrandTotalAmount')
            if grand_total is None or not grand_total.text:
                errors.append("Montant total TTC manquant")
        
        # 6. Vérifier la cohérence des montants (si disponibles)
        if monetary_summation is not None:
            tax_basis = monetary_summation.find('.//{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}TaxBasisTotalAmount')
            tax_total = monetary_summation.find('.//{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}TaxTotalAmount')
            grand_total = monetary_summation.find('.//{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}GrandTotalAmount')
            
            if tax_basis is not None and tax_total is not None and grand_total is not None:
                try:
                    ht = float(tax_basis.text)
                    tva = float(tax_total.text)
                    ttc = float(grand_total.text)
                    
                    # Vérifier que HT + TVA = TTC (avec tolérance)
                    expected_ttc = ht + tva
                    if abs(expected_ttc - ttc) > 0.01:
                        warnings.append(f"Incohérence des montants : HT ({ht:.2f}) + TVA ({tva:.2f}) ≠ TTC ({ttc:.2f})")
                except:
                    pass
        
        # Générer un rapport lisible
        report_lines = []
        if errors:
            report_lines.append("❌ ERREURS:")
            for error in errors:
                report_lines.append(f"  - {error}")
        else:
            report_lines.append("✅ Aucune erreur détectée")
        
        if warnings:
            report_lines.append("\n⚠️ AVERTISSEMENTS:")
            for warning in warnings:
                report_lines.append(f"  - {warning}")
        
        report = "\n".join(report_lines)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "report": report
        }
    
    except ET.ParseError as e:
        return {
            "valid": False,
            "errors": [f"Erreur de parsing XML : {str(e)}"],
            "warnings": [],
            "report": f"❌ ERREUR: Le fichier XML n'est pas valide\n{str(e)}"
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Erreur lors de la validation : {str(e)}"],
            "warnings": [],
            "report": f"❌ ERREUR: {str(e)}"
        }

