import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";
import { ErrorBoundaryWrapper } from "@/components/ErrorBoundaryWrapper";

export const metadata: Metadata = {
  title: "MealAdapt - One kitchen. Many needs.",
  description: "AI-powered recipe adaptation for family dietary needs",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <ErrorBoundaryWrapper>
          <AuthProvider>
            <div className="max-w-2xl mx-auto px-4 py-8">
              {children}
            </div>
          </AuthProvider>
        </ErrorBoundaryWrapper>
      </body>
    </html>
  );
}
