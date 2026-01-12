'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { useAuth } from '@/components/AuthProvider';

export default function UserMenu() {
  const { user, isAuthenticated, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
    router.push('/');
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center gap-3">
        <Link
          href="/login"
          className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] font-medium transition-colors"
        >
          Sign In
        </Link>
        <Link
          href="/signup"
          className="bg-[var(--accent-green)] hover:bg-[#98C5AA] text-[var(--text-primary)] font-medium px-4 py-2 rounded-full transition-colors"
        >
          Sign Up
        </Link>
      </div>
    );
  }

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 bg-white hover:bg-gray-50 px-3 py-2 rounded-full border border-gray-200 transition-colors"
      >
        <div className="w-8 h-8 bg-[var(--accent-green)] rounded-full flex items-center justify-center">
          <span className="text-sm font-semibold text-[var(--text-primary)]">
            {user?.name?.charAt(0).toUpperCase() || 'U'}
          </span>
        </div>
        <span className="text-sm font-medium text-[var(--text-primary)] max-w-[100px] truncate hidden sm:block">
          {user?.name || 'User'}
        </span>
        <ChevronDown className={`w-4 h-4 text-[var(--text-secondary)] transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-50">
          <div className="px-4 py-3 border-b border-gray-100">
            <p className="text-sm font-medium text-[var(--text-primary)] truncate">{user?.name}</p>
            <p className="text-xs text-[var(--text-secondary)] truncate">{user?.email}</p>
          </div>
          
          <Link
            href="/profile"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
          >
            <User className="w-4 h-4 text-[var(--text-secondary)]" />
            <span className="text-sm text-[var(--text-primary)]">Profile</span>
          </Link>
          
          <Link
            href="/profile"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
          >
            <Settings className="w-4 h-4 text-[var(--text-secondary)]" />
            <span className="text-sm text-[var(--text-primary)]">Settings</span>
          </Link>
          
          <div className="border-t border-gray-100 mt-1 pt-1">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-4 py-3 hover:bg-red-50 transition-colors w-full text-left"
            >
              <LogOut className="w-4 h-4 text-red-500" />
              <span className="text-sm text-red-500">Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
