/**
 * Tests unitaires pour le client SDK JavaScript/TypeScript
 */

import { OCRFactureAPI } from '../index';
import {
  OCRFactureAPIError,
  OCRFactureAuthError,
  OCRFactureRateLimitError,
  OCRFactureValidationError,
} from '../index';
import axios from 'axios';
import FormData from 'form-data';
import * as fs from 'fs';
import * as path from 'path';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('OCRFactureAPI', () => {
  let api: OCRFactureAPI;
  const mockApiKey = 'test_api_key';
  const baseUrl = 'https://ocr-facture-api-production.up.railway.app';

  beforeEach(() => {
    api = new OCRFactureAPI(mockApiKey);
    jest.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with API key', () => {
      const client = new OCRFactureAPI('test_key');
      expect(client).toBeInstanceOf(OCRFactureAPI);
    });

    it('should initialize with custom base URL', () => {
      const client = new OCRFactureAPI('test_key', 'https://custom-api.com');
      expect(client['baseUrl']).toBe('https://custom-api.com');
    });

    it('should initialize with custom timeout', () => {
      const client = new OCRFactureAPI('test_key', undefined, 120);
      expect(client['timeout']).toBe(120);
    });
  });

  describe('extractFromFile', () => {
    const mockSuccessResponse = {
      success: true,
      cached: false,
      data: {
        text: 'FACTURE\nNuméro: FAC-2024-001',
        language: 'fra',
      },
      extracted_data: {
        invoice_number: 'FAC-2024-001',
        total_ttc: 1250.5,
        total_ht: 1042.08,
        tva: 208.42,
        date: '15/03/2024',
        vendor: 'Société Example SARL',
        client: 'Client ABC',
      },
      confidence_scores: {
        invoice_number: 0.95,
        total_ttc: 0.92,
      },
    };

    it('should extract data from file successfully', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: mockSuccessResponse,
        status: 200,
      });

      // Mock fs.readFileSync
      jest.spyOn(fs, 'readFileSync').mockReturnValueOnce(Buffer.from('fake image data'));

      const result = await api.extractFromFile('test_facture.pdf', { language: 'fra' });

      expect(result.success).toBe(true);
      expect(result.extracted_data?.invoice_number).toBe('FAC-2024-001');
      expect(result.extracted_data?.total_ttc).toBe(1250.5);
      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/v1/ocr/upload'),
        expect.any(FormData),
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-RapidAPI-Proxy-Secret': mockApiKey,
          }),
        })
      );
    });

    it('should handle authentication error', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { error: 'Unauthorized' },
        },
      });

      jest.spyOn(fs, 'readFileSync').mockReturnValueOnce(Buffer.from('fake image data'));

      await expect(api.extractFromFile('test.pdf')).rejects.toThrow(OCRFactureAuthError);
    });

    it('should handle rate limit error', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 429,
          headers: { 'retry-after': '60' },
          data: { error: 'Rate limit exceeded' },
        },
      });

      jest.spyOn(fs, 'readFileSync').mockReturnValueOnce(Buffer.from('fake image data'));

      await expect(api.extractFromFile('test.pdf')).rejects.toThrow(OCRFactureRateLimitError);
    });

    it('should send idempotency key when provided', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: mockSuccessResponse,
        status: 200,
      });

      jest.spyOn(fs, 'readFileSync').mockReturnValueOnce(Buffer.from('fake image data'));

      await api.extractFromFile('test.pdf', { idempotencyKey: 'test-uuid-123' });

      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(FormData),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Idempotency-Key': 'test-uuid-123',
          }),
        })
      );
    });
  });

  describe('extractFromBase64', () => {
    const mockSuccessResponse = {
      success: true,
      extracted_data: {
        invoice_number: 'FAC-2024-001',
        total_ttc: 1250.5,
      },
    };

    it('should extract data from base64 successfully', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: mockSuccessResponse,
        status: 200,
      });

      const base64Data = 'data:image/jpeg;base64,/9j/4AAQSkZJRg==';
      const result = await api.extractFromBase64(base64Data, { language: 'fra' });

      expect(result.success).toBe(true);
      expect(result.extracted_data?.invoice_number).toBe('FAC-2024-001');
    });
  });

  describe('batchExtract', () => {
    const mockBatchResponse = {
      success: true,
      results: [
        {
          success: true,
          extracted_data: { invoice_number: 'FAC-001' },
        },
        {
          success: true,
          extracted_data: { invoice_number: 'FAC-002' },
        },
      ],
      total_processed: 2,
      total_cached: 0,
    };

    it('should process batch successfully', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: mockBatchResponse,
        status: 200,
      });

      jest.spyOn(fs, 'readFileSync').mockReturnValue(Buffer.from('fake image data'));

      const result = await api.batchExtract(['facture1.pdf', 'facture2.pdf']);

      expect(result.success).toBe(true);
      expect(result.total_processed).toBe(2);
      expect(result.results).toHaveLength(2);
    });

    it('should reject more than 10 files', async () => {
      const files = Array.from({ length: 11 }, (_, i) => `facture${i}.pdf`);

      await expect(api.batchExtract(files)).rejects.toThrow(OCRFactureValidationError);
    });
  });

  describe('checkCompliance', () => {
    const mockComplianceResponse = {
      success: true,
      compliance: {
        compliance_check: {
          compliant: true,
          score: 95.0,
          missing_fields: [],
        },
      },
    };

    it('should check compliance successfully', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: mockComplianceResponse,
        status: 200,
      });

      const result = await api.checkCompliance({ invoice_number: 'FAC-001' });

      expect(result.compliance?.compliance_check?.compliant).toBe(true);
    });
  });

  describe('generateFacturX', () => {
    const mockFacturXResponse = {
      success: true,
      xml: "<?xml version='1.0'?><Invoice>...</Invoice>",
      format: 'Factur-X EN16931',
    };

    it('should generate Factur-X successfully', async () => {
      mockedAxios.post.mockResolvedValueOnce({
        data: mockFacturXResponse,
        status: 200,
      });

      const result = await api.generateFacturX({ invoice_number: 'FAC-001' });

      expect(result.success).toBe(true);
      expect(result.xml).toBeDefined();
    });
  });

  describe('getSupportedLanguages', () => {
    const mockLanguagesResponse = {
      languages: [
        { code: 'fra', name: 'Français' },
        { code: 'eng', name: 'English' },
      ],
    };

    it('should get supported languages', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: mockLanguagesResponse,
        status: 200,
      });

      const result = await api.getSupportedLanguages();

      expect(result.languages).toHaveLength(2);
      expect(result.languages?.some((l) => l.code === 'fra')).toBe(true);
    });
  });

  describe('getQuota', () => {
    const mockQuotaResponse = {
      plan: 'PRO',
      monthly: { limit: 20000, remaining: 19500 },
      daily: { limit: 666, remaining: 600 },
    };

    it('should get quota information', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: mockQuotaResponse,
        status: 200,
      });

      const result = await api.getQuota();

      expect(result.plan).toBe('PRO');
      expect(result.monthly).toBeDefined();
    });
  });

  describe('healthCheck', () => {
    const mockHealthResponse = {
      status: 'healthy',
      api_version: '2.0.0',
    };

    it('should check health successfully', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: mockHealthResponse,
        status: 200,
      });

      const result = await api.healthCheck();

      expect(result.status).toBe('healthy');
    });
  });

  describe('Error handling', () => {
    it('should handle network errors', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('Network error'));

      jest.spyOn(fs, 'readFileSync').mockReturnValueOnce(Buffer.from('fake image data'));

      await expect(api.extractFromFile('test.pdf')).rejects.toThrow(OCRFactureAPIError);
    });

    it('should handle validation errors', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 422,
          data: { detail: 'Facture non conforme' },
        },
      });

      await expect(api.checkCompliance({})).rejects.toThrow(OCRFactureValidationError);
    });
  });
});



