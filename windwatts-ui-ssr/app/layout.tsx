import Providers from "./providers";
import Header from "../src/components/Header";

export const metadata = {
  title: "Windwatts UI (SSR)",
  description: "Server-side rendered Windwatts UI"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <meta name="emotion-insertion-point" content="" />
      </head>
      <body>
        <Providers>
          <Header />
          {children}
        </Providers>
      </body>
    </html>
  );
}
