import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="relative min-h-screen">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 -z-10"></div>
          {/* Decorative elements */}
          <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-20">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl"></div>
            <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-pink-500/5 rounded-full blur-3xl"></div>
            <div className="absolute top-1/3 right-1/3 w-72 h-72 bg-blue-500/5 rounded-full blur-3xl"></div>
          </div>

          {children}
        </div>
      </body>
    </html>
  );
}