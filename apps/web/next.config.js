/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: {
      allowedOrigins: ["http://localhost:3000", "https://misfits.westfam.media"],
    },
  },
};

export default nextConfig;
