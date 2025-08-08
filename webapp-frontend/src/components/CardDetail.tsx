import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { ArrowLeft, Eye, Calendar, Trophy, Sparkles, Copy, ExternalLink } from 'lucide-react';
import { apiService, Card as CardType } from '../services/api';

interface CardDetailProps {
  watermarkId: string;
  onBack: () => void;
}

export function CardDetail({ watermarkId, onBack }: CardDetailProps) {
  const [card, setCard] = useState<CardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const loadCard = async () => {
      console.log('Loading card with watermark ID:', watermarkId);
      try {
        const cardData = await apiService.getCard(watermarkId);
        console.log('Card data loaded:', cardData);
        setCard(cardData);
      } catch (error) {
        console.error('Error loading card:', error);
      } finally {
        setLoading(false);
      }
    };

    if (watermarkId) {
      loadCard();
    } else {
      console.error('No watermark ID provided');
      setLoading(false);
    }
  }, [watermarkId]);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-lg font-medium">Loading card details...</p>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="text-center py-12">
        <h3 className="text-xl font-semibold mb-2">Card not found</h3>
        <p className="text-muted-foreground mb-4">The requested card could not be found.</p>
        <Button onClick={onBack} className="flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Gallery
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="outline" onClick={onBack} className="flex items-center gap-2">
          <ArrowLeft className="w-4 h-4" />
          Back to Gallery
        </Button>
        <div>
          <h1 className="text-3xl font-bold">{card.card_name}</h1>
          <p className="text-muted-foreground">
            Watermark ID: <span className="font-mono font-semibold">{card.watermark_id}</span>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Images */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Original Image
              </CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={card.image_url}
                alt={card.card_name}
                className="w-full rounded-lg border hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.open(card.image_url, '_blank')}
              />
              <Button
                variant="outline"
                size="sm"
                className="w-full mt-3 flex items-center gap-2"
                onClick={() => window.open(card.image_url, '_blank')}
              >
                <ExternalLink className="w-4 h-4" />
                Open Full Size
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5" />
                Watermarked Image
              </CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={card.watermarked_image_url}
                alt={`${card.card_name} (Watermarked)`}
                className="w-full rounded-lg border hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.open(card.watermarked_image_url, '_blank')}
              />
              <Button
                variant="outline"
                size="sm"
                className="w-full mt-3 flex items-center gap-2"
                onClick={() => window.open(card.watermarked_image_url, '_blank')}
              >
                <ExternalLink className="w-4 h-4" />
                Open Full Size
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Details */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Card Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Series</label>
                  <p className="font-semibold">{card.series || 'N/A'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Rarity</label>
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${
                      card.rarity === 'Legendary' ? 'bg-yellow-500' :
                      card.rarity === 'Epic' ? 'bg-purple-500' :
                      card.rarity === 'Rare' ? 'bg-blue-500' :
                      card.rarity === 'Uncommon' ? 'bg-green-500' :
                      'bg-gray-500'
                    }`}></span>
                    <span className="font-semibold">{card.rarity}</span>
                  </div>
                </div>
              </div>

              {card.description && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Description</label>
                  <p className="mt-1">{card.description}</p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-muted-foreground">Watermark ID</label>
                <div className="flex items-center gap-2 mt-1">
                  <code className="bg-muted px-2 py-1 rounded font-mono text-sm">{card.watermark_id}</code>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(card.watermark_id)}
                    className="flex items-center gap-1"
                  >
                    <Copy className="w-3 h-3" />
                    {copied ? 'Copied!' : 'Copy'}
                  </Button>
                </div>
              </div>

              {card.creator_address && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Creator Address</label>
                  <div className="flex items-center gap-2 mt-1">
                    <code className="bg-muted px-2 py-1 rounded font-mono text-xs break-all">{card.creator_address}</code>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(card.creator_address!)}
                      className="flex items-center gap-1 shrink-0"
                    >
                      <Copy className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <Eye className="w-4 h-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-600">Scans</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-700">{card.scan_count}</p>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="flex items-center justify-center gap-2 mb-1">
                    <Calendar className="w-4 h-4 text-green-600" />
                    <span className="text-sm font-medium text-green-600">Created</span>
                  </div>
                  <p className="text-sm font-bold text-green-700">
                    {new Date(card.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {card.owner_address && (
                <div className="p-4 bg-yellow-50 rounded-lg border-l-4 border-yellow-400">
                  <div className="flex items-center gap-2 mb-2">
                    <Trophy className="w-5 h-5 text-yellow-600" />
                    <span className="font-semibold text-yellow-800">NFT Status</span>
                  </div>
                  <p className="text-sm text-yellow-700 mb-2">This card has been claimed as an NFT!</p>
                  <div className="space-y-1 text-xs">
                    <div>
                      <span className="font-medium">Owner:</span>
                      <code className="ml-2 bg-yellow-100 px-1 rounded">{card.owner_address}</code>
                    </div>
                    {card.nft_token_id && (
                      <div>
                        <span className="font-medium">Token ID:</span>
                        <code className="ml-2 bg-yellow-100 px-1 rounded">{card.nft_token_id}</code>
                      </div>
                    )}
                    {card.minted_at && (
                      <div>
                        <span className="font-medium">Minted:</span>
                        <span className="ml-2">{new Date(card.minted_at).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}