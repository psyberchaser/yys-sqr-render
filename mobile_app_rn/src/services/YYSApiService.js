// YYS-SQR API Service for React Native
import axios from 'axios';

// Configure your backend URL here
const API_BASE_URL = 'http://localhost:5000/api'; // Change to your server IP for device testing

class YYSApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 30 second timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Scan watermark from base64 image using automatic corner detection
   */
  async scanWatermark(base64Image) {
    try {
      const response = await this.client.post('/scan', {
        image: base64Image,
      });
      
      return response.data;
    } catch (error) {
      console.error('API Error - scanWatermark:', error);
      throw new Error(error.response?.data?.error || 'Network error');
    }
  }

  /**
   * Embed watermark in base64 image
   */
  async embedWatermark(base64Image, message) {
    try {
      const response = await this.client.post('/embed', {
        image: base64Image,
        message: message,
      });
      
      return response.data;
    } catch (error) {
      console.error('API Error - embedWatermark:', error);
      throw new Error(error.response?.data?.error || 'Network error');
    }
  }

  /**
   * Batch scan multiple images
   */
  async batchScan(base64Images) {
    try {
      const response = await this.client.post('/scan/batch', {
        images: base64Images,
      });
      
      return response.data;
    } catch (error) {
      console.error('API Error - batchScan:', error);
      throw new Error(error.response?.data?.error || 'Network error');
    }
  }

  /**
   * Get watermark capacity information
   */
  async getCapacity() {
    try {
      const response = await this.client.get('/capacity');
      return response.data;
    } catch (error) {
      console.error('API Error - getCapacity:', error);
      throw new Error(error.response?.data?.error || 'Network error');
    }
  }

  /**
   * Get available detection methods
   */
  async getDetectionMethods() {
    try {
      const response = await this.client.get('/methods');
      return response.data;
    } catch (error) {
      console.error('API Error - getDetectionMethods:', error);
      throw new Error(error.response?.data?.error || 'Network error');
    }
  }

  /**
   * Visualize corner detection process
   */
  async visualizeDetection(base64Image) {
    try {
      const response = await this.client.post('/scan/visualize', {
        image: base64Image,
      });
      
      return response.data;
    } catch (error) {
      console.error('API Error - visualizeDetection:', error);
      throw new Error(error.response?.data?.error || 'Network error');
    }
  }

  /**
   * Health check
   */
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      console.error('API Error - healthCheck:', error);
      throw new Error('Backend server not available');
    }
  }
}

// Export singleton instance
export default new YYSApiService();