import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Grid3X3, Eye, Calendar, Loader2, Trophy } from 'lucide-react';
import { apiService, Card as CardType } from '../services/api';

interface CardGalleryProps {
  onCardSelect?: (watermarkId: string) => void;
}

export function CardGallery({ onCardSelect }: CardGalleryProps) {
  const [cards, setCards] = useState<CardType[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const loadCards = async (page: number = 1) => {
    setLoading(true);
    try {
      const response = await apiService.getCards(page, 12);
      setCards(response.cards);
      setCurrentPage(response.current_page);
      setTotalPages(response.pages);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading cards:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCards();
  }, []);

  const handlePageChange = (page: number) => {
    loadCards(page);
  };

  if (loading) {
    return (
      <div className="text-center py-16">
        <div className="relative">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-6 text-primary" />
          <div className="absolute inset-0 w-12 h-12 mx-auto border-4 border-primary/20 rounded-full animate-pulse"></div>
        </div>
        <h3 className="text-xl font-semibold mb-2">Loading Cards</h3>
        <p className="text-muted-foreground">Fetching your digital collection...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-2 flex items-center justify-center gap-3">
          <Grid3X3 className="w-8 h-8" />
          Card Gallery
        </h2>
        <p className="text-muted-foreground">
          Explore all created cards ({total} total)
        </p>
      </div>

      {cards.length === 0 ? (
        <div className="text-center py-12">
          <Grid3X3 className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No cards yet</h3>
          <p className="text-muted-foreground">Be the first to create a trading card!</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {cards.map((card) => (
              <Card key={card.watermark_id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-square relative group overflow-hidden rounded-t-lg">
                  <img
                    src={card.image_url}
                    alt={card.card_name}
                    className="w-full h-full object-cover cursor-pointer transition-all duration-200 group-hover:scale-105"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.open(card.watermarked_image_url, '_blank');
                    }}
                    title="Click to view watermarked image"
                  />
                  <div className="absolute top-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-xs font-mono pointer-events-none">
                    {card.watermark_id}
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none flex items-center justify-center">
                    <div className="bg-white/90 rounded-full p-2 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-200">
                      <Eye className="w-6 h-6 text-gray-800" />
                    </div>
                  </div>
                </div>
                <CardHeader className="pb-2">
                  <CardTitle 
                    className="text-lg cursor-pointer hover:text-primary transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log('Card title clicked:', card.watermark_id);
                      onCardSelect?.(card.watermark_id);
                    }}
                    title="Click to view card details"
                  >
                    {card.card_name}
                  </CardTitle>
                  <CardDescription>
                    {card.series && <span className="block">{card.series}</span>}
                    <span className="inline-flex items-center gap-1">
                      <span className={`w-2 h-2 rounded-full ${
                        card.rarity === 'Legendary' ? 'bg-yellow-500' :
                        card.rarity === 'Epic' ? 'bg-purple-500' :
                        card.rarity === 'Rare' ? 'bg-blue-500' :
                        card.rarity === 'Uncommon' ? 'bg-green-500' :
                        'bg-gray-500'
                      }`}></span>
                      {card.rarity}
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex justify-between items-center text-sm text-muted-foreground mb-2">
                    <span className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      {card.scan_count} scans
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(card.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {card.description && (
                    <p className="text-sm mt-2 line-clamp-2 text-muted-foreground">{card.description}</p>
                  )}
                  {card.owner_address && (
                    <div className="mt-2 flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
                      <Trophy className="w-3 h-3" />
                      NFT Claimed
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              
              <div className="flex gap-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const page = i + 1;
                  return (
                    <Button
                      key={page}
                      variant={currentPage === page ? "default" : "outline"}
                      size="sm"
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </Button>
                  );
                })}
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}