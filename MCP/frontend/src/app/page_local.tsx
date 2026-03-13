/**
 * Local mode landing page - redirects directly to dashboard
 */
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LocalHomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboard immediately in local mode
    router.push('/dashboard');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Udyami AI - Local Mode</h1>
        <p className="text-gray-600">Redirecting to dashboard...</p>
      </div>
    </div>
  );
}
