'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search, Camera, Cookie, BookOpen, ShoppingCart, CalendarDays } from 'lucide-react';
import FamilyProfile from '@/components/FamilyProfile';
import UserMenu from '@/components/UserMenu';
import { api } from '@/lib/api';
import { FamilyProfile as FamilyProfileType } from '@/lib/types';
import { useAuth } from '@/components/AuthProvider';

export default function Home() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<FamilyProfileType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading) {
      loadProfile();
    }
  }, [authLoading, isAuthenticated]);

  const loadProfile = async () => {
    try {
      const data = await api.getFamilyProfile();
      setProfile(data);
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Failed to load profile:', error);
      }
      setProfile({ members: [] });
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = () => {
    loadProfile();
  };

  return (
    <div className="space-y-8">
      {/* Header with User Menu */}
      <div className="flex items-center justify-between">
        <div></div>
        <UserMenu />
      </div>

      {/* Title */}
      <div className="text-center py-4">
        <h1 className="text-5xl font-bold text-[var(--text-primary)] mb-2">
          MealAdapt
        </h1>
        <p className="text-[var(--text-secondary)] text-lg">
          One kitchen. Many needs.
        </p>
      </div>

      {/* Scan Ingredient Label Card */}
      <Link href="/scan">
        <div className="card hover:shadow-md transition-shadow cursor-pointer">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-semibold mb-1">
                Scan Ingredient Label
              </h3>
              <p className="text-[var(--text-secondary)] text-sm">
                Check if packaged food is safe for everyone
              </p>
            </div>
            <Camera className="w-6 h-6 text-[var(--text-secondary)]" />
          </div>
        </div>
      </Link>

      {/* Action Cards Grid */}
      <div className="grid grid-cols-2 gap-6 mt-4">
        <Link href="/adapt">
          <div className="card text-center hover:shadow-md transition-shadow cursor-pointer h-32 flex flex-col items-center justify-center">
            <Search className="w-8 h-8 mb-2 text-[var(--text-primary)]" />
            <h3 className="font-semibold">Adapt Recipe</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-1">Check any dish</p>
          </div>
        </Link>

        <Link href="/recipes">
          <div className="card text-center hover:shadow-md transition-shadow cursor-pointer h-32 flex flex-col items-center justify-center">
            <BookOpen className="w-8 h-8 mb-2 text-[var(--text-primary)]" />
            <h3 className="font-semibold">My Recipes</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-1">Saved collection</p>
          </div>
        </Link>

        <Link href="/pantry">
          <div className="card text-center hover:shadow-md transition-shadow cursor-pointer h-32 flex flex-col items-center justify-center">
            <Cookie className="w-8 h-8 mb-2 text-[var(--text-primary)]" />
            <h3 className="font-semibold">My Pantry</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-1">Get recipe ideas</p>
          </div>
        </Link>

        <Link href="/shopping">
          <div className="card text-center hover:shadow-md transition-shadow cursor-pointer h-32 flex flex-col items-center justify-center">
            <ShoppingCart className="w-8 h-8 mb-2 text-[var(--text-primary)]" />
            <h3 className="font-semibold">Shopping</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-1">Grocery lists</p>
          </div>
        </Link>

        <Link href="/planner">
          <div className="card text-center hover:shadow-md transition-shadow cursor-pointer h-32 flex flex-col items-center justify-center">
            <CalendarDays className="w-8 h-8 mb-2 text-[var(--text-primary)]" />
            <h3 className="font-semibold">Meal Planner</h3>
            <p className="text-xs text-[var(--text-secondary)] mt-1">Plan your week</p>
          </div>
        </Link>
      </div>

      {/* Family Profile */}
      {loading || authLoading ? (
        <div className="card">
          <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      ) : (
        profile && (
          <FamilyProfile 
            profile={profile} 
            onUpdate={handleProfileUpdate}
          />
        )
      )}

      {/* Safety Filter Badges */}
      <div className="flex gap-3 justify-center flex-wrap">
        <div className="badge badge-diabetes">✓ Diabetic-Safe</div>
        <div className="badge badge-celiac">🧪 Low-Sodium</div>
        <div className="badge badge-baby">☀️ Baby-Safe</div>
      </div>

      {/* Footer */}
      <p className="text-center text-xs text-[var(--text-secondary)]">
        Powered by Google Gemini AI
      </p>
    </div>
  );
}
