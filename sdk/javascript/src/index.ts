/**
 * SDK JavaScript/TypeScript officiel pour l'API OCR Facture France
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import FormData from 'form-data';
import * as fs from 'fs';
import * as path from 'path';

// Types
export interface ExtractResult {
  success: boolean;
  cached?: boolean;
  data?: {
    text: string;
    language: string;
    pages_processed?: number;
  };
  extracted_data?: {
    invoice_number?: string;
    total?: number;
    total_ht?: number;
    total_ttc?: number;
    tva?: number;
    date?: string;
    vendor?: string;
    client?: string;
    items?: InvoiceItem[];
    currency?: string;
  };
  confidence_scores?: {
    [key: string]: number;
  };
  compliance?: any;
  error?: string;
}

export interface InvoiceItem {
  description: string;
  quantity?: number;
  unit_price?: number;
  total?: number;
}

export interface BatchResult {
  success: boolean;
  results: ExtractResult[];
  total_processed: number;
  total_cached: number;
}

export interface QuotaInfo {
  plan: string;
  monthly: {
    limit: number;
    remaining: number;
    reset_time: string;
  };
  daily: {
    limit: number;
    remaining: number;
    reset_time: string;
  };
}

// Exceptions
export class OCRFactureAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'OCRFactureAPIError';
  }
}

export class OCRFactureAuthError extends OCRFactureAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'OCRFactureAuthError';
  }
}

export class OCRFactureRateLimitError extends OCRFactureAPIError {
  constructor(
    message: string,
    public retryAfter?: number,
    statusCode?: number,
    response?: any
  ) {
    super(message, statusCode, response);
    this.name = 'OCRFactureRateLimitError';
  }
}

export class OCRFactureValidationError extends OCRFactureAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'OCRFactureValidationError';
  }
}

export class OCRFactureServerError extends OCRFactureAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'OCRFactureServerError';
  }
}

/**
 * Client principal pour l'API OCR Facture
 */
export class OCRFactureAPI {
  private client: AxiosInstance;
  private baseUrl: string;
  private apiKey: string;

