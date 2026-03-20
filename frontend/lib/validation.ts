export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(email: string): string | null {
  if (!email.trim()) return 'Email is required';
  if (!EMAIL_REGEX.test(email)) return 'Please enter a valid email address';
  return null;
}

export function validatePassword(password: string): string | null {
  if (!password) return 'Password is required';
  if (password.length < 6) return 'Password must be at least 6 characters';
  if (password.length > 128) return 'Password must be less than 128 characters';
  return null;
}

export function validateName(name: string): string | null {
  if (!name.trim()) return 'Name is required';
  if (name.trim().length < 2) return 'Name must be at least 2 characters';
  if (name.trim().length > 100) return 'Name must be less than 100 characters';
  return null;
}

export function validatePasswordMatch(password: string, confirmPassword: string): string | null {
  if (password !== confirmPassword) return 'Passwords do not match';
  return null;
}

export function validateRecipeText(text: string): string | null {
  if (!text.trim()) return 'Recipe text is required';
  if (text.trim().length < 3) return 'Recipe text is too short';
  if (text.length > 15000) return 'Recipe text must be less than 15,000 characters';
  return null;
}

export function validateBarcode(barcode: string): string | null {
  if (!barcode.trim()) return 'Barcode is required';
  if (!/^\d{8,14}$/.test(barcode.trim())) return 'Barcode must be 8-14 digits';
  return null;
}
