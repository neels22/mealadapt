'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Camera, Upload, Loader2, X, Barcode, Image, AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import { api } from '@/lib/api';
import { ScanResult, BarcodeProduct, BarcodeAnalysisResponse, FamilyProfile } from '@/lib/types';
import ScanResultDisplay from '@/components/ScanResultDisplay';

type ScanMode = 'label' | 'barcode';

export default function ScanPage() {
  const [mode, setMode] = useState<ScanMode>('label');
  
  // Label scanning state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [labelResult, setLabelResult] = useState<ScanResult | null>(null);
  
  // Barcode scanning state
  const [barcodeInput, setBarcodeInput] = useState('');
  const [barcodeProduct, setBarcodeProduct] = useState<BarcodeProduct | null>(null);
  const [barcodeAnalysis, setBarcodeAnalysis] = useState<BarcodeAnalysisResponse | null>(null);
  const [familyProfile, setFamilyProfile] = useState<FamilyProfile | null>(null);
  
  // Shared state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadFamilyProfile();
  }, []);

  const loadFamilyProfile = async () => {
    try {
      const profile = await api.getFamilyProfile();
      setFamilyProfile(profile);
    } catch (err) {
      console.error('Failed to load family profile:', err);
    }
  };

  // Label scanning handlers
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setLabelResult(null);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setLabelResult(null);
      setError(null);
    }
  };

  const handleAnalyzeLabel = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const scanResult = await api.scanIngredientLabel(selectedFile);
      setLabelResult(scanResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze image');
    } finally {
      setLoading(false);
    }
  };

  const clearLabelSelection = () => {
    setSelectedFile(null);
    setPreview(null);
    setLabelResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Barcode scanning handlers
  const handleLookupBarcode = async () => {
    if (!barcodeInput.trim()) return;

    setLoading(true);
    setError(null);
    setBarcodeProduct(null);
    setBarcodeAnalysis(null);

    try {
      const product = await api.lookupBarcode(barcodeInput.trim());
      setBarcodeProduct(product);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Product not found');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeBarcode = async () => {
    if (!barcodeProduct || !familyProfile) return;

    setLoading(true);
    setError(null);

    try {
      const analysis = await api.analyzeBarcode(barcodeProduct.barcode, familyProfile);
      setBarcodeAnalysis(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze product');
    } finally {
      setLoading(false);
    }
  };

  const clearBarcode = () => {
    setBarcodeInput('');
    setBarcodeProduct(null);
    setBarcodeAnalysis(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link 
        href="/" 
        className="inline-flex items-center gap-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Home
      </Link>

      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Scan Products</h1>
        <p className="text-[var(--text-secondary)]">
          Check if food products are safe for your family
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="flex gap-2 p-1 bg-gray-100 rounded-full">
        <button
          onClick={() => setMode('label')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-full font-medium transition-colors ${
            mode === 'label'
              ? 'bg-white shadow-sm text-[var(--text-primary)]'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          <Image className="w-4 h-4" />
          Scan Label
        </button>
        <button
          onClick={() => setMode('barcode')}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-full font-medium transition-colors ${
            mode === 'barcode'
              ? 'bg-white shadow-sm text-[var(--text-primary)]'
              : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
          }`}
        >
          <Barcode className="w-4 h-4" />
          Scan Barcode
        </button>
      </div>

      {/* Label Scanning Mode */}
      {mode === 'label' && (
        <>
          <div className="card">
            {!preview ? (
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-[var(--accent-green)] transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <div className="flex flex-col items-center gap-4">
                  <div className="flex gap-4">
                    <div className="w-16 h-16 bg-[var(--accent-green)] rounded-full flex items-center justify-center">
                      <Camera className="w-8 h-8 text-[var(--text-primary)]" />
                    </div>
                    <div className="w-16 h-16 bg-[var(--accent-blue)] rounded-full flex items-center justify-center">
                      <Upload className="w-8 h-8 text-[var(--text-primary)]" />
                    </div>
                  </div>
                  <div>
                    <p className="font-medium text-lg">Tap to take a photo or upload</p>
                    <p className="text-sm text-[var(--text-secondary)] mt-1">
                      Point your camera at the ingredients list
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={preview}
                    alt="Selected ingredient label"
                    className="w-full rounded-xl max-h-64 object-contain bg-gray-100"
                  />
                  <button
                    onClick={clearLabelSelection}
                    className="absolute top-2 right-2 p-2 bg-white rounded-full shadow-md hover:bg-gray-100"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <button
                  onClick={handleAnalyzeLabel}
                  disabled={loading}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>🔍 Check for My Family</>
                  )}
                </button>
              </div>
            )}

            {error && mode === 'label' && (
              <p className="mt-4 text-sm text-red-600 text-center">{error}</p>
            )}
          </div>

          {labelResult && <ScanResultDisplay result={labelResult} />}
        </>
      )}

      {/* Barcode Scanning Mode */}
      {mode === 'barcode' && (
        <>
          <div className="card">
            <label className="block text-sm font-medium mb-2">
              Enter Barcode Number
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={barcodeInput}
                onChange={(e) => setBarcodeInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleLookupBarcode();
                  }
                }}
                placeholder="e.g., 5000159407236"
                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--accent-green)]"
              />
              <button
                onClick={handleLookupBarcode}
                disabled={loading || !barcodeInput.trim()}
                className="btn-primary px-6 disabled:opacity-50"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Look Up'}
              </button>
            </div>
            <p className="text-xs text-[var(--text-secondary)] mt-2">
              Enter the barcode number found on the product packaging
            </p>

            {error && mode === 'barcode' && (
              <p className="mt-4 text-sm text-red-600 text-center">{error}</p>
            )}
          </div>

          {/* Product Info Display */}
          {barcodeProduct && (
            <div className="card space-y-4">
              <div className="flex items-start gap-4">
                {barcodeProduct.image_url && (
                  <img
                    src={barcodeProduct.image_url}
                    alt={barcodeProduct.name}
                    className="w-24 h-24 rounded-lg object-cover bg-gray-100"
                  />
                )}
                <div className="flex-1">
                  <h3 className="text-xl font-bold">{barcodeProduct.name}</h3>
                  <p className="text-[var(--text-secondary)]">{barcodeProduct.brand}</p>
                  {barcodeProduct.quantity && (
                    <p className="text-sm text-[var(--text-secondary)]">{barcodeProduct.quantity}</p>
                  )}
                  {barcodeProduct.nutriscore && (
                    <div className={`inline-block mt-2 px-2 py-1 rounded text-xs font-bold uppercase ${
                      barcodeProduct.nutriscore === 'a' ? 'bg-green-100 text-green-700' :
                      barcodeProduct.nutriscore === 'b' ? 'bg-lime-100 text-lime-700' :
                      barcodeProduct.nutriscore === 'c' ? 'bg-yellow-100 text-yellow-700' :
                      barcodeProduct.nutriscore === 'd' ? 'bg-orange-100 text-orange-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      Nutri-Score {barcodeProduct.nutriscore.toUpperCase()}
                    </div>
                  )}
                </div>
                <button
                  onClick={clearBarcode}
                  className="p-2 rounded-full hover:bg-gray-100"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              {/* Ingredients */}
              {barcodeProduct.ingredients_text && (
                <div>
                  <h4 className="font-semibold mb-2">Ingredients</h4>
                  <p className="text-sm text-[var(--text-secondary)] bg-gray-50 p-3 rounded-lg">
                    {barcodeProduct.ingredients_text}
                  </p>
                </div>
              )}

              {/* Allergens */}
              {barcodeProduct.allergens.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Allergens</h4>
                  <div className="flex flex-wrap gap-2">
                    {barcodeProduct.allergens.map((allergen, i) => (
                      <span key={i} className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-sm">
                        {allergen.replace('en:', '')}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Nutrition */}
              {barcodeProduct.nutrition.energy_kcal && (
                <div>
                  <h4 className="font-semibold mb-2">Nutrition (per 100g)</h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {barcodeProduct.nutrition.energy_kcal && (
                      <div className="bg-gray-50 p-2 rounded-lg text-center">
                        <div className="text-lg font-bold">{Math.round(barcodeProduct.nutrition.energy_kcal)}</div>
                        <div className="text-xs text-[var(--text-secondary)]">kcal</div>
                      </div>
                    )}
                    {barcodeProduct.nutrition.proteins && (
                      <div className="bg-gray-50 p-2 rounded-lg text-center">
                        <div className="text-lg font-bold">{barcodeProduct.nutrition.proteins.toFixed(1)}g</div>
                        <div className="text-xs text-[var(--text-secondary)]">Protein</div>
                      </div>
                    )}
                    {barcodeProduct.nutrition.carbohydrates && (
                      <div className="bg-gray-50 p-2 rounded-lg text-center">
                        <div className="text-lg font-bold">{barcodeProduct.nutrition.carbohydrates.toFixed(1)}g</div>
                        <div className="text-xs text-[var(--text-secondary)]">Carbs</div>
                      </div>
                    )}
                    {barcodeProduct.nutrition.fat && (
                      <div className="bg-gray-50 p-2 rounded-lg text-center">
                        <div className="text-lg font-bold">{barcodeProduct.nutrition.fat.toFixed(1)}g</div>
                        <div className="text-xs text-[var(--text-secondary)]">Fat</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Analyze Button */}
              {!barcodeAnalysis && (
                <button
                  onClick={handleAnalyzeBarcode}
                  disabled={loading || !familyProfile?.members.length}
                  className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>🔍 Check for My Family</>
                  )}
                </button>
              )}

              {!familyProfile?.members.length && (
                <p className="text-sm text-[var(--accent-red)] text-center">
                  Add family members first to analyze products
                </p>
              )}
            </div>
          )}

          {/* Analysis Results */}
          {barcodeAnalysis && (
            <div className="card space-y-4">
              <div className="flex items-center gap-3">
                {barcodeAnalysis.overall_safety === 'safe' ? (
                  <CheckCircle2 className="w-8 h-8 text-green-500" />
                ) : barcodeAnalysis.overall_safety === 'caution' ? (
                  <AlertTriangle className="w-8 h-8 text-yellow-500" />
                ) : (
                  <XCircle className="w-8 h-8 text-red-500" />
                )}
                <div>
                  <h3 className="text-xl font-bold">
                    {barcodeAnalysis.overall_safety === 'safe' ? 'Safe for Family' :
                     barcodeAnalysis.overall_safety === 'caution' ? 'Use with Caution' :
                     'Not Recommended'}
                  </h3>
                </div>
              </div>

              {/* Concerns */}
              {barcodeAnalysis.concerns.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Concerns</h4>
                  <div className="space-y-2">
                    {barcodeAnalysis.concerns.map((concern, i) => (
                      <div 
                        key={i} 
                        className={`p-3 rounded-lg ${
                          concern.severity === 'high' ? 'bg-red-50 border border-red-200' :
                          concern.severity === 'medium' ? 'bg-yellow-50 border border-yellow-200' :
                          'bg-orange-50 border border-orange-200'
                        }`}
                      >
                        <div className="font-medium">{concern.ingredient}</div>
                        <div className="text-sm text-[var(--text-secondary)]">{concern.reason}</div>
                        <div className="text-xs mt-1">
                          Affects: {concern.affected_members.join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Safe Ingredients */}
              {barcodeAnalysis.safe_for_all.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-2">Safe for Everyone</h4>
                  <div className="flex flex-wrap gap-2">
                    {barcodeAnalysis.safe_for_all.map((item, i) => (
                      <span key={i} className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {barcodeAnalysis.recommendations.length > 0 && (
                <div className="bg-[var(--accent-yellow)]/30 p-4 rounded-xl">
                  <h4 className="font-semibold mb-2">💡 Recommendations</h4>
                  <ul className="text-sm space-y-1">
                    {barcodeAnalysis.recommendations.map((rec, i) => (
                      <li key={i}>• {rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}

      {/* Tips */}
      <div className="card bg-[var(--accent-yellow)]/30">
        <h3 className="font-semibold mb-2">
          {mode === 'label' ? '📸 Tips for Best Results' : '🔢 Barcode Tips'}
        </h3>
        <ul className="text-sm space-y-1 text-[var(--text-secondary)]">
          {mode === 'label' ? (
            <>
              <li>• Ensure good lighting on the ingredient label</li>
              <li>• Keep the text in focus and readable</li>
              <li>• Include the full ingredients list in frame</li>
              <li>• Avoid glare and shadows</li>
            </>
          ) : (
            <>
              <li>• Find the barcode number under the barcode lines</li>
              <li>• Common formats: EAN-13 (13 digits), UPC-A (12 digits)</li>
              <li>• Product data comes from Open Food Facts database</li>
              <li>• Some products may not be in the database yet</li>
            </>
          )}
        </ul>
      </div>

      {/* Footer */}
      <p className="text-center text-xs text-[var(--text-secondary)]">
        ✨ Powered by Google Gemini AI & Open Food Facts
      </p>
    </div>
  );
}
