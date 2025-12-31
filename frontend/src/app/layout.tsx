import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'StakeholderSim',
  description: 'AI-powered role-play training for stakeholder communication',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
