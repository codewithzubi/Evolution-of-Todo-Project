import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Phase II Todo - Never forget a task again",
  description: "Simple. Powerful. Yours. Organize your tasks and amplify your productivity with our intuitive todo application.",
  keywords: ["todo", "task management", "productivity", "organize tasks"],
  authors: [{ name: "Phase II Todo" }],
  openGraph: {
    title: "Phase II Todo - Never forget a task again",
    description: "Simple. Powerful. Yours. Organize your tasks and amplify your productivity.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Phase II Todo - Never forget a task again",
    description: "Simple. Powerful. Yours. Organize your tasks and amplify your productivity.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            richColors
            toastOptions={{
              style: {
                background: 'rgb(31, 41, 55)',
                border: '1px solid rgb(55, 65, 81)',
                color: 'rgb(243, 244, 246)',
              },
              className: 'backdrop-blur-sm',
            }}
          />
        </Providers>
      </body>
    </html>
  );
}
