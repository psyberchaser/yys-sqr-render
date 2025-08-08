import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Palette, Upload, Sparkles, Eye, RotateCcw, CheckCircle, Loader2, Copy } from 'lucide-react';
import { apiService, CreateCardData } from '../services/api';
import { Confetti } from './Confetti';

interface CreateCardProps {
  onCardCreated?: (card: any) => void;
}

export function CreateCard({ onCardCreated }: CreateCardProps) {
  const [formData, setFormData] = useState({
    card_name: '',
    description: '',
    series: '',
    rarity: 'Common',
    creator_address: '',
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      alert('Please select an image file');
      return;
    }

    setIsLoading(true);
    try {
      const base64Image = await apiService.fileToBase64(selectedFile);
      
      const createData: CreateCardData = {
        ...formData,
        image: base64Image,
      };

      const response = await apiService.createCard(createData);
      
      if (response.success) {
        setResult(response);
        onCardCreated?.(response.card);
        
        // Reset form
        setFormData({
          card_name: '',
          description: '',
          series: '',
          rarity: 'Common',
          creator_address: '',
        });
        setSelectedFile(null);
        setPreviewUrl('');
      } else {
        alert('Error creating card: ' + response.error);
      }
    } catch (error) {
      alert('Error creating card: ' + (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  if (result) {
    return (
      <div className="space-y-6">
        <Confetti trigger={true} />
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-green-100 to-green-200 rounded-full mb-6 animate-pulse">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-4">
            🎉 Card Created Successfully!
          </h2>
          <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-6 mb-6 border border-green-200">
            <p className="text-lg text-muted-foreground mb-2">Your unique watermark ID:</p>
            <div className="flex items-center justify-center gap-3">
              <code className="text-2xl font-bold font-mono bg-white px-4 py-2 rounded-lg border-2 border-green-300 text-green-700">
                {result.card.watermark_id}
              </code>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigator.clipboard.writeText(result.card.watermark_id)}
                className="flex items-center gap-1"
              >
                <Copy className="w-4 h-4" />
                Copy
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-3">
              This ID is now embedded invisibly in your card image!
            </p>
          </div>
        </div>

        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h6 className="font-semibold mb-3 flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  Original Image
                </h6>
                <img 
                  src={result.card.image_url} 
                  alt="Original" 
                  className="w-full rounded-lg border hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => window.open(result.card.image_url, '_blank')}
                />
              </div>
              <div>
                <h6 className="font-semibold mb-3 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Watermarked Image
                </h6>
                <img 
                  src={`data:image/png;base64,${result.watermarked_image}`}
                  alt="Watermarked" 
                  className="w-full rounded-lg border hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => window.open(`data:image/png;base64,${result.watermarked_image}`, '_blank')}
                />
              </div>
            </div>
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400">
              <div className="flex items-start gap-3">
                <Sparkles className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h6 className="font-semibold text-blue-800 mb-1">Watermark Embedded!</h6>
                  <p className="text-sm text-blue-700">
                    This ID has been invisibly embedded in the image. Users can scan the physical card to claim the digital twin!
                  </p>
                </div>
              </div>
            </div>
            <div className="mt-6 flex gap-3">
              <Button onClick={() => setResult(null)} className="flex items-center gap-2">
                <RotateCcw className="w-4 h-4" />
                Create Another Card
              </Button>
              <Button variant="outline" className="flex items-center gap-2">
                <Eye className="w-4 h-4" />
                View Card Details
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Form */}
      <div className="lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Palette className="w-5 h-5" />
              Create New Trading Card
            </CardTitle>
            <CardDescription>
              Upload your artwork and create watermarked trading cards ready for printing.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="card_name">Card Name *</Label>
                <Input
                  id="card_name"
                  value={formData.card_name}
                  onChange={(e) => handleInputChange('card_name', e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="series">Series</Label>
                  <Input
                    id="series"
                    value={formData.series}
                    onChange={(e) => handleInputChange('series', e.target.value)}
                    placeholder="e.g., Genesis Collection"
                  />
                </div>
                <div>
                  <Label htmlFor="rarity">Rarity</Label>
                  <select
                    id="rarity"
                    value={formData.rarity}
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleInputChange('rarity', e.target.value)}
                    className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <option value="Common">Common</option>
                    <option value="Uncommon">Uncommon</option>
                    <option value="Rare">Rare</option>
                    <option value="Epic">Epic</option>
                    <option value="Legendary">Legendary</option>
                    <option value="Mythic">Mythic</option>
                  </select>
                </div>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  value={formData.description}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleInputChange('description', e.target.value)}
                  placeholder="Enter detailed description, lore, or story..."
                  rows={4}
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <div>
                <Label htmlFor="creator_address">Creator Address</Label>
                <Input
                  id="creator_address"
                  value={formData.creator_address}
                  onChange={(e) => handleInputChange('creator_address', e.target.value)}
                  placeholder="0x..."
                />
              </div>

              <div>
                <Label htmlFor="image">Card Image *</Label>
                <Input
                  id="image"
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  required
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Upload the original card image. A watermarked version will be generated automatically.
                </p>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating Card...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Create Card & Generate Watermark
                  </div>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      {/* Preview */}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            {previewUrl ? (
              <img src={previewUrl} alt="Preview" className="w-full rounded-lg border" />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Upload className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Upload an image to see preview</p>
              </div>
            )}
            
            {formData.card_name && (
              <div className="mt-4 space-y-2">
                <h6 className="font-semibold">Card Details:</h6>
                <ul className="text-sm space-y-1">
                  <li><strong>Name:</strong> {formData.card_name}</li>
                  <li><strong>Series:</strong> {formData.series || '-'}</li>
                  <li><strong>Rarity:</strong> {formData.rarity}</li>
                  <li><strong>Watermark ID:</strong> <span className="text-green-600">Auto-generated</span></li>
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>How it Works</CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="text-sm space-y-1">
              <li>1. Upload your card image and fill in details</li>
              <li>2. System generates a unique 5-character watermark ID</li>
              <li>3. Watermark is embedded invisibly into the image</li>
              <li>4. Card is added to the database</li>
              <li>5. Users can scan the physical card to claim the NFT</li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}