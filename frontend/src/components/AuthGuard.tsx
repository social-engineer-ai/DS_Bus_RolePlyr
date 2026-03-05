'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { api } from '@/lib/api';

const PUBLIC_PATHS = ['/login', '/signup'];

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const isPublic = PUBLIC_PATHS.includes(pathname);
    const isAuthenticated = api.isAuthenticated();

    if (!isPublic && !isAuthenticated) {
      router.replace('/login');
    } else if (isPublic && isAuthenticated) {
      router.replace('/');
    } else {
      setChecked(true);
    }
  }, [pathname, router]);

  if (!checked) {
    return null;
  }

  return <>{children}</>;
}
