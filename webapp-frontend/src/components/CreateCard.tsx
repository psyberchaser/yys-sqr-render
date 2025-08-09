import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { FileUpload } from './ui/file-upload';
import { StatefulButton } from './ui/stateful-button';
import { Upload, Sparkles, Eye, RotateCcw, CheckCircle, Loader2, Copy } from 'lucide-react';
import { apiService, CreateCardData } from '../services/api';
import { Confetti } from './Confetti';

interface CreateCardProps {
  onCardSelect?: (watermarkId: string) => void;
  onViewGallery?: () => void;
}

export function CreateCard({ onCardSelect, onViewGallery }: CreateCardProps) {
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

  const handleFileChange = (files: File[]) => {
    const file = files[0];
    if (file) {
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      alert('Please select an image file');
      return;
    }

    const base64Image = await apiService.fileToBase64(selectedFile);
    
    const createData: CreateCardData = {
      ...formData,
      image: base64Image,
    };

    const response = await apiService.createCard(createData);
    
    if (response.success) {
      setResult(response);
      
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
      throw new Error(response.error || 'Failed to create card');
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
              This card now contains the embedded data and can be minted.
            </p>
          </div>
        </div>

        {/* Card Preview */}
        <div className="max-w-md mx-auto">
          <Card>
            <CardContent className="p-0">
              <div className="aspect-square relative overflow-hidden rounded-t-lg">
                <img 
                  src={`data:image/png;base64,${result.watermarked_image}`}
                  alt="Created Card" 
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 right-3 bg-black/80 backdrop-blur-sm text-white px-2 py-1 rounded-md text-xs font-mono">
                  {result.card.watermark_id}
                </div>
              </div>
              <div className="p-4">
                <h3 className="font-bold text-lg text-gray-900 mb-2">
                  {result.card.card_name}
                </h3>
                <div className="flex items-center gap-3 mb-3">
                  {result.card.series && (
                    <span className="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded-md">
                      {result.card.series}
                    </span>
                  )}
                  <div className="flex items-center gap-1">
                    <div className={`w-2 h-2 rounded-full ${result.card.rarity === 'Legendary' ? 'bg-yellow-500' :
                      result.card.rarity === 'Mythic' ? 'bg-purple-600' :
                        result.card.rarity === 'Epic' ? 'bg-purple-500' :
                          result.card.rarity === 'Rare' ? 'bg-blue-500' :
                            result.card.rarity === 'Uncommon' ? 'bg-green-500' :
                              'bg-gray-400'
                      }`}></div>
                    <span className="text-sm font-medium text-gray-700">{result.card.rarity}</span>
                  </div>
                </div>
                {result.card.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {result.card.description}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="flex justify-center gap-3">
          <Button onClick={() => setResult(null)} className="flex items-center gap-2">
            <RotateCcw className="w-4 h-4" />
            Create Another Card
          </Button>
          <Button 
            variant="outline" 
            className="flex items-center gap-2"
            onClick={() => onCardSelect?.(result.card.watermark_id)}
          >
            <Eye className="w-4 h-4" />
            View Card Stats
          </Button>
          <Button 
            variant="secondary"
            className="flex items-center gap-2"
            onClick={() => onViewGallery?.()}
          >
            View Gallery
          </Button>
        </div>
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
              Create New Trading Card
            </CardTitle>
            <CardDescription>
              Upload your artwork and create watermarked trading cards ready for printing.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="card_name" className="block mb-2">Card Name *</Label>
                <Input
                  id="card_name"
                  value={formData.card_name}
                  onChange={(e) => handleInputChange('card_name', e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="series" className="block mb-2">Series</Label>
                  <Input
                    id="series"
                    value={formData.series}
                    onChange={(e) => handleInputChange('series', e.target.value)}
                    placeholder="e.g., Genesis Collection"
                  />
                </div>
                <div>
                  <Label htmlFor="rarity" className="block mb-2">Rarity</Label>
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
                <Label htmlFor="description" className="block mb-2">Description</Label>
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
                <Label htmlFor="creator_address" className="block mb-2">Creator Address</Label>
                <Input
                  id="creator_address"
                  value={formData.creator_address}
                  onChange={(e) => handleInputChange('creator_address', e.target.value)}
                  placeholder="0x..."
                />
              </div>

              <div>
                <Label className="block mb-2">Card Image *</Label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg">
                  <FileUpload onChange={handleFileChange} />
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Upload the original card image. A watermarked version will be generated automatically.
                </p>
              </div>

              <StatefulButton
                onClick={handleSubmit}
                disabled={!selectedFile || !formData.card_name}
                loadingText="Creating Card..."
                successText="Card Created!"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Create Card & Generate Watermark
              </StatefulButton>
            </div>
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

        {/* Removed How it Works section per request */}
      </div>
    </div>
  );
}