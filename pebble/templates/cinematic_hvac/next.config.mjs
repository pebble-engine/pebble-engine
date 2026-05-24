/** @type {import('next').NextConfig} */
const nextConfig = {
  allowedDevOrigins: ['127.0.0.1', 'localhost', '*.local'],
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.unsplash.com' },
      { protocol: 'https', hostname: 'images.pexels.com' },
      { protocol: 'https', hostname: 'videos.pexels.com' },
      { protocol: 'https', hostname: 'pixabay.com' },
    ],
  },
};

export default nextConfig;
