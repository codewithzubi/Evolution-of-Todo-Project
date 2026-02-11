/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://zubairahmed0077-webapp-todo-phase-ii.hf.space/api/:path*',
      },
    ];
  },
};

export default nextConfig;








// /** @type {import('next').NextConfig} */
// const nextConfig = {
//   images: {
//     remotePatterns: [],
//   },
// };

// export default nextConfig;
