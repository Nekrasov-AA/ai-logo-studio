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

const COLOR_OPTIONS = [
  { label: 'Orange', value: '#ea580c' },
  { label: 'Blue',   value: '#2563eb' },
  { label: 'Green',  value: '#16a34a' },
  { label: 'Purple', value: '#9333ea' },
  { label: 'Red',    value: '#dc2626' },
  { label: 'Slate',  value: '#475569' },
];

const LogoForm: React.FC<LogoFormProps> = ({ onBack, onSubmit }) => {
  const [formData, setFormData] = useState<FormData>({
    businessName: '',
    industry: '',
    style: '',
    colors: ['#ea580c'],
    description: ''
  });

  const isFormValid = formData.businessName.trim() && formData.industry && formData.style;

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

          {/* Color */}
          <div className="space-y-3">
            <label className="text-sm font-medium">Brand Color *</label>
            <div className="flex gap-3">
              {COLOR_OPTIONS.map((color) => {
                const selected = formData.colors[0] === color.value;
                return (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, colors: [color.value] })}
                    className={`relative w-8 h-8 rounded-full transition-all focus:outline-none ${
                      selected
                        ? 'ring-2 ring-foreground ring-offset-2 ring-offset-background'
                        : 'hover:ring-2 hover:ring-muted-foreground hover:ring-offset-2 hover:ring-offset-background'
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.label}
                  >
                    {selected && (
                      <svg
                        className="absolute inset-0 m-auto w-4 h-4"
                        viewBox="0 0 16 16"
                        fill="none"
                        stroke="white"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <polyline points="3,8 6.5,11.5 13,4.5" />
                      </svg>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Additional Details — hidden until LLM integration (Phase 5) */}
          {false && (
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
          )}

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
