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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {cards.map((card) => (
              <div key={card.watermark_id} className="bg-white rounded-xl shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100">
                {/* Image Section - Full Width */}
                <div className="aspect-square relative group overflow-hidden">
                  <img
                    src={card.image_url}
                    alt={card.card_name}
                    className="w-full h-full object-cover cursor-pointer transition-all duration-300 group-hover:scale-110"
                    onClick={(e) => {
                      e.stopPropagation();
                      const newWindow = window.open('', '_blank');
                      if (newWindow) {
                        newWindow.document.write(`
                          <html>
                            <head>
                              <title>${card.card_name} - Watermarked</title>
                              <style>
                                body { margin: 0; padding: 20px; background: #000; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
                                img { max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px; }
                              </style>
                            </head>
                            <body>
                              <img src="${card.watermarked_image_url}" alt="${card.card_name} - Watermarked" />
                            </body>
                          </html>
                        `);
                        newWindow.document.close();
                      }
                    }}
                    title="Click to view watermarked image"
                  />
                  
                  {/* Watermark ID Badge */}
                  <div className="absolute top-3 right-3 bg-black/80 backdrop-blur-sm text-white px-2 py-1 rounded-md text-xs font-mono pointer-events-none">
                    {card.watermark_id}
                  </div>
                  
                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all duration-300 pointer-events-none flex items-center justify-center">
                    <div className="bg-white/95 backdrop-blur-sm rounded-full p-3 transform scale-0 group-hover:scale-100 transition-transform duration-300 shadow-lg">
                      <Eye className="w-5 h-5 text-gray-700" />
                    </div>
                  </div>
                  
                  {/* NFT Badge */}
                  {card.owner_address && (
                    <div className="absolute top-3 left-3 bg-gradient-to-r from-yellow-400 to-yellow-600 text-white px-2 py-1 rounded-md text-xs font-semibold flex items-center gap-1">
                      <Trophy className="w-3 h-3" />
                      NFT
                    </div>
                  )}
                </div>

                {/* Content Section */}
                <div className="p-4">
                  {/* Title */}
                  <h3 
                    className="font-bold text-lg text-gray-900 cursor-pointer hover:text-blue-600 transition-colors duration-200 mb-2 line-clamp-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      onCardSelect?.(card.watermark_id);
                    }}
                    title="Click to view card details"
                  >
                    {card.card_name}
                  </h3>
                  
                  {/* Series and Rarity */}
                  <div className="flex items-center justify-between mb-3">
                    {card.series && (
                      <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded-md">
                        {card.series}
                      </span>
                    )}
                    <div className="flex items-center gap-1">
                      <div className={`w-2 h-2 rounded-full ${
                        card.rarity === 'Legendary' ? 'bg-yellow-500' :
                        card.rarity === 'Mythic' ? 'bg-purple-600' :
                        card.rarity === 'Epic' ? 'bg-purple-500' :
                        card.rarity === 'Rare' ? 'bg-blue-500' :
                        card.rarity === 'Uncommon' ? 'bg-green-500' :
                        'bg-gray-400'
                      }`}></div>
                      <span className="text-sm font-medium text-gray-700">{card.rarity}</span>
                    </div>
                  </div>
                  
                  {/* Description */}
                  {card.description && (
                    <p className="text-sm text-gray-600 mb-3 line-clamp-2 leading-relaxed">
                      {card.description}
                    </p>
                  )}
                  
                  {/* Stats */}
                  <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-100">
                    <div className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      <span>{card.scan_count} scans</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(card.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
              </div>
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