import React from 'react';
import { Button } from '@/components/ui/button';

interface WelcomeScreenProps {
  onGetStarted: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onGetStarted }) => {
  const stats = [
    { value: '30s', label: 'Average generation time' },
    { value: '6', label: 'Unique variations' },
    { value: 'SVG', label: 'Scalable format' }
  ];

  return (
    <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-6">
      <div className="max-w-4xl w-full text-center space-y-12">
        <div className="space-y-6">
          <h2 className="text-5xl lg:text-6xl font-light tracking-tight">
            AI-powered logo generation in seconds
          </h2>
          <p className="text-xl text-muted-foreground font-light max-w-2xl mx-auto">
            Create professional logos instantly with our AI technology. 
            No design skills required, just describe your vision.
          </p>
        </div>

        <Button 
          onClick={onGetStarted}
          size="lg"
          className="px-12 py-6 text-lg font-medium"
        >
          Get Started
        </Button>

        <div className="pt-12 border-t border-border">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="space-y-2">
                <div className="text-4xl font-light">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
