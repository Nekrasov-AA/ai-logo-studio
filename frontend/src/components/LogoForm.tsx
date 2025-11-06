import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { FormData } from '@/types/logo';

interface LogoFormProps {
  onBack: () => void;
  onSubmit: (data: FormData) => void;
}

const industries = [
  'tech', 'healthcare', 'finance', 'food', 
  'retail', 'consulting', 'creative', 'other'
];

const styles = [
  'modern', 'minimalist', 'vintage', 
  'bold', 'elegant', 'playful'
];

const colors = [
  { name: 'blue', class: 'bg-accent-blue' },
  { name: 'green', class: 'bg-accent-green' },
  { name: 'purple', class: 'bg-accent-purple' },
  { name: 'red', class: 'bg-accent-red' },
  { name: 'orange', class: 'bg-accent-orange' },
  { name: 'pink', class: 'bg-accent-pink' }
];

const LogoForm: React.FC<LogoFormProps> = ({ onBack, onSubmit }) => {
  const [formData, setFormData] = useState<FormData>({
    businessName: '',
    industry: '',
    style: '',
    colors: [],
    description: ''
  });

  const handleColorToggle = (colorName: string) => {
    setFormData(prev => {
      const newColors = prev.colors.includes(colorName)
        ? prev.colors.filter(c => c !== colorName)
        : prev.colors.length < 3
        ? [...prev.colors, colorName]
        : prev.colors;
      return { ...prev, colors: newColors };
    });
  };

  const isFormValid = formData.businessName.trim() && formData.industry && 
                       formData.style && formData.colors.length > 0;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isFormValid) {
      onSubmit(formData);
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] py-12 px-6">
      <div className="max-w-2xl mx-auto space-y-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="text-sm">Back</span>
        </button>

        <div className="space-y-2">
          <h2 className="text-4xl font-light">Tell us about your business</h2>
          <p className="text-muted-foreground">
            Help us understand your brand to generate the perfect logo
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Business Name */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Business Name *</label>
            <input
              type="text"
              value={formData.businessName}
              onChange={(e) => setFormData({ ...formData, businessName: e.target.value })}
              placeholder="Enter your business name"
              className="w-full bg-transparent border-b border-input py-3 text-2xl font-light focus:outline-none focus:border-foreground transition-colors"
            />
          </div>

          {/* Industry */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Industry *</label>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              {industries.map((industry) => (
                <button
                  key={industry}
                  type="button"
                  onClick={() => setFormData({ ...formData, industry })}
                  className={`px-4 py-3 text-sm capitalize border rounded-lg transition-all ${
                    formData.industry === industry
                      ? 'bg-foreground text-background border-foreground'
                      : 'bg-background text-foreground border-border hover:border-foreground'
                  }`}
                >
                  {industry}
                </button>
              ))}
            </div>
          </div>

          {/* Style */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Style *</label>
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
              {styles.map((style) => (
                <button
                  key={style}
                  type="button"
                  onClick={() => setFormData({ ...formData, style })}
                  className={`px-4 py-3 text-sm capitalize border rounded-lg transition-all ${
                    formData.style === style
                      ? 'bg-foreground text-background border-foreground'
                      : 'bg-background text-foreground border-border hover:border-foreground'
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          {/* Colors */}
          <div className="space-y-3">
            <label className="text-sm font-medium">
              Color Preferences * (Select up to 3)
            </label>
            <div className="flex gap-4">
              {colors.map((color) => (
                <button
                  key={color.name}
                  type="button"
                  onClick={() => handleColorToggle(color.name)}
                  className={`w-12 h-12 rounded-full ${color.class} transition-all ${
                    formData.colors.includes(color.name)
                      ? 'ring-4 ring-foreground ring-offset-2 ring-offset-background'
                      : 'hover:ring-2 ring-muted-foreground ring-offset-2 ring-offset-background'
                  }`}
                  title={color.name}
                />
              ))}
            </div>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <label className="text-sm font-medium">
              Additional Details (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Tell us more about your brand vision..."
              rows={4}
              className="w-full bg-transparent border-b border-input py-3 font-light focus:outline-none focus:border-foreground transition-colors resize-none"
            />
          </div>

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={!isFormValid}
            className="w-full py-6 text-base font-medium"
          >
            Generate Logos
          </Button>
        </form>
      </div>
    </div>
  );
};

export default LogoForm;