  /**
   * Crée une instance du client API
   * 
   * @param apiKey - Clé API RapidAPI ou X-RapidAPI-Proxy-Secret
   * @param baseUrl - URL de base de l'API (optionnel)
   * @param timeout - Timeout en millisecondes (défaut: 60000)
   */
  constructor(
    apiKey: string,
    baseUrl: string = 'https://ocr-facture-api-production.up.railway.app',
    timeout: number = 60000
  ) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/$/, '');

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout,
      headers: {
        'X-RapidAPI-Proxy-Secret': apiKey,
      },
    });

    // Intercepteur pour gérer les erreurs
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response) {
          const status = error.response.status;
          const data = error.response.data;

          if (status === 401) {
            throw new OCRFactureAuthError(
              'Clé API invalide ou manquante',
              status,
              data
            );
          } else if (status === 429) {
            const retryAfter = parseInt(
              error.response.headers['retry-after'] || '60'
            );
            throw new OCRFactureRateLimitError(
              'Quota dépassé. Veuillez réessayer plus tard.',
              retryAfter,
              status,
              data
            );
          } else if (status === 422) {
            throw new OCRFactureValidationError(
              data?.detail || 'Erreur de validation',
              status,
              data
            );
          } else if (status >= 500) {
            throw new OCRFactureServerError(
              `Erreur serveur: ${status}`,
              status,
              data
            );
          }
        }

        throw new OCRFactureAPIError(
          error.message || 'Erreur de connexion',
          error.response?.status,
          error.response?.data
        );
      }
    );
  }

  /**
   * Extrait les données d'une facture depuis un fichier
   * 
   * @param filePath - Chemin vers le fichier ou Buffer
   * @param language - Code langue (fra, eng, deu, spa, ita, por). Défaut: fra
   * @param checkCompliance - Activer validation conformité FR (défaut: false)
   * @param idempotencyKey - Clé d'idempotence (UUID recommandé, optionnel)
   * @returns Résultat OCR avec données extraites
   */
  async extractFromFile(
    filePath: string | Buffer,
    language: string = 'fra',
    checkCompliance: boolean = false,
    idempotencyKey?: string
  ): Promise<ExtractResult> {
    const form = new FormData();

    if (Buffer.isBuffer(filePath)) {
      form.append('file', filePath, 'invoice.pdf');
    } else {
      form.append('file', fs.createReadStream(filePath));
    }

    form.append('language', language);
    form.append('check_compliance', checkCompliance.toString());

    const headers: any = {
      ...form.getHeaders(),
    };

    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    const response = await this.client.post<ExtractResult>(
      '/v1/ocr/upload',
      form,
      { headers }
    );

    return response.data;
  }

  /**
   * Extrait les données d'une facture depuis une image encodée en base64
   * 
   * @param base64String - Image encodée en base64 (avec ou sans préfixe data:)
   * @param language - Code langue (défaut: fra)
   * @param checkCompliance - Activer validation conformité FR (défaut: false)
   * @param idempotencyKey - Clé d'idempotence (optionnel)
   * @returns Résultat OCR avec données extraites
   */
  async extractFromBase64(
    base64String: string,
    language: string = 'fra',
    checkCompliance: boolean = false,
    idempotencyKey?: string
  ): Promise<ExtractResult> {
    // Nettoyer le préfixe data: si présent
    if (base64String.startsWith('data:')) {
      base64String = base64String.split(',')[1];
    }

    const data = new URLSearchParams();
    data.append('image_base64', base64String);
    data.append('language', language);
    data.append('check_compliance', checkCompliance.toString());

    const headers: any = {};
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    const response = await this.client.post<ExtractResult>(
      '/v1/ocr/base64',
      data.toString(),
      {
        headers: {
          ...headers,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    return response.data;
  }

  /**
   * Traite plusieurs factures en une seule requête (batch processing)
   * 
   * @param files - Liste de chemins de fichiers ou Buffers
   * @param language - Code langue (défaut: fra)
   * @param idempotencyKey - Clé d'idempotence (optionnel)
   * @returns Résultats batch avec liste des résultats pour chaque fichier
   * @throws OCRFactureValidationError si plus de 10 fichiers
   */
  async batchExtract(
    files: (string | Buffer)[],
    language: string = 'fra',
    idempotencyKey?: string
  ): Promise<BatchResult> {
    if (files.length > 10) {
      throw new OCRFactureValidationError(
        'Maximum 10 fichiers par requête batch',
        400
      );
    }

    // Encoder tous les fichiers en base64
    const filesBase64: string[] = [];

    for (const file of files) {
      let fileData: Buffer;
      let mimePrefix = 'data:image/jpeg;base64,';

      if (Buffer.isBuffer(file)) {
        fileData = file;
      } else {
        fileData = fs.readFileSync(file);
        const ext = path.extname(file).toLowerCase();
        if (ext === '.pdf') {
          mimePrefix = 'data:application/pdf;base64,';
        } else if (ext === '.png') {
          mimePrefix = 'data:image/png;base64,';
        }
      }

      const base64 = fileData.toString('base64');
      filesBase64.push(`${mimePrefix}${base64}`);
    }

    const headers: any = {
      'Content-Type': 'application/json',
    };

    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }

    const response = await this.client.post<BatchResult>(
      '/v1/ocr/batch',
      {
        files: filesBase64,
        language,
      },
      { headers }
    );

    return response.data;
  }

  /**
   * Vérifie la conformité d'une facture française
   * 
   * @param invoiceData - Données extraites de la facture
   * @returns Résultat de validation de conformité
   */
  async checkCompliance(invoiceData: any): Promise<any> {
    const response = await this.client.post('/v1/compliance/check', invoiceData);
    return response.data;
  }

  /**
   * Valide les taux et calculs de TVA pour une facture française
   * 
   * @param invoiceData - Données extraites avec montants HT, TTC, TVA
   * @returns Résultat de validation TVA
   */
  async validateVAT(invoiceData: any): Promise<any> {
    const response = await this.client.post(
      '/compliance/validate-vat',
      invoiceData
    );
    return response.data;
  }

  /**
   * Enrichit les données avec l'API Sirene (Insee) à partir d'un SIRET
   * 
   * @param siret - Numéro SIRET (14 chiffres)
   * @returns Données enrichies depuis l'API Sirene
   */
  async enrichSiret(siret: string): Promise<any> {
    const response = await this.client.post('/compliance/enrich-siret', {
      siret,
    });
    return response.data;
  }

  /**
   * Valide un numéro TVA intracommunautaire via l'API VIES
   * 
   * @param vatNumber - Numéro TVA intracom (ex: FR47945319300)
   * @returns Résultat de validation VIES
   */
  async validateVIES(vatNumber: string): Promise<any> {
    const response = await this.client.post('/compliance/validate-vies', {
      vat_number: vatNumber,
    });
    return response.data;
  }

  /**
   * Génère un XML Factur-X (EN16931) à partir des données de facture
   * 
   * @param invoiceData - Données de facture extraites
   * @returns XML Factur-X conforme EN16931
   */
  async generateFacturX(invoiceData: any): Promise<any> {
    const response = await this.client.post('/facturx/generate', invoiceData);
    return response.data;
  }

  /**
   * Extrait le XML Factur-X embarqué dans un PDF/A-3
   * 
   * @param filePath - Chemin vers le PDF Factur-X ou Buffer
   * @returns XML extrait et données parsées
   */
  async parseFacturX(filePath: string | Buffer): Promise<any> {
    const form = new FormData();

    if (Buffer.isBuffer(filePath)) {
      form.append('file', filePath, 'invoice.pdf');
    } else {
      form.append('file', fs.createReadStream(filePath));
    }

    const response = await this.client.post('/facturx/parse', form, {
      headers: form.getHeaders(),
    });

    return response.data;
  }

  /**
   * Valide un XML Factur-X contre le schéma EN16931
   * 
   * @param xmlContent - Contenu XML Factur-X (string)
   * @returns Résultat de validation avec erreurs et avertissements
   */
  async validateFacturXXML(xmlContent: string): Promise<any> {
    const response = await this.client.post('/facturx/validate', {
      xml_content: xmlContent,
    });
    return response.data;
  }

  /**
   * Retourne la liste des langues supportées pour l'OCR
   * 
   * @returns Liste des langues avec codes et noms
   */
  async getSupportedLanguages(): Promise<any> {
    const response = await this.client.get('/v1/languages');
    return response.data;
  }

  /**
   * Retourne les informations sur le quota restant
   * 
   * @returns Informations sur quota, limites, utilisations
   */
  async getQuota(): Promise<QuotaInfo> {
    const response = await this.client.get<QuotaInfo>('/v1/quota');
    return response.data;
  }

  /**
   * Vérifie l'état de santé de l'API
   * 
   * @returns Statut de santé de l'API et dépendances
   */
  async healthCheck(): Promise<any> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

// Export par défaut
export default OCRFactureAPI;

