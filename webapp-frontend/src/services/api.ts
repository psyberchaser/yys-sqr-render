// API service for communicating with Flask backend
const API_BASE_URL = 'https://yys-sqr-render.onrender.com';

export interface Card {
  watermark_id: string;
  card_name: string;
  description: string;
  series: string;
  rarity: string;
  creator_address: string;
  image_url: string;
  watermarked_image_url: string;
  created_at: string;
  scan_count: number;
  owner_address?: string;
  nft_token_id?: number;
  minted_at?: string;
}

export interface CreateCardData {
  card_name: string;
  description?: string;
  series?: string;
  rarity?: string;
  creator_address?: string;
  image: string; // base64 encoded
}

export interface CreateCardResponse {
  success: boolean;
  card: Card;
  watermarked_image: string;
  error?: string;
}

export interface GetCardsResponse {
  cards: Card[];
  total: number;
  pages: number;
  current_page: number;
}

class ApiService {
  async createCard(data: CreateCardData): Promise<CreateCardResponse> {
    const response = await fetch(`${API_BASE_URL}/api/cards`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getCards(page: number = 1, perPage: number = 20): Promise<GetCardsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/cards?page=${page}&per_page=${perPage}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getCard(watermarkId: string): Promise<Card> {
    const response = await fetch(`${API_BASE_URL}/api/cards/${watermarkId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Helper function to convert file to base64
  fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data:image/...;base64, prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }
}

export const apiService = new ApiService();