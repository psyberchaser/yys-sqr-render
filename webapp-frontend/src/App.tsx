import React, { useState } from 'react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { LoginForm } from './components/login-form';
import { CreateCard } from './components/CreateCard';
import { CardGallery } from './components/CardGallery';
import { CardDetail } from './components/CardDetail';
import { Home, Palette, Grid3X3, Camera, Shield, Download, Zap } from 'lucide-react';

type View = 'home' | 'create' | 'gallery' | 'card-detail';

function App() {
  const [currentView, setCurrentView] = useState<View>('home');
  const [selectedCardId, setSelectedCardId] = useState<string>('');

  const handleCardSelect = (watermarkId: string) => {
    console.log('App: Card selected:', watermarkId);
    setSelectedCardId(watermarkId);
    setCurrentView('card-detail');
  };

  const renderView = () => {
    switch (currentView) {
      case 'create':
        return <CreateCard onCardCreated={() => setCurrentView('gallery')} />;
      case 'gallery':
        return <CardGallery onCardSelect={handleCardSelect} />;
      case 'card-detail':
        return <CardDetail watermarkId={selectedCardId} onBack={() => setCurrentView('gallery')} />;
      default:
        return <HomeView onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <button 
            onClick={() => setCurrentView('home')}
            className="text-4xl font-bold text-foreground mb-2 hover:text-primary cursor-pointer"
          >
            YYS-SQR
          </button>
          <p className="text-xl text-muted-foreground">Watermark Scanner & NFT Platform</p>
        </div>

        {/* Navigation */}
        <div className="flex justify-center gap-2 mb-8">
          <Button 
            variant={currentView === 'home' ? 'default' : 'outline'}
            onClick={() => setCurrentView('home')}
            className="flex items-center gap-2"
          >
            <Home className="w-4 h-4" />
            Home
          </Button>
          <Button 
            variant={currentView === 'create' ? 'default' : 'outline'}
            onClick={() => setCurrentView('create')}
            className="flex items-center gap-2"
          >
            <Palette className="w-4 h-4" />
            Create Card
          </Button>
          <Button 
            variant={currentView === 'gallery' ? 'default' : 'outline'}
            onClick={() => setCurrentView('gallery')}
            className="flex items-center gap-2"
          >
            <Grid3X3 className="w-4 h-4" />
            Gallery
          </Button>
        </div>

        {/* Content */}
        {renderView()}
      </div>
    </div>
  );
}

function HomeView({ onNavigate }: { onNavigate: (view: View) => void }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Left Column - Login */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Dashboard Access
                </CardTitle>
                <CardDescription>
                  Sign in to access your personal dashboard and manage your cards.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <LoginForm />
                <div className="mt-4 space-y-2">
                  <Button 
                    className="w-full flex items-center gap-2" 
                    variant="outline"
                    onClick={() => onNavigate('create')}
                  >
                    <Zap className="w-4 h-4" />
                    Quick Create Card
                  </Button>
                  <p className="text-sm text-muted-foreground text-center">
                    Simple authentication for card tracking
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Other Options */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Camera className="w-5 h-5" />
                  Scan Cards
                </CardTitle>
                <CardDescription>
                  Use our mobile app to scan physical trading cards and discover their digital twins.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button className="w-full flex items-center gap-2">
                  <Download className="w-4 h-4" />
                  Download Mobile App
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="w-5 h-5" />
                  Create Cards
                </CardTitle>
                <CardDescription>
                  Upload your artwork and create watermarked trading cards ready for printing.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className="w-full flex items-center gap-2" 
                  variant="outline"
                  onClick={() => onNavigate('create')}
                >
                  <Palette className="w-4 h-4" />
                  Create New Card
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Grid3X3 className="w-5 h-5" />
                  Browse Gallery
                </CardTitle>
                <CardDescription>
                  Explore all created cards and see their scan history and NFT status.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  className="w-full flex items-center gap-2" 
                  variant="secondary"
                  onClick={() => onNavigate('gallery')}
                >
                  <Grid3X3 className="w-4 h-4" />
                  View Gallery
                </Button>
              </CardContent>
            </Card>
          </div>
    </div>
  );
}

export default App;
