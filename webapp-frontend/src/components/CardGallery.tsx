import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { CardContainer, CardBody, CardItem } from './ui/3d-card';
import { Eye, Calendar, Loader2 } from 'lucide-react';
import { apiService, Card as CardType } from '../services/api';

interface CardGalleryProps {
  onCardSelect?: (watermarkId: string) => void;
}

export function CardGallery({ onCardSelect }: CardGalleryProps) {
  const [cards, setCards] = useState<CardType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  const loadCards = async (page: number = 1) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getCards(page, 12);
      setCards(response.cards);
      setCurrentPage(response.current_page);
      setTotalPages(response.pages);
      setTotal(response.total);
    } catch (error) {
      console.error('Error loading cards:', error);
      setError(error instanceof Error ? error.message : 'Failed to load cards');
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
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-2 text-center">Card Gallery</h2>
          <p className="text-muted-foreground">Loading cards...</p>
        </div>

        {/* Loading Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 8 }, (_, i) => (
            <div key={i} className="bg-white border border-gray-200 rounded-xl overflow-hidden animate-pulse">
              <div className="aspect-square bg-gray-200"></div>
              <div className="p-4 space-y-3">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-2 text-center">Card Gallery</h2>
        </div>

        <div className="text-center py-12">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h3 className="text-xl font-semibold mb-2 text-red-600">Failed to Load Cards</h3>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={() => loadCards(currentPage)} variant="outline">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold mb-2 text-center">Card Gallery</h2>
        <p className="text-muted-foreground">
          Explore all created cards ({total} total)
        </p>
      </div>

      {cards.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No cards yet</h3>
          <p className="text-muted-foreground">Be the first to create a trading card!</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {cards.map((card) => (
              <CardContainer key={card.watermark_id} containerClassName="py-4">
                <CardBody className="bg-white relative group/card hover:shadow-2xl hover:shadow-blue-500/[0.1] border border-gray-200 w-full max-w-sm h-auto rounded-xl p-0 overflow-hidden font-barlow">
                  {/* Image Section */}
                  <CardItem translateZ="50" className="w-full">
                    <div className="aspect-square relative group overflow-hidden bg-gray-100">
                      <img
                        src={card.image_url}
                        alt={card.card_name}
                        className="w-full h-full object-cover cursor-pointer transition-all duration-300 group-hover:scale-110"
                        loading="lazy"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                          const parent = target.parentElement;
                          if (parent) {
                            parent.innerHTML = `
                              <div class="w-full h-full flex items-center justify-center bg-gray-200">
                                <div class="text-center text-gray-500">
                                  <div class="text-2xl mb-2">🖼️</div>
                                  <div class="text-sm">Image not available</div>
                                </div>
                              </div>
                            `;
                          }
                        }}
                        onClick={() => onCardSelect?.(card.watermark_id)}
                        title="Click to view details"
                      />

                      {/* Watermark ID Badge */}
                      <CardItem
                        translateZ="60"
                        className="absolute top-3 right-3 bg-black/80 backdrop-blur-sm text-white px-2 py-1 rounded-md text-xs font-mono pointer-events-none"
                      >
                        {card.watermark_id}
                      </CardItem>



                      {/* Claimed Badge */}
                      {card.owner_address && (
                        <CardItem
                          translateZ="70"
                          className="absolute top-3 left-3 bg-blue-600 text-white px-2 py-1 rounded-md text-xs font-semibold"
                        >
                          Claimed
                        </CardItem>
                      )}
                    </div>
                  </CardItem>

                  {/* Content Section */}
                  <div className="p-4">
                    {/* Title */}
                    <CardItem
                      translateZ="50"
                      as="h3"
                      className="font-bold text-lg text-gray-900 hover:text-blue-600 transition-colors duration-200 mb-2 line-clamp-1 cursor-pointer"
                      onClick={() => onCardSelect?.(card.watermark_id)}
                    >
                      {card.card_name}
                    </CardItem>

                    {/* Series and Rarity */}
                    <CardItem
                      translateZ="40"
                      className="flex items-center gap-3 mb-3"
                    >
                      {card.series && (
                        <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded-md">
                          {card.series}
                        </span>
                      )}
                      <div className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${card.rarity === 'Legendary' ? 'bg-yellow-500' :
                          card.rarity === 'Mythic' ? 'bg-purple-600' :
                            card.rarity === 'Epic' ? 'bg-purple-500' :
                              card.rarity === 'Rare' ? 'bg-blue-500' :
                                card.rarity === 'Uncommon' ? 'bg-green-500' :
                                  'bg-gray-400'
                          }`}></div>
                        <span className="text-sm font-medium text-gray-700">{card.rarity}</span>
                      </div>
                    </CardItem>

                    {/* Description - fixed height for uniform cards */}
                    <CardItem
                      translateZ="30"
                      as="p"
                      className="text-sm text-gray-600 mb-3 line-clamp-2 leading-relaxed min-h-[44px]"
                    >
                      {card.description || ''}
                    </CardItem>

                    {/* End of padded content */}
                  </div>

                  {/* Stats row full width */}
                  <div className="w-full border-t border-gray-100 px-4 py-2 text-xs text-gray-500 flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      <span>{card.scan_count} {card.scan_count === 1 ? 'scan' : 'scans'}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(card.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                </CardBody>
              </CardContainer>
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